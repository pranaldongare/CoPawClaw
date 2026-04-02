"""
Unified structured LLM invocation with retries and fallbacks.

Fallback chain: GPU (vLLM/Ollama via OpenAI-compatible API) → Gemini → OpenAI.
Removes LangChain dependency — uses direct httpx/openai calls and Pydantic v2
schema generation instead of PydanticOutputParser.
"""

import asyncio
import contextvars
import itertools
import json
import logging
import os
import time
import traceback
from datetime import datetime, timezone
from typing import Type

from google import genai
from openai import AsyncOpenAI
from pydantic import BaseModel

from enterprise_skills_lib.config import settings
from enterprise_skills_lib.constants import FALLBACK_GEMINI_MODEL, FALLBACK_OPENAI_MODEL, SWITCHES
from enterprise_skills_lib.llm.output_sanitizer import parse_llm_json, sanitize_llm_json, _strip_schema_metadata

logger = logging.getLogger("llm.client")

# Directory for logging parse failures
_PARSE_ERRORS_DIR = "DEBUG/parse_errors"
os.makedirs(_PARSE_ERRORS_DIR, exist_ok=True)


def _log_parse_failure(
    source: str,
    attempt: int,
    raw_output: str,
    error: str,
    schema_name: str,
    prompt_snippet: str = "",
):
    """Log a parse failure to a JSONL file for later analysis."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "attempt": attempt,
        "schema": schema_name,
        "error": error,
        "raw_output": raw_output[:5000],
        "prompt_tail": prompt_snippet[-500:] if prompt_snippet else "",
    }
    try:
        log_path = os.path.join(_PARSE_ERRORS_DIR, "failures.jsonl")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _get_format_instructions(schema: Type[BaseModel]) -> str:
    """
    Generate format instructions from a Pydantic v2 model's JSON schema.
    Replaces LangChain's PydanticOutputParser.get_format_instructions().
    """
    json_schema = schema.model_json_schema()
    schema_str = json.dumps(json_schema, indent=2)
    return (
        "The output should be formatted as a JSON instance that conforms to the "
        "JSON schema below.\n\n"
        f"```json\n{schema_str}\n```"
    )


# ── Rate limiter for INTERNAL API ─────────────────────────────────


class _RateLimiter:
    """Async sliding-window rate limiter."""

    def __init__(self, max_calls: int, window_seconds: float):
        self.max_calls = max_calls
        self.window = window_seconds
        self._timestamps: list[float] = []
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.time()
            self._timestamps = [t for t in self._timestamps if now - t < self.window]
            if len(self._timestamps) >= self.max_calls:
                wait_time = self.window - (now - self._timestamps[0])
                if wait_time > 0:
                    logger.info(
                        f"[Rate limit] {self.max_calls} calls in last "
                        f"{self.window:.0f}s, waiting {wait_time:.1f}s..."
                    )
                    await asyncio.sleep(wait_time)
                    now = time.time()
                    self._timestamps = [
                        t for t in self._timestamps if now - t < self.window
                    ]
            self._timestamps.append(time.time())


_internal_rate_limiter = _RateLimiter(max_calls=3, window_seconds=60.0)

# ── Sticky fallback: once GPU fails, skip it for subsequent calls
#    in the same async context. ──────────────────────────────────

_skip_gpu: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "_skip_gpu", default=False
)

# Cache AsyncOpenAI clients for GPU endpoints (vLLM/Ollama)
_gpu_client_cache: dict[tuple[str, int], AsyncOpenAI] = {}


def _get_gpu_client(port: int) -> AsyncOpenAI:
    """Return a cached AsyncOpenAI client pointing at a local GPU server."""
    base_url = f"http://localhost:{port}/v1"
    key = ("gpu", port)
    if key not in _gpu_client_cache:
        _gpu_client_cache[key] = AsyncOpenAI(
            base_url=base_url,
            api_key="not-needed",
            timeout=120.0,
        )
    return _gpu_client_cache[key]


# Gemini API key rotation
API_KEYS = [
    settings.API_KEY_1,
    settings.API_KEY_2,
    settings.API_KEY_3,
    settings.API_KEY_4,
    settings.API_KEY_5,
    settings.API_KEY_6,
]

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API)
MAX_RETRIES = 4

# Thread-safe API key cycling
_api_key_cycle = itertools.cycle(API_KEYS)
_api_key_lock = asyncio.Lock()


async def _next_api_key():
    """Get the next API key in round-robin fashion."""
    async with _api_key_lock:
        return next(_api_key_cycle)


def _check_empty_lists(result, response_schema) -> None:
    """
    Reject outputs where ALL required list fields are empty.
    Triggers a self-correction retry instead of accepting useless data.
    """
    from pydantic.fields import PydanticUndefined

    model_fields = getattr(response_schema, "model_fields", {})
    required_list_fields = []
    for name, info in model_fields.items():
        annotation = info.annotation
        origin = getattr(annotation, "__origin__", None)
        if origin is not list:
            continue
        if info.default is not PydanticUndefined or info.default_factory is not None:
            continue
        required_list_fields.append(name)

    if not required_list_fields:
        return

    all_empty = all(
        len(getattr(result, f, None) or []) == 0 for f in required_list_fields
    )
    if all_empty:
        raise ValueError(
            f"All required list fields are empty ({', '.join(required_list_fields)}). "
            "Expected actual data items, not empty arrays."
        )


def _try_parse(raw_output: str, response_schema: Type[BaseModel]):
    """
    Attempt to parse LLM output with sanitization and repair fallbacks.

    Strategy:
    1. Sanitize + json.loads + strip schema metadata + model_validate
    2. parse_llm_json() with json_repair + model_validate

    Post-validation: reject outputs with all-empty list fields.
    """
    cleaned = sanitize_llm_json(raw_output)

    # Strategy 1: Direct parse after sanitization
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            parsed = _strip_schema_metadata(parsed, response_schema)
        result = response_schema.model_validate(parsed)
        _check_empty_lists(result, response_schema)
        return result
    except Exception:
        pass

    # Strategy 2: Full parse_llm_json with json_repair
    result = parse_llm_json(raw_output, response_schema)
    _check_empty_lists(result, response_schema)
    return result


def _serialize_prompt_messages(messages: list) -> str:
    """
    Convert a list of role/parts message dicts into a readable prompt string.
    """
    parts = []
    for msg in messages:
        role = msg.get("role", "system").upper()
        content = msg.get("parts", "")
        parts.append(f"[{role}]\n{content}")
    return "\n\n".join(parts)


def _messages_to_openai_format(messages: list) -> list[dict]:
    """
    Convert role/parts message dicts to OpenAI chat format.
    Used for GPU (vLLM/Ollama) and OpenAI API calls.
    """
    result = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("parts", "")
        if role not in ("system", "user", "assistant"):
            role = "user"
        result.append({"role": role, "content": content})
    return result


async def invoke_llm(
    gpu_model: str,
    response_schema: Type[BaseModel],
    contents,
    port: int = 11434,
    remove_thinking: bool = False,
):
    """
    Unified structured LLM invocation with retries and fallbacks:
    - GPU server (vLLM/Ollama via OpenAI-compatible API)
    - Gemini API (6-key rotation)
    - OpenAI API
    Each returns parsed structured data.
    """

    format_instructions = _get_format_instructions(response_schema)

    # Serialize contents
    if isinstance(contents, list) and contents and isinstance(contents[0], dict) and "role" in contents[0]:
        serialized = _serialize_prompt_messages(contents)
        chat_messages = _messages_to_openai_format(contents)
    else:
        serialized = str(contents)
        chat_messages = [{"role": "user", "content": serialized}]

    # Use different framing for answer-generating schemas vs extraction schemas
    is_answer_schema = hasattr(response_schema, "model_fields") and "answer" in response_schema.model_fields

    if is_answer_schema:
        prompt = f"""{serialized}

