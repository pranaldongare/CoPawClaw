"""Tests for configuration loading."""

import pytest

from enterprise_skills_lib.config import Settings
from enterprise_skills_lib.constants import (
    GPU_SENSING_CLASSIFY_LLM,
    GPU_SENSING_REPORT_LLM,
    PORT1,
    SWITCHES,
)


class TestSettings:
    def test_defaults(self):
        """Settings should load with defaults even without env vars."""
        s = Settings()
        assert s.MAIN_MODEL is not None
        assert isinstance(s.OPENAI_API, str)

    def test_api_keys_exist(self):
        s = Settings()
        # All 6 API key fields should exist
        for i in range(1, 7):
            assert hasattr(s, f"API_KEY_{i}")


class TestConstants:
    def test_switches(self):
        assert isinstance(SWITCHES, dict)
        assert "FALLBACK_TO_GEMINI" in SWITCHES
        assert "FALLBACK_TO_OPENAI" in SWITCHES

    def test_gpu_configs(self):
        assert GPU_SENSING_CLASSIFY_LLM.model is not None
        assert GPU_SENSING_REPORT_LLM.model is not None

    def test_port(self):
        assert PORT1 == 11434
