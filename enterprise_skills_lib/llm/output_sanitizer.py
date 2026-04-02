"""
Centralized LLM output sanitization and JSON repair pipeline.

Handles common LLM JSON output issues:
- Markdown code fences wrapping JSON
- Unicode whitespace characters (non-breaking spaces, thin spaces, etc.)
- Preamble/postamble text around JSON
- Malformed JSON (trailing commas, single quotes, unescaped chars)
"""

import json
import re
from typing import Type, TypeVar

from pydantic import BaseModel


try:
    import json_repair
except ImportError:
    json_repair = None

T = TypeVar("T", bound=BaseModel)

# Unicode whitespace characters that have no semantic meaning in JSON
# and can cause parsing failures
_UNICODE_WHITESPACE_RE = re.compile(
    r"[\u00a0\u2009\u200a\u202f\u00ad\u2002\u2003\u2004\u2005\u2006\u2007\u2008]"
)

# Zero-width characters that should be removed entirely
_ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\ufeff\u2060\u180e]")

# Markdown code fence patterns
_CODE_FENCE_RE = re.compile(r"```(?:json|JSON)?\s*\n?(.*?)\n?\s*```", re.DOTALL)

# Thinking / reasoning tags (some models emit these even when disabled)
_THINK_TAG_RE = re.compile(r"<think>.*?</think>", re.DOTALL)
_REASONING_TAG_RE = re.compile(r"<reasoning>.*?</reasoning>", re.DOTALL)


def sanitize_llm_json(raw: str) -> str:
    """
    Pre-process raw LLM output to maximize JSON parsing success.

    Pipeline (each step is fast string/regex ops):
    1. Strip markdown code fences
    2. Replace unicode whitespace with regular spaces
    3. Remove zero-width characters
    4. Normalize newlines
    5. Extract JSON object/array from surrounding text
    """
    if not raw or not raw.strip():
        return raw

    text = raw

    # 0. Strip thinking / reasoning tags (models may emit these before JSON)
    text = _THINK_TAG_RE.sub("", text)
    text = _REASONING_TAG_RE.sub("", text)

    # 1. Strip markdown code fences (```json ... ``` or ``` ... ```)
    fence_match = _CODE_FENCE_RE.search(text)
    if fence_match:
        text = fence_match.group(1)

    # 2. Replace unicode whitespace with regular spaces
    text = _UNICODE_WHITESPACE_RE.sub(" ", text)

    # 3. Remove zero-width characters
    text = _ZERO_WIDTH_RE.sub("", text)

    # 4. Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 5. Extract JSON object/array from surrounding text
    text = text.strip()
    text = _extract_json_block(text)

    # 6. Escape control characters within strings
    text = _escape_control_chars_in_strings(text)

    return text


def _sanitize_fallback_text(raw: str) -> str:
    """Clean plain-text fallback output without forcing JSON extraction."""
    if not raw:
        return raw

    text = raw
    text = _THINK_TAG_RE.sub("", text)
    text = _REASONING_TAG_RE.sub("", text)

    fence_match = _CODE_FENCE_RE.search(text)
    if fence_match:
        text = fence_match.group(1)

    text = _UNICODE_WHITESPACE_RE.sub(" ", text)
    text = _ZERO_WIDTH_RE.sub("", text)
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def _escape_control_chars_in_strings(text: str) -> str:
    """
    Escapes control characters (newlines, tabs) only when they appear
    inside double-quoted strings, to ensure valid JSON.
    """
    result = []
    in_string = False
    i = 0
    n = len(text)

    while i < n:
        char = text[i]

        if char == '"':
            if i > 0 and text[i - 1] == "\\":
                bs_count = 0
                j = i - 1
                while j >= 0 and text[j] == "\\":
                    bs_count += 1
                    j -= 1
                if bs_count % 2 == 0:
                    in_string = not in_string
            else:
                in_string = not in_string

        if in_string:
            if char == "\n":
                result.append("\\n")
            elif char == "\t":
                result.append("\\t")
            elif char == "\r":
                pass
            else:
                result.append(char)
        else:
            result.append(char)

        i += 1

    return "".join(result)


# Known schema field names for finding the "right" JSON object
_SCHEMA_FIELD_RE = re.compile(
    r'\{\s*"(?:answer|action|sql_query|excel_request|summary|outline|sections|content'
    r'|description|reasoning|result|data|items|categories|findings|recommendations'
    r'|stop_words|nodes|edges|milestones|phases|insights|review'
    r'|articles|report_title|executive_summary|key_trends|radar_items|market_signals'
    r'|radar_item_details|report_sections'
    r'|roadmap_title|overall_vision|current_state_analysis|technology_domains'
    r'|key_technology_enablers|risks_and_mitigations|innovation_opportunities'
    r'|tabular_summary|llm_inferred_additions|phased_roadmap'
    r'|vision_and_end_goal|current_baseline|strategic_pillars'
    r'|enablers_and_dependencies|risks_and_mitigation|key_metrics_and_milestones'
    r'|future_opportunities'
    r'|requires_decomposition|hypothetical_document|verdict|themes'
    r'|file_name|values|document_title|heading|overall_score'
    r'|analysis_title|mind_map|document_summary|title'
    r'|technology_name|stopwords)"'
)


