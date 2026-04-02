"""
Feature switches, GPU model configs, and platform constants.

Adapted from source repo — stripped to skills-platform-relevant constants only.
"""

from pydantic import BaseModel

from enterprise_skills_lib.config import settings


class GPULLMConfig(BaseModel):
    model: str
    port: int


# Feature switches — control fallback behavior and skill enablement
SWITCHES = {
    # LLM fallback chain — set both to False for GPU-only (no remote calls)
    "FALLBACK_TO_GEMINI": False,
    "FALLBACK_TO_OPENAI": False,
    "USE_INTERNAL": settings.USE_INTERNAL,
    "REMOTE_GPU": settings.REMOTE_GPU,
    "DISABLE_THINKING": True,

    # Skills
    "TECH_SENSING": True,
    "COMPETITIVE_INTEL": True,
    "PATENT_MONITOR": True,
    "REGULATION_TRACKER": True,
    "TALENT_RADAR": True,
    "EXECUTIVE_BRIEF": True,
    "EMAIL_DIGEST": True,
    "PPTX_GEN": True,
}

# GPU server ports
PORT1 = 11434  # Primary GPU server (vLLM/Ollama)
PORT2 = 11435  # Vision model (optional)

MAIN_MODEL = settings.MAIN_MODEL

# GPU LLM configurations — all sensing skills share these
GPU_SENSING_CLASSIFY_LLM = GPULLMConfig(model=MAIN_MODEL, port=PORT1)
GPU_SENSING_REPORT_LLM = GPULLMConfig(model=MAIN_MODEL, port=PORT1)

# Additional skill-specific GPU configs (can point to different models/ports if needed)
GPU_COMPETITIVE_LLM = GPULLMConfig(model=MAIN_MODEL, port=PORT1)
GPU_PATENT_LLM = GPULLMConfig(model=MAIN_MODEL, port=PORT1)
GPU_REGULATION_LLM = GPULLMConfig(model=MAIN_MODEL, port=PORT1)
GPU_TALENT_LLM = GPULLMConfig(model=MAIN_MODEL, port=PORT1)
GPU_EXECUTIVE_LLM = GPULLMConfig(model=MAIN_MODEL, port=PORT1)

# Fallback LLM models
FALLBACK_GEMINI_MODEL = "gemini-2.5-flash"
FALLBACK_OPENAI_MODEL = "gpt-4o-mini"
