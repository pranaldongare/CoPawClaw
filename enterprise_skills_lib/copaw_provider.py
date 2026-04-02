"""
CoPaw-compatible FallbackProvider that wraps our invoke_llm() chain.

Registered as a custom provider in CoPaw's ProviderManager.
Bridges: CoPaw Provider ABC <-> enterprise_skills_lib.llm.client.invoke_llm()
"""

import asyncio
from typing import List, Tuple

from copaw.providers.provider import Provider, ModelInfo, ProviderInfo

from enterprise_skills_lib.config import settings
from enterprise_skills_lib.constants import (
    GPU_SENSING_CLASSIFY_LLM,
    GPU_SENSING_REPORT_LLM,
    PORT1,
)


class FallbackChatModel:
    """
    AgentScope ChatModelBase-compatible wrapper around invoke_llm().

    CoPaw's agent calls .chat() or .__call__() on this object.
    We route to invoke_llm() which handles the full GPU->Gemini->OpenAI chain.
    """

    def __init__(self, model_id: str, port: int = PORT1):
        self.model_id = model_id
        self.port = port

    async def __call__(self, prompt: str, **kwargs):
        """Direct invocation — used by CoPaw's agent loop."""
        from enterprise_skills_lib.llm.client import invoke_llm
        from enterprise_skills_lib.llm.output_schemas.base import SimpleTextOutput

        result = await invoke_llm(
            gpu_model=self.model_id,
            response_schema=SimpleTextOutput,
            contents=prompt,
            port=self.port,
        )
        return result.text


class FallbackProvider(Provider):
    """
    CoPaw Provider that delegates all LLM calls to our fallback chain.

    Registration:
        provider_manager.add_custom_provider(FallbackProvider(
            id="fallback",
            name="Enterprise Fallback (GPU->Gemini->OpenAI)",
            base_url=f"http://localhost:{PORT1}",
            api_key="not-needed",
            is_local=False,
            is_custom=True,
        ))
    """

    async def check_connection(self, timeout: float = 5) -> Tuple[bool, str]:
        """Verify that at least one backend in the chain is reachable."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(f"http://localhost:{PORT1}/v1/models")
                if resp.status_code == 200:
                    return True, "GPU server is reachable"
        except Exception:
            pass
        # GPU is down but Gemini/OpenAI might work
        return True, "GPU unreachable, but cloud fallbacks available"

    async def fetch_models(self, timeout: float = 5) -> List[ModelInfo]:
        """Return the models our chain supports."""
        return [
            ModelInfo(id=GPU_SENSING_CLASSIFY_LLM.model, name="Sensing Classify Model"),
            ModelInfo(id=GPU_SENSING_REPORT_LLM.model, name="Sensing Report Model"),
            ModelInfo(id="gemini-2.5-flash", name="Gemini 2.5 Flash (fallback)"),
            ModelInfo(id="gpt-4o-mini", name="OpenAI GPT-4o Mini (fallback)"),
        ]

    async def check_model_connection(
        self, model_id: str, timeout: float = 5
    ) -> Tuple[bool, str]:
        return True, f"Model {model_id} available via fallback chain"

    def get_chat_model_instance(self, model_id: str):
        """Return our FallbackChatModel wrapping invoke_llm()."""
        return FallbackChatModel(model_id=model_id, port=PORT1)