RESPONSE FORMAT — CRITICAL:
You MUST respond with a single valid JSON object matching this schema:
{format_instructions}

JSON RULES:
1. Output ONLY the JSON object — no markdown fences, no commentary, no text before or after.
2. Escape newlines as \\n and tabs as \\t within JSON string values.
3. If you use internal reasoning (e.g. <think> tags), produce the JSON AFTER the closing tag.
4. The "answer" field should contain your FULL, DETAILED response following the guidelines above. Do NOT truncate or shorten it.
5. For tables inside the answer field, use HTML <table> tags, NOT Markdown pipe tables.
6. Do NOT echo the schema definition. Never include "$defs", "$ref", "properties", "required", "title", "type":"object" or "description" as top-level keys. Only output the DATA that conforms to the schema.
"""
    else:
        prompt = f"""Extract structured data according to this model:
{format_instructions}

Input:
{serialized}

CRITICAL OUTPUT RULES:
1. Output must be valid JSON.
2. Escape newlines as \\n and tabs as \\t within JSON strings.
3. If you generate internal reasoning (e.g. inside <think> tags), you MUST produce the final JSON object AFTER the closing </think> tag.
4. Do not output any text before or after the JSON object.
5. Do NOT echo the schema definition. Never include "$defs", "$ref", "properties", "required", "title", "type":"object" or "description" as top-level keys. Only output the DATA that conforms to the schema.
6. Every list/array field must contain actual items. Do not return empty arrays unless the input data genuinely contains zero relevant items.
"""

    # ── Helper: build effective prompt with self-correction context ──
    def _build_prompt(base: str, failed_output: str | None, parse_error: str | None) -> str:
        if failed_output and parse_error:
            logger.debug("[Self-correction] Injecting previous output + error into prompt")
            return (
                f"{base}\n\n"
                "--- PREVIOUS ATTEMPT FAILED ---\n"
                "Your previous output could not be parsed. Fix the errors and output valid JSON only.\n\n"
                f"Previous output (rejected):\n{failed_output[:2000]}\n\n"
                f"Parse error:\n{parse_error}\n\n"
                "Fix the above errors and return ONLY valid JSON matching the schema."
            )
        return base

    def _build_chat_messages(base_messages: list[dict], failed_output: str | None, parse_error: str | None) -> list[dict]:
        """Build chat messages with self-correction appended."""
        if failed_output and parse_error:
            correction_msg = (
                "--- PREVIOUS ATTEMPT FAILED ---\n"
                "Your previous output could not be parsed. Fix the errors and output valid JSON only.\n\n"
                f"Previous output (rejected):\n{failed_output[:2000]}\n\n"
                f"Parse error:\n{parse_error}\n\n"
                "Fix the above errors and return ONLY valid JSON matching the schema."
            )
            return base_messages + [
                {"role": "assistant", "content": failed_output[:2000]},
                {"role": "user", "content": correction_msg},
            ]
        return base_messages

    # Inject format instructions into chat messages for GPU/OpenAI
    gpu_chat_messages = []
    if chat_messages:
        # Add format instructions to the last user message
        gpu_chat_messages = chat_messages[:-1] + [
            {
                "role": chat_messages[-1]["role"],
                "content": chat_messages[-1]["content"] + f"\n\n{format_instructions}\n\n"
                    "CRITICAL: Output ONLY valid JSON. No markdown fences, no commentary. "
                    "Do NOT echo schema definitions.",
            }
        ]

    # ── Phase 1: GPU SERVER (vLLM/Ollama via OpenAI-compatible API) ──
    last_failed_output = None
    last_parse_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        logger.info(f"=== Attempt {attempt}/{MAX_RETRIES} ===")

        if gpu_model and not _skip_gpu.get():
            llm_output = None
            try:
                logger.info(f"Trying GPU server ({gpu_model} on port {port})...")
                gpu_client = _get_gpu_client(port)
                effective_messages = _build_chat_messages(
                    gpu_chat_messages, last_failed_output, last_parse_error
                )

                s = time.time()
                response = await gpu_client.chat.completions.create(
                    model=gpu_model,
                    messages=effective_messages,
                    temperature=0.2,
                    max_tokens=16384,
                )
                llm_output = response.choices[0].message.content
                e = time.time()
                logger.info(f"Success via GPU server, LLM call took {e - s:.2f}s")

                structured = _try_parse(llm_output, response_schema)
                return structured

            except Exception as exc:
                error_str = str(exc)
                logger.error(f"GPU server failed at port {port}: {error_str}")
                if llm_output:
                    last_failed_output = llm_output
                    last_parse_error = error_str
                    _log_parse_failure(
                        source="gpu",
                        attempt=attempt,
                        raw_output=llm_output,
                        error=error_str,
                        schema_name=response_schema.__name__,
                    )
                    logger.debug(f"[Self-correction] Captured failed GPU output ({len(llm_output)} chars)")
                    continue  # Retry GPU with self-correction

        # === 2. GEMINI FALLBACK ===
        if SWITCHES.get("FALLBACK_TO_GEMINI", True):
            effective_prompt = _build_prompt(prompt, last_failed_output, last_parse_error)
            logger.info("Falling back to Gemini...")

            for _ in range(len(API_KEYS)):
                api_key = await _next_api_key()
                if not api_key:
                    continue
                client = genai.Client(api_key=api_key)
                s = time.time()
                raw_output = None
                try:
                    config = genai.types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=200000,
                        response_mime_type="text/plain",
                        safety_settings=[],
                    )

                    if remove_thinking:
                        config.thinking_config = genai.types.ThinkingConfig(
                            thinking_budget=0
                        )

                    response = await asyncio.wait_for(
                        asyncio.to_thread(
                            client.models.generate_content,
                            model=FALLBACK_GEMINI_MODEL,
                            contents=effective_prompt,
                            config=config,
                        ),
                        timeout=80,
                    )

                    try:
                        raw_output = response.text or str(response)
                    except Exception:
                        raw_output = str(response)

                    structured = _try_parse(raw_output, response_schema)
                    e = time.time()
                    logger.info(f"Success via Gemini, LLM call took {e - s:.2f}s")
                    return structured

                except asyncio.TimeoutError:
                    logger.warning("Gemini timeout — switching key...")
                except Exception as exc:
                    logger.warning(f"Gemini error: {exc}")
                    if raw_output:
                        _log_parse_failure(
                            source="gemini",
                            attempt=attempt,
                            raw_output=raw_output,
                            error=str(exc),
                            schema_name=response_schema.__name__,
                        )
                    await asyncio.sleep(0.2)

        # === 3. OPENAI FALLBACK ===
        if SWITCHES.get("FALLBACK_TO_OPENAI", True):
            effective_prompt = _build_prompt(prompt, last_failed_output, last_parse_error)
            openai_raw = None
            try:
                logger.info("Falling back to OpenAI...")
                s = time.time()
                response = await openai_client.chat.completions.create(
                    model=FALLBACK_OPENAI_MODEL,
                    messages=[{"role": "user", "content": effective_prompt}],
                    temperature=0.2,
                )

                openai_raw = response.choices[0].message.content
                structured = _try_parse(openai_raw, response_schema)
                e = time.time()
                logger.info(f"Success via OpenAI, LLM call took {e - s:.2f}s")
                return structured

            except Exception as exc:
                logger.warning(f"OpenAI fallback error: {exc}")
                if openai_raw:
                    _log_parse_failure(
                        source="openai",
                        attempt=attempt,
                        raw_output=openai_raw,
                        error=str(exc),
                        schema_name=response_schema.__name__,
                    )

        await asyncio.sleep(2)

    raise RuntimeError("All fallback attempts failed (GPU + Gemini + OpenAI).")