def _extract_json_block(text: str) -> str:
    """
    Extract the outermost JSON object or array from text that may contain
    preamble or postamble content.
    """
    if text.startswith("{"):
        start = 0
        open_char = "{"
        close_char = "}"
    elif text.startswith("["):
        start = 0
        open_char = "["
        close_char = "]"
    else:
        schema_match = _SCHEMA_FIELD_RE.search(text)
        if schema_match:
            start = schema_match.start()
            open_char = "{"
            close_char = "}"
        else:
            start = -1
            open_char = None
            close_char = None
            for i, ch in enumerate(text):
                if ch == "{":
                    start = i
                    open_char = "{"
                    close_char = "}"
                    break
                elif ch == "[":
                    start = i
                    open_char = "["
                    close_char = "]"
                    break

    if start == -1:
        return text

    depth = 0
    in_string = False
    escape_next = False
    end = len(text)

    for i in range(start, len(text)):
        ch = text[i]

        if escape_next:
            escape_next = False
            continue

        if ch == "\\":
            if in_string:
                escape_next = True
            continue

        if ch == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    return text[start:end]


# Keys that belong to a JSON Schema definition, not to actual data.
_SCHEMA_META_KEYS = frozenset({
    "$defs", "$ref", "$schema", "$id",
    "definitions", "properties", "required",
    "title", "type", "description", "additionalProperties",
    "allOf", "anyOf", "oneOf", "not", "enum", "const",
    "default", "examples",
})


def _strip_schema_metadata(parsed: dict, schema: type) -> dict:
    """
    Remove JSON-Schema metadata keys that the LLM erroneously echoed,
    keeping only data keys that the Pydantic model actually expects.
    """
    model_fields = set(getattr(schema, "model_fields", {}).keys())
    if not model_fields:
        return parsed

    data_keys = {k for k in parsed if k in model_fields}
    meta_keys = {k for k in parsed if k in _SCHEMA_META_KEYS and k not in model_fields}

    if not meta_keys:
        return parsed

    if data_keys:
        return {k: v for k, v in parsed.items() if k in model_fields}

    return parsed


def parse_llm_json(raw: str, schema: Type[T]) -> T:
    """
    Parse and validate LLM output against a Pydantic schema with
    multiple fallback strategies.

    Strategies (in order):
    1. Sanitize + json.loads + strip schema metadata + model_validate
    2. json_repair.loads + strip schema metadata + model_validate
    3. Raise with clear error
    """
    cleaned = sanitize_llm_json(raw)

    # Strategy 1: Standard json.loads after sanitization
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            parsed = _strip_schema_metadata(parsed, schema)
        return schema.model_validate(parsed)
    except (json.JSONDecodeError, Exception):
        pass

    # Strategy 2: json_repair (handles structural issues)
    if json_repair is not None:
        try:
            repaired = json_repair.loads(cleaned)
            if isinstance(repaired, dict):
                repaired = _strip_schema_metadata(repaired, schema)
            if isinstance(repaired, (dict, list)):
                return schema.model_validate(repaired)
        except Exception:
            pass

        try:
            repaired = json_repair.loads(sanitize_llm_json(raw))
            if isinstance(repaired, dict):
                repaired = _strip_schema_metadata(repaired, schema)
            if isinstance(repaired, (dict, list)):
                return schema.model_validate(repaired)
        except Exception:
            pass

    # Strategy 3: Emergency fallback for answer-only schemas.
    model_fields = getattr(schema, "model_fields", {})
    if "answer" in model_fields and "action" not in model_fields:
        try:
            fallback_data = {"answer": _sanitize_fallback_text(raw)[:8000]}
            return schema.model_validate(fallback_data)
        except Exception:
            pass

    raise ValueError(
        f"Failed to parse LLM output as {schema.__name__}. "
        f"Cleaned output: {cleaned[:500]}"
    )


# Regex to collapse 3+ consecutive newlines to 2
_EXCESSIVE_NEWLINES_RE = re.compile(r"\n{3,}")


def normalize_answer_content(text: str) -> str:
    """
    Post-process answer content after JSON parsing to fix common
    formatting artifacts from json_repair and LLM output.
    """
    if not text:
        return text

    result = text

    # Protect genuine escaped backslashes first
    result = result.replace("\\\\", "\x00BSLASH\x00")

    # Double-escaped newlines -> actual newlines
    result = result.replace("\\n", "\n")

    # Double-escaped tabs -> actual tabs
    result = result.replace("\\t", "\t")

    # Double-escaped quotes -> actual quotes
    result = result.replace('\\"', '"')

    # Escaped forward slashes (common json_repair artifact)
    result = result.replace("\\/", "/")

    # Restore escaped backslashes
    result = result.replace("\x00BSLASH\x00", "\\")

    # Collapse excessive blank lines
    result = _EXCESSIVE_NEWLINES_RE.sub("\n\n", result)

    return result
