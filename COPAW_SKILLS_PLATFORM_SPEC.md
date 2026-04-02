# CoPaw Enterprise Skills Platform — Technical Specification

> **Version**: 1.0.0
> **Author**: System Architecture Team
> **Date**: 2026-04-01
> **Status**: Implementation-Ready Specification
> **Target Framework**: CoPaw v1.0.0 (github.com/agentscope-ai/CoPaw, 14K+ stars, Python, Apache 2.0)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [CoPaw Framework Integration Strategy](#3-copaw-framework-integration-strategy)
4. [The Fallback LLM Provider](#4-the-fallback-llm-provider)
5. [Skill 1: Tech Sensing](#5-skill-1-tech-sensing)
6. [Skill 2: PPTX Generation](#6-skill-2-pptx-generation)
7. [Skill 3: Competitive Intelligence](#7-skill-3-competitive-intelligence)
8. [Skill 4: Patent Monitor](#8-skill-4-patent-monitor)
9. [Skill 5: Regulation Tracker](#9-skill-5-regulation-tracker)
10. [Skill 6: Talent Radar](#10-skill-6-talent-radar)
11. [Skill 7: Executive Brief Composer](#11-skill-7-executive-brief-composer)
12. [Skill 8: Email Digest Composer](#12-skill-8-email-digest-composer)
13. [Cross-Skill Data Contracts](#13-cross-skill-data-contracts)
14. [Multi-Agent Orchestration Patterns](#14-multi-agent-orchestration-patterns)
15. [Source Repository Code Reuse Map](#15-source-repository-code-reuse-map)
16. [Pydantic Schema Reference](#16-pydantic-schema-reference)
17. [LLM Prompt Engineering Reference](#17-llm-prompt-engineering-reference)
18. [Data Storage & Persistence](#18-data-storage--persistence)
19. [API & Real-Time Communication](#19-api--real-time-communication)
20. [Configuration & Environment](#20-configuration--environment)
21. [Testing Strategy](#21-testing-strategy)
22. [Deployment & Security](#22-deployment--security)
23. [Implementation Roadmap](#23-implementation-roadmap)

---

## 1. Executive Summary

### 1.1 Purpose

This specification defines a multi-skill enterprise platform built on **CoPaw** (an open-source Python multi-agent framework). The platform reuses production-hardened code from an existing internal repository ("source repo") — specifically its **Tech Sensing pipeline**, **LLM invocation infrastructure**, and **structured output parsing** — and extends it with seven additional enterprise skills.

### 1.2 Why CoPaw

| Criterion | CoPaw Advantage |
|-----------|----------------|
| **Language** | Python-native — matches source repo entirely |
| **Skill system** | Markdown-driven `SKILL.md` + Python scripts — no class inheritance ceremony |
| **Provider system** | Pluggable `Provider` ABC with built-in Ollama, OpenAI, Gemini, Anthropic |
| **Multi-agent** | Built-in `MultiAgentManager` with lazy loading, hot-reload, inter-agent CLI chat |
| **MCP support** | Native `MCPClientManager` with stdio and HTTP transports, file-watching hot-reload |
| **Channels** | 12+ built-in (Discord, Telegram, DingTalk, Feishu, Slack, etc.) |
| **Configuration** | Pydantic models loaded from `~/.copaw/config.json` |
| **Security** | Skill security scanning, provider key masking |
| **Maturity** | v1.0.0 (2026-03-30), 14K+ stars, active development |

### 1.3 What We Are Building

Eight interconnected skills orchestrated by CoPaw's multi-agent system:

| # | Skill | Description | Source Repo Reuse |
|---|-------|-------------|-------------------|
| 1 | **Tech Sensing** | 7-stage pipeline: Ingest(5 sources) -> Dedup -> Extract -> Classify -> Report -> Verify -> Movement | **Heavy** — full `core/sensing/` module |
| 2 | **PPTX Generation** | Beautiful presentations from any skill's output | New (uses CoPaw's built-in PPTX skill as foundation) |
| 3 | **Competitive Intelligence** | Company/product competitive landscape analysis | Partial — reuses ingest, classify, LLM infrastructure |
| 4 | **Patent Monitor** | Patent filing monitoring and analysis | Partial — reuses ingest patterns, LLM infrastructure |
| 5 | **Regulation Tracker** | Regulatory change monitoring (AI Act, GDPR, etc.) | Partial — reuses ingest patterns, LLM infrastructure |
| 6 | **Talent Radar** | AI/tech talent market intelligence | Partial — reuses ingest patterns, LLM infrastructure |
| 7 | **Executive Brief** | Cross-skill synthesis into C-suite one-pagers | New — consumes outputs from all other skills |
| 8 | **Email Digest** | Scheduled multi-skill digests via SMTP | **Heavy** — reuses `core/sensing/email_digest.py` + scheduler |

### 1.4 Key Architectural Decision: Library Extraction, Not Fork

We will **NOT** fork CoPaw. Instead:

1. Install CoPaw as a dependency (`pip install copaw`)
2. Extract reusable source repo code into a **shared Python library** (`enterprise_skills_lib/`)
3. Each CoPaw skill references this library from its `scripts/` directory
4. The `FallbackProvider` wraps the source repo's `invoke_llm()` as a CoPaw-compatible provider

This gives us clean separation: CoPaw handles agent orchestration, channels, MCP, and multi-agent coordination. Our library handles domain logic, LLM invocation, and structured output parsing.

---

## 2. Architecture Overview

### 2.1 High-Level Diagram

```
+------------------------------------------------------------------+
|                      CoPaw Multi-Agent Platform                   |
|                                                                   |
|  +-------------------+  +-------------------+  +---------------+  |
|  | Agent: Analyst     |  | Agent: Reporter   |  | Agent: Admin  |  |
|  | Skills:            |  | Skills:           |  | Skills:       |  |
|  |  - tech_sensing    |  |  - pptx           |  |  - scheduler  |  |
|  |  - competitive_intel|  |  - exec_brief    |  |  - email_digest|  |
|  |  - patent_monitor  |  |                   |  |               |  |
|  |  - regulation_tracker|  |                  |  |               |  |
|  |  - talent_radar    |  |                   |  |               |  |
|  +--------+-----------+  +--------+----------+  +-------+-------+  |
|           |                       |                      |         |
|           +----------- CLI Chat --+----------+-----------+         |
|                                                                   |
|  +-------------------------------------------------------------+  |
|  |              enterprise_skills_lib/  (shared library)         |  |
|  |  invoke_llm()  |  Pydantic schemas  |  Ingest sources       |  |
|  |  JSON parsing   |  Dedup/Classify   |  Signal scoring        |  |
|  +-------------------------------------------------------------+  |
|                                                                   |
|  +-------------------------------------------------------------+  |
|  |              FallbackProvider (CoPaw Provider)                |  |
|  |  GPU (vLLM/Ollama) -> Gemini (6-key rotation) -> OpenAI     |  |
|  +-------------------------------------------------------------+  |
+------------------------------------------------------------------+
         |               |                |
    Channels          MCP Servers      REST API
  (Discord,          (custom tools)   (FastAPI)
   Telegram,
   Slack, ...)
```

### 2.2 Directory Structure

```
copaw-enterprise-skills/
|-- pyproject.toml                     # Project metadata, dependencies
|-- .env.example                       # Environment variable template
|-- Makefile                           # build, run, test, lint targets
|-- Dockerfile                         # Container build
|-- docker-compose.yml                 # Full stack (CoPaw + services)
|
|-- enterprise_skills_lib/             # Shared Python library
|   |-- __init__.py
|   |-- llm/
|   |   |-- __init__.py
|   |   |-- client.py                  # invoke_llm() with fallback chain
|   |   |-- output_sanitizer.py        # 6-step JSON sanitization pipeline
|   |   |-- output_schemas/
|   |   |   |-- __init__.py
|   |   |   |-- base.py               # LLMOutputBase with Unicode validators
|   |   |   |-- sensing.py            # All tech sensing Pydantic models
|   |   |   |-- competitive.py        # Competitive intel schemas
|   |   |   |-- patents.py            # Patent monitor schemas
|   |   |   |-- regulations.py        # Regulation tracker schemas
|   |   |   |-- talent.py             # Talent radar schemas
|   |   |   |-- executive.py          # Executive brief schemas
|   |   |-- prompts/
|   |   |   |-- sensing_prompts.py     # Tech sensing prompt templates
|   |   |   |-- competitive_prompts.py
|   |   |   |-- patent_prompts.py
|   |   |   |-- regulation_prompts.py
|   |   |   |-- talent_prompts.py
|   |   |   |-- executive_prompts.py
|   |-- sensing/                       # Core sensing logic (extracted from source)
|   |   |-- __init__.py
|   |   |-- pipeline.py               # 7-stage orchestrator
|   |   |-- config.py                 # RSS feeds, domains, constants
|   |   |-- ingest.py                 # RawArticle + fetch functions
|   |   |-- sources/
|   |   |   |-- arxiv_search.py
|   |   |   |-- github_trending.py
|   |   |   |-- hackernews.py
|   |   |-- dedup.py                  # URL normalization + fuzzy title matching
|   |   |-- classify.py              # Batched LLM classification with cache
|   |   |-- cache.py                 # URL-hashed classification cache (30d TTL)
|   |   |-- report_generator.py      # 2-phase LLM report generation
|   |   |-- verifier.py              # LLM-based relevance verification
|   |   |-- signal_score.py          # Source authority + diversity scoring
|   |   |-- movement.py              # Radar ring movement detection
|   |   |-- deep_dive.py             # Focused technology deep-dive analysis
|   |   |-- comparison.py            # Report-to-report diffing
|   |   |-- collaboration.py         # Share, vote, comment on reports
|   |   |-- org_context.py           # Organizational context personalization
|   |   |-- timeline.py             # Multi-report technology timeline builder
|   |   |-- scheduler.py            # Asyncio-based recurring execution
|   |   |-- email_digest.py         # SMTP email sending
|   |-- config.py                    # Pydantic Settings (env vars)
|   |-- constants.py                 # GPULLMConfig, model ports, switches
|
|-- copaw_config/                     # CoPaw configuration files
|   |-- config.json                   # Main CoPaw config
|   |-- providers/
|   |   |-- fallback_provider.json    # FallbackProvider registration
|
|-- skills/                           # CoPaw skill directories
|   |-- tech_sensing/
|   |   |-- SKILL.md
|   |   |-- scripts/
|   |   |   |-- run_pipeline.py
|   |   |   |-- run_deep_dive.py
|   |   |   |-- run_comparison.py
|   |   |   |-- run_timeline.py
|   |   |   |-- manage_schedule.py
|   |   |   |-- manage_collaboration.py
|   |   |   |-- manage_org_context.py
|   |-- pptx_gen/
|   |   |-- SKILL.md
|   |   |-- references/
|   |   |   |-- design_system.md
|   |   |   |-- slide_templates.md
|   |   |-- scripts/
|   |   |   |-- generate_deck.py
|   |   |   |-- skill_to_slides.py
|   |-- competitive_intel/
|   |   |-- SKILL.md
|   |   |-- scripts/
|   |   |   |-- run_competitive_analysis.py
|   |   |   |-- track_company.py
|   |-- patent_monitor/
|   |   |-- SKILL.md
|   |   |-- scripts/
|   |   |   |-- run_patent_scan.py
|   |   |   |-- analyze_patent.py
|   |-- regulation_tracker/
|   |   |-- SKILL.md
|   |   |-- scripts/
|   |   |   |-- run_regulation_scan.py
|   |   |   |-- impact_assessment.py
|   |-- talent_radar/
|   |   |-- SKILL.md
|   |   |-- scripts/
|   |   |   |-- run_talent_scan.py
|   |   |   |-- skill_gap_analysis.py
|   |-- executive_brief/
|   |   |-- SKILL.md
|   |   |-- scripts/
|   |   |   |-- compose_brief.py
|   |   |   |-- cross_skill_synthesis.py
|   |-- email_digest/
|   |   |-- SKILL.md
|   |   |-- scripts/
|   |   |   |-- send_digest.py
|   |   |   |-- manage_subscriptions.py
|
|-- api/                              # Optional REST API layer
|   |-- __init__.py
|   |-- main.py                       # FastAPI app
|   |-- routes/
|   |   |-- sensing.py
|   |   |-- skills.py
|   |   |-- schedules.py
|   |-- socket_handler.py            # Socket.IO for real-time progress
|
|-- tests/
|   |-- unit/
|   |-- integration/
|   |-- conftest.py
|
|-- data/                             # Runtime data (gitignored)
|   |-- sensing_cache/
|   |-- shared_reports/
|   |-- schedules/
|   |-- {user_id}/
|       |-- sensing/
|       |-- competitive/
|       |-- patents/
|       |-- regulations/
|       |-- talent/
|       |-- briefs/
```

---

## 3. CoPaw Framework Integration Strategy

### 3.1 Understanding CoPaw's Skill Model

**Critical**: CoPaw skills are NOT Python classes with an `execute()` method. They are **markdown-driven prompt/tool bundles**:

- A `SKILL.md` file with YAML frontmatter defines the skill (name, description, metadata)
- The markdown body is injected into the agent's system prompt
- Python scripts in `scripts/` are executed via the agent's `execute_shell_command` tool
- The agent (LLM) decides when and how to invoke the skill based on the user's request

This means our skills consist of:
1. **`SKILL.md`** — Instructions telling the agent what the skill can do, when to use it, and what scripts to call
2. **`scripts/`** — Python entry points that import from `enterprise_skills_lib/` and execute domain logic
3. **`references/`** — Additional context documents the agent can read

### 3.2 CoPaw Installation and Setup

```bash
# Install CoPaw
pip install copaw

# Initialize workspace
copaw init

# Directory created: ~/.copaw/
#   config.json         — main config
#   .secret/            — provider API keys
#   skill_pool/         — shared skills
#   workspaces/         — per-agent state
```

### 3.3 Registering Our Skills

CoPaw discovers skills by scanning directories for `SKILL.md` files. There are three registration paths:

**Option A: Symlink into workspace** (recommended for development)
```bash
# For each skill
ln -s /path/to/copaw-enterprise-skills/skills/tech_sensing ~/.copaw/workspaces/{agent_id}/skills/tech_sensing
```

**Option B: Install to skill pool** (recommended for production)
```bash
copaw skill install /path/to/copaw-enterprise-skills/skills/tech_sensing
```

**Option C: Package as zip** (for distribution)
```bash
cd skills/tech_sensing && zip -r tech_sensing.zip . && copaw skill import tech_sensing.zip
```

After installation, CoPaw runs `reconcile_workspace_manifest()` which:
1. Scans for directories containing `SKILL.md`
2. Reads YAML frontmatter (name, description, metadata)
3. Computes content SHA-256 hash for change detection
4. Updates `skill.json` manifest

### 3.4 Agent Configuration

Each CoPaw agent is a `Workspace` with its own model config, skills, and MCP clients. Configure in `~/.copaw/config.json`:

```json
{
  "agents": [
    {
      "id": "analyst",
      "name": "Enterprise Analyst",
      "provider_id": "fallback",
      "model_id": "gpt-oss-20b",
      "skills": {
        "tech_sensing": {"enabled": true, "channels": ["*"]},
        "competitive_intel": {"enabled": true, "channels": ["*"]},
        "patent_monitor": {"enabled": true, "channels": ["*"]},
        "regulation_tracker": {"enabled": true, "channels": ["*"]},
        "talent_radar": {"enabled": true, "channels": ["*"]}
      },
      "running_params": {
        "retry_limit": 3,
        "rate_limit": {"max_calls": 10, "window_seconds": 60}
      }
    },
    {
      "id": "reporter",
      "name": "Report Generator",
      "provider_id": "fallback",
      "model_id": "gpt-oss-20b",
      "skills": {
        "pptx_gen": {"enabled": true, "channels": ["*"]},
        "executive_brief": {"enabled": true, "channels": ["*"]}
      }
    },
    {
      "id": "admin",
      "name": "Platform Admin",
      "provider_id": "fallback",
      "model_id": "gpt-oss-20b",
      "skills": {
        "email_digest": {"enabled": true, "channels": ["*"]}
      }
    }
  ]
}
```

---

## 4. The Fallback LLM Provider

### 4.1 Overview

The source repo's core strength is its **battle-tested LLM invocation chain** (`invoke_llm()`). We must preserve this exact behavior inside CoPaw's provider system.

CoPaw uses AgentScope's `ChatModelBase` as its LLM abstraction. Our `FallbackProvider` bridges between CoPaw's provider interface and our `invoke_llm()` function.

### 4.2 Source Repo `invoke_llm()` — Complete Behavior Specification

```
invoke_llm(gpu_model, response_schema, contents, port=11434, remove_thinking=False)
```

**Fallback Chain (exact order):**

```
Phase 0: INTERNAL API (if USE_INTERNAL=True)
  |-- Up to 4 retries with rate limiting (3 calls/min)
  |-- Self-correction: on parse failure, injects failed output + error into next prompt
  |-- On network error: break immediately, set sticky fallback (contextvars)
  |-- On exhaustion: set _skip_internal=True for entire async context

Phase 1: Main retry loop (4 iterations)
  |
  |-- Step 1: GPU Server (vLLM/Ollama on configurable port)
  |     invoke via asyncio.to_thread(_get_cached_llm(model, port)._call(prompt))
  |     On parse failure: self-correction retry (inject failed output)
  |     On network failure: fall through to Gemini
  |
  |-- Step 2: Gemini Fallback (if SWITCHES["FALLBACK_TO_GEMINI"])
  |     Cycle through 6 API keys (round-robin with asyncio.Lock)
  |     Model: gemini-2.5-flash
  |     Temperature: 0.2, max_output_tokens: 200000
  |     Timeout: 80s per key (asyncio.wait_for)
  |     Optional: thinking_budget=0 if remove_thinking=True
  |     On timeout: try next key
  |     On parse failure: log, sleep 0.2s, try next key
  |
  |-- Step 3: OpenAI Fallback (if SWITCHES["FALLBACK_TO_OPENAI"])
  |     Model: gpt-4o-mini
  |     Temperature: 0.2
  |     Single attempt per iteration
  |
  After each full iteration failure: sleep 2s
  After 4 iterations: raise RuntimeError
```

**JSON Parse Pipeline (`_try_parse`):**

```
Strategy 1: sanitize_llm_json() + PydanticOutputParser.parse()
Strategy 2: sanitize_llm_json() + json.loads() + _strip_schema_metadata() + model_validate()
Strategy 3: parse_llm_json() (json_repair + model_validate)
Post-validation: _check_empty_lists() rejects outputs where ALL required list fields are empty
```

**JSON Sanitization (`sanitize_llm_json`) — 6 steps:**
1. Strip `<think>` and `<reasoning>` XML tags
2. Extract from markdown code fences (```json ... ```)
3. Replace Unicode whitespace with ASCII space
4. Remove zero-width characters
5. Extract JSON object/array using bracket counting + known first-field regex
6. Escape literal control characters inside JSON string values

**Self-Correction Mechanism:**
When a parse attempt fails, the next retry injects:
```
--- PREVIOUS ATTEMPT FAILED ---
Your output: {truncated_to_2000_chars}
Parse error: {error_message}
Please fix the JSON and try again.
```

### 4.3 FallbackProvider Implementation

```python
# enterprise_skills_lib/copaw_provider.py

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
        # For unstructured chat, we use a simple text response schema
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
            api_key="not-needed",  # Keys managed internally
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
            ModelInfo(id=settings.MAIN_MODEL, name="Main GPU Model (gpt-oss-20b)"),
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
```

### 4.4 Provider Registration

Save to `~/.copaw/.secret/providers/custom/fallback.json`:

```json
{
  "id": "fallback",
  "name": "Enterprise Fallback (GPU->Gemini->OpenAI)",
  "base_url": "http://localhost:11434",
  "api_key": "managed-internally",
  "chat_model": "enterprise_skills_lib.copaw_provider.FallbackProvider",
  "is_local": false,
  "is_custom": true,
  "models": [
    {"id": "gpt-oss-20b", "name": "Main GPU Model"}
  ]
}
```

Alternatively, register programmatically:

```python
from copaw.providers.provider_manager import ProviderManager
from enterprise_skills_lib.copaw_provider import FallbackProvider

pm = ProviderManager.get_instance()
pm.add_custom_provider(FallbackProvider(
    id="fallback",
    name="Enterprise Fallback (GPU->Gemini->OpenAI)",
    base_url="http://localhost:11434",
    api_key="managed-internally",
    is_local=False,
    is_custom=True,
))
```

### 4.5 Feature Switches

Preserve the source repo's `SWITCHES` dict to control fallback behavior:

```python
# enterprise_skills_lib/constants.py

SWITCHES = {
    "FALLBACK_TO_GEMINI": True,       # Enable Gemini fallback
    "FALLBACK_TO_OPENAI": True,       # Enable OpenAI fallback
    "USE_INTERNAL": False,            # INTERNAL API as primary
    "REMOTE_GPU": False,              # Remote vs local GPU
    "TECH_SENSING": True,             # Tech sensing feature
    "DISABLE_THINKING": True,         # Disable LLM thinking mode
}
```

### 4.6 Environment Variables Required

```bash
# GPU Server
MAIN_MODEL=gpt-oss-20b              # Primary GPU model name
QUERY_URL=http://localhost:11434     # vLLM/Ollama endpoint
VISION_URL=http://localhost:11435    # VLM endpoint (optional)

# Gemini API Keys (6 for round-robin rotation)
API_KEY_1=AIza...
API_KEY_2=AIza...
API_KEY_3=AIza...
API_KEY_4=AIza...
API_KEY_5=AIza...
API_KEY_6=AIza...

# OpenAI
OPENAI_API=sk-...

# INTERNAL API (optional)
USE_INTERNAL=false
INTERNAL_BASE_URL=
INTERNAL_CLIENT_KEY=
INTERNAL_API_TOKEN=
INTERNAL_USER_EMAIL=
INTERNAL_MODEL_ID=

# SMTP (for email digest)
SMTP_HOST=smtp.company.com
SMTP_PORT=587
SMTP_USER=alerts@company.com
SMTP_PASSWORD=...
SMTP_FROM=alerts@company.com
SMTP_USE_TLS=true

# GitHub (for trending repos)
GITHUB_TOKEN=ghp_...                  # Optional, increases rate limits

# MongoDB (for user auth, optional)
DATABASE_URL=mongodb://localhost:27017
SECRET_KEY=your-jwt-secret
```

---

## 5. Skill 1: Tech Sensing

### 5.1 Overview

The flagship skill. A 7-stage pipeline that scans 5 data sources, deduplicates, extracts full text, classifies via LLM, generates a Technology Radar report, verifies relevance, and detects movement trends.

**This skill is a direct port of the source repo's `core/sensing/` module — 15 Python files, ~2,500 lines of production code.**

### 5.2 SKILL.md

```yaml
---
name: tech_sensing
description: "Run a comprehensive Technology Radar analysis. Ingests articles from RSS, DuckDuckGo, GitHub Trending, arXiv, and Hacker News, then classifies, generates radar reports, deep dives, comparisons, and timelines. Use this skill when the user asks about technology trends, emerging tech, or wants a sensing report."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "radar"
  requires:
    bins: ["python3"]
    env: ["MAIN_MODEL", "API_KEY_1"]
---

# Tech Sensing Skill

## What This Skill Does

Generates Technology Radar reports by scanning 5 data sources and analyzing trends via LLM.

## Available Commands

### Generate a full sensing report
```bash
python3 scripts/run_pipeline.py --domain "Generative AI" --lookback-days 7 --user-id "$USER_ID"
```

Optional arguments:
- `--custom-requirements "Focus on LLM agents"` — additional guidance for the LLM
- `--must-include "RAG,agents,MCP"` — comma-separated keywords to prioritize
- `--dont-include "crypto,blockchain"` — comma-separated keywords to exclude
- `--feed-urls "url1,url2"` — override default RSS feeds
- `--search-queries "query1,query2"` — override default DuckDuckGo queries

Output: JSON file at `data/{user_id}/sensing/report_{tracking_id}.json`

### Deep dive into a specific technology
```bash
python3 scripts/run_deep_dive.py --technology "Model Context Protocol" --domain "Generative AI" --user-id "$USER_ID"
```

Output: JSON with comprehensive_analysis, technical_architecture, competitive_landscape, adoption_roadmap, risk_assessment, key_resources

### Compare two reports
```bash
python3 scripts/run_comparison.py --report-a "$TRACKING_ID_A" --report-b "$TRACKING_ID_B" --user-id "$USER_ID"
```

Output: Radar diff (added/removed/moved/unchanged items), trend diff, signal diffs

### Build technology timeline
```bash
python3 scripts/run_timeline.py --user-id "$USER_ID" --domain "Generative AI"
```

Output: Per-technology ring evolution across all historical reports

### Manage schedules
```bash
python3 scripts/manage_schedule.py --action create --domain "Generative AI" --frequency weekly --user-id "$USER_ID"
python3 scripts/manage_schedule.py --action list --user-id "$USER_ID"
python3 scripts/manage_schedule.py --action delete --schedule-id "$ID"
```

### Manage collaboration (share, vote, comment)
```bash
python3 scripts/manage_collaboration.py --action share --report-id "$TRACKING_ID" --user-id "$USER_ID"
python3 scripts/manage_collaboration.py --action vote --share-id "$ID" --item "GPT-5" --ring "Trial" --user-id "$USER_ID"
python3 scripts/manage_collaboration.py --action comment --share-id "$ID" --text "Interesting trend" --user-id "$USER_ID"
python3 scripts/manage_collaboration.py --action feedback --share-id "$ID"
```

### Manage organizational context
```bash
python3 scripts/manage_org_context.py --action get --user-id "$USER_ID"
python3 scripts/manage_org_context.py --action update --user-id "$USER_ID" --tech-stack "Python,React,PostgreSQL" --industry "Financial Services" --priorities "AI automation,Cost reduction"
```

## Report Structure

The generated report contains:
- **Executive Summary** — High-level overview
- **Headline Moves** — Top 10 significant industry moves (actor + segment + sources)
- **Key Trends** — 5-10 trends with evidence, impact level (High/Medium/Low), time horizon
- **Technology Radar** — 15-30 items across 4 quadrants (Techniques/Platforms/Tools/Languages & Frameworks) and 4 rings (Adopt/Trial/Assess/Hold)
- **Radar Item Details** — Deep write-up per item: what_it_is, why_it_matters, current_state, key_players, practical_applications
- **Market Signals** — Company/player strategic moves with industry impact assessment
- **Report Sections** — 3-6 deep-dive narrative sections
- **Recommendations** — Prioritized (Critical/High/Medium/Low) with related trends
- **Notable Articles** — Top source articles with relevance scores

## When to Use

- User asks about "technology trends", "what's new in AI", "emerging technologies"
- User wants a "tech radar", "sensing report", "technology landscape"
- User asks to "monitor" or "track" technology areas
- User wants to compare reports or see how technologies have evolved
- User wants to schedule recurring reports
```

### 5.3 Pipeline Stages — Detailed Specification

**Stage 1: Ingest** (5 parallel data sources)

| Source | Module | API/Method | Key Parameters | Output Mapping to RawArticle |
|--------|--------|-----------|----------------|------------------------------|
| RSS Feeds | `ingest.py` | `feedparser.parse()` via `asyncio.to_thread` | `get_feeds_for_domain(domain)` returns general (5 feeds) + domain-specific (3-11 feeds). Domains: ai, robotics, quantum, cybersecurity, blockchain, cloud. Max `MAX_ARTICLES_PER_FEED=20` per feed. Lookback filtering via parsed date. | `title=entry["title"]`, `url=entry["link"]`, `source=feed.feed["title"][:50]`, `published_date=_parse_feed_date()`, `snippet=entry["summary"][:500]`, `content=""` |
| DuckDuckGo | `ingest.py` | `DDGS().text()` (sync, via `asyncio.to_thread`) | `get_search_queries_for_domain(domain, must_include)` returns 5 base queries + up to 5 from must_include. `MAX_SEARCH_RESULTS=30`. Timelimit: <=7d->"w", <=30d->"m", else->"y". | `title=r["title"]`, `url=r["href"]`, `source="DuckDuckGo"`, `snippet=r["body"][:500]` |
| GitHub Trending | `sources/github_trending.py` | `httpx.AsyncClient` -> `api.github.com/search/repositories` | Query: `"{domain} created:>{cutoff}"` or `"{domain} stars:>10"`. Sort by stars desc. `GITHUB_MAX_RESULTS=15`. Optional `GITHUB_TOKEN` for auth. | `title=repo["full_name"]`, `url=repo["html_url"]`, `source="GitHub"`, `published_date=repo["created_at"]`, `snippet="{stars} stars | {language} | {desc[:200]}"`, `content=repo["description"]` |
| arXiv | `sources/arxiv_search.py` | `httpx.AsyncClient` -> `export.arxiv.org/api/query` (Atom feed parsed by feedparser) | Query: `"all:{domain}"` AND up to 3 must_include keywords. `ARXIV_MAX_RESULTS=20`. Sorted by submittedDate desc. | `title=entry["title"]` (newlines stripped), `url=entry["link"]`, `source="arXiv"`, `published_date=entry["published"]`, `snippet="{authors} | {categories}"`, `content=entry["summary"]` |
| Hacker News | `sources/hackernews.py` | `httpx.AsyncClient` -> `hn.algolia.com/api/v1/search_by_date` | `query=domain`, `tags="story"`, `HN_MAX_RESULTS=20`. Numeric filter on `created_at_i` for lookback. | `title=hit["title"]`, `url=hit["url"]` (fallback: HN item link), `source="Hacker News"`, `published_date=hit["created_at"]`, `snippet="{points} points, {comments} comments"`, `content=hit["story_text"]` |

**RawArticle dataclass:**
```python
@dataclass
class RawArticle:
    title: str
    url: str
    source: str
    published_date: Optional[str] = None   # ISO format
    content: str = ""                       # Full extracted text
    snippet: str = ""                       # Short excerpt
```

**General RSS Feeds (always included):**
- MIT Technology Review (`technologyreview.com/feed`)
- TechCrunch AI (`techcrunch.com/category/artificial-intelligence/feed`)
- VentureBeat AI (`venturebeat.com/category/ai/feed`)
- Wired (`wired.com/feed/rss`)
- Ars Technica (`feeds.arstechnica.com/arstechnica/technology-lab`)

**Domain-specific feeds** (examples for "ai" domain — 11 feeds):
Includes OpenAI blog, Google AI blog, Hugging Face blog, NVIDIA AI blog, DeepMind, AI News, The Batch, IEEE Spectrum AI, Sebastian Raschka, etc.

**Stage 2: Dedup**

Two-phase deduplication:
1. **URL normalization**: Parse URL, strip tracking params (`utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`, `ref`, `source`, `fbclid`, `gclid`), strip fragment, strip trailing `/`, lowercase. Exact match on normalized URL.
2. **Fuzzy title matching**: `difflib.SequenceMatcher.ratio()` >= `DEDUP_SIMILARITY_THRESHOLD` (0.85).

Then **keyword exclusion** filter: if `dont_include` is provided, remove articles where `f"{title} {snippet} {content}".lower()` contains any excluded keyword.

**Stage 3: Extract Full Text**

Parallel extraction with `asyncio.Semaphore(5)` (max 5 concurrent HTTP fetches):
- Primary: `trafilatura.fetch_url()` + `trafilatura.extract()`, cap at 5,000 chars
- Fallback: use existing `snippet` or `title` as content

**Stage 4: Classify**

Batched LLM classification:
- Batch size: `ARTICLE_BATCH_SIZE = 6` articles per LLM call
- Model: `GPU_SENSING_CLASSIFY_LLM` (same as `MAIN_MODEL` on `PORT1`)
- Schema: `ArticleBatchClassification` -> `List[ClassifiedArticle]`
- Cache check first: `get_cached_classification(url)` — SHA-256 of URL, 30-day TTL, stored at `data/sensing_cache/{hash}.json`
- Each article classified with: `relevance_score` (0.0-1.0), `quadrant`, `ring`, `technology_name`, `topic_category`, `industry_segment`, `summary`, `reasoning`
- Filter: only keep articles with `relevance_score >= MIN_RELEVANCE_SCORE` (0.3)

**Topic categories**: Foundation Models & Agents, Safety & Governance, Infrastructure & Tooling, Applications & Industry, Research & Breakthroughs

**Industry segments**: Frontier Labs, Big Tech Platforms, Enterprise & B2B, Open Source & Community, Startups & VC

**Stage 5: Generate Report** (2-phase LLM generation)

*Phase 1 — Skeleton:*
- Input: Top 50 articles by relevance score, with content excerpts (800 chars each)
- Model: `GPU_SENSING_REPORT_LLM`
- Schema: `TechSensingReportSkeleton`
- Output: report_title, executive_summary, headline_moves (10), key_trends (5-10), radar_items (15-30), market_signals (5-10), report_sections (3-6), recommendations, notable_articles
- Org context injected if available (tech_stack, industry, priorities)

*Phase 2 — Radar Details:*
- Input: radar_items from Phase 1 + classified articles
- Model: `GPU_SENSING_REPORT_LLM`
- Schema: `RadarDetailsOutput`
- Output: Per-item `RadarItemDetail` with what_it_is, why_it_matters, current_state, key_players, practical_applications, source_urls

*Merge: Skeleton + Details = `TechSensingReport`*

**Stage 6: Verify Relevance**

LLM-based verification using `GPU_SENSING_CLASSIFY_LLM`:
- Input: the complete report + domain + must_include/dont_include keywords
- Schema: `VerifiedItems` — lists of relevant radar_items, market_signals, trends (by name), plus `attribution_warnings` (format: `"tech_name: entity_to_remove | reason"`)
- Filters: removes items not in the verified lists, removes misattributed `key_players` from radar item details
- Fail-safe: on any error, returns original report unmodified

**Stage 7: Movement Detection**

Compares current radar items against the most recent previous report for the same user+domain:
- Scans `data/{user_id}/sensing/report_*.json` sorted by mtime
- Fuzzy name matching: `SequenceMatcher.ratio()` >= 0.85
- Sets `moved_in` field on items whose ring changed (e.g., `"Assess -> Trial"`)

**Post-pipeline: Signal Strength Scoring**

Pure computation (no LLM):
- For each radar item, finds supporting articles by matching `technology_name` (lowered)
- Composite score: 40% avg source authority + 30% source diversity (capped at 4 unique sources) + 30% avg relevance score
- Source authority weights: Nature/Science (0.95), arXiv/MIT Tech Review/IEEE (0.85-0.9), TechCrunch (0.8), VentureBeat/Ars Technica (0.75), Hacker News/The Verge (0.7), default (0.5)
- Items with no matching articles: baseline `signal_strength=0.2, source_count=0`

### 5.4 Supplementary Features

**Deep Dive** (`deep_dive.py`):
- 3 stages: (1) DDG search with 3 targeted queries, (2) extract full text from top 15 articles (semaphore=5), (3) LLM analysis
- Model: `GPU_SENSING_REPORT_LLM`
- Schema: `DeepDiveReport` — comprehensive_analysis (500-1000 words), technical_architecture (200-400 words), competitive_landscape (3-6 `CompetitorEntry`), adoption_roadmap (200-300 words), risk_assessment (150-300 words), key_resources (5-10 items), recommendations (3-5)

**Report Comparison** (`comparison.py`):
- No LLM — pure diffing logic
- Compares radar items: added, removed, moved (ring changed), unchanged
- Compares trends: new, removed, continuing
- Compares market signals: new vs removed company names
- Sort priority: moved > added > removed > unchanged

**Collaboration** (`collaboration.py`):
- File-based storage at `data/shared_reports/{share_id}.json`
- Share: creates 8-char UUID share_id linked to report tracking_id
- Vote: user votes on suggested ring for a radar item (with reasoning)
- Comment: user comments on a specific radar item or on the report generally
- Feedback aggregation: per-item ring vote counts, all comments, totals

**Timeline** (`timeline.py`):
- Scans all `report_*.json` for a user, optionally filtered by domain
- Builds per-technology chronological entries: report_date, report_id, ring, quadrant
- Sorted by number of appearances (most tracked technologies first)

**Scheduler** (`scheduler.py`):
- Asyncio background loop checking every 60 seconds
- Frequencies: daily, weekly, biweekly, monthly
- Persisted to `data/sensing_schedules.json`
- On due: runs `run_sensing_pipeline()`, saves report, sends email digest (if SMTP configured), emits Socket.IO event
- CRUD: add_schedule, remove_schedule, update_schedule, list_schedules

**Org Context** (`org_context.py`):
- Stores `OrgTechContext` (tech_stack, industry, priorities) at `data/{user_id}/sensing/org_context.json`
- Generates prompt string injected into report generation: "ORGANIZATIONAL CONTEXT: The reader's organization uses... Tech stack: ... Industry: ... Priorities: ... Tailor recommendations accordingly."

---

## 6. Skill 2: PPTX Generation

### 6.1 Overview

Generates beautiful, branded PowerPoint presentations from any skill's output. Builds on CoPaw's built-in PPTX skill (which provides XML manipulation, LibreOffice conversion, and visual QA) but adds enterprise slide templates and cross-skill data adapters.

### 6.2 SKILL.md

```yaml
---
name: pptx_gen
description: "Generate professional PowerPoint presentations from skill outputs. Converts tech sensing reports, competitive intel, patent analysis, and executive briefs into branded slide decks. Use when the user asks for a presentation, deck, slides, or PPTX."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "presentation"
  requires:
    bins: ["python3", "soffice"]
    env: []
---

# PPTX Generation Skill

## What This Skill Does

Converts structured skill outputs into professional slide decks.

## Available Commands

### Generate from tech sensing report
```bash
python3 scripts/skill_to_slides.py --skill tech_sensing --input "data/{user_id}/sensing/report_{id}.json" --output "output/deck.pptx" --template "executive"
```

### Generate from any JSON input
```bash
python3 scripts/generate_deck.py --input "data/input.json" --schema "tech_sensing|competitive|patent|regulation|talent|brief" --output "output/deck.pptx"
```

### Templates available
- `executive` — C-suite ready, minimal text, high-impact visuals
- `detailed` — Full analysis with data tables and charts
- `briefing` — Quick 5-slide overview
- `custom` — User-provided template PPTX as base

## Slide Structure by Skill

### Tech Sensing -> PPTX
1. Title slide (report_title, domain, date_range)
2. Executive summary (key stats cards)
3. Headline moves (top 5, one per bullet)
4. Technology radar visualization (4-quadrant diagram)
5-7. Key trends (one slide per top 3 trends)
8. Market signals matrix
9. Recommendations (priority-colored cards)
10. Sources and methodology

### Competitive Intel -> PPTX
1. Title + scope
2. Competitive landscape matrix
3-5. Per-competitor deep dive
6. SWOT summary
7. Strategic recommendations

### Executive Brief -> PPTX
1. Title
2. Key findings (cross-skill synthesis)
3. Risk/opportunity matrix
4. Action items
5. Appendix references

## Design System

- Primary colors: Navy (#1B2A4A), Accent (#2E86AB), Success (#28A745), Warning (#FFC107), Danger (#DC3545)
- Font: Calibri (headings 28pt, body 18pt, captions 12pt)
- Layouts: Title, Section Header, Two Column, Full Width, Data Table, Chart
- All slides include: company logo position (top-right), page number (bottom-right), confidentiality footer
```

### 6.3 Implementation Approach

The PPTX skill uses `python-pptx` for programmatic slide generation. Each skill output type has a dedicated adapter:

```python
# skills/pptx_gen/scripts/skill_to_slides.py

"""
Adapter that converts skill JSON outputs into PPTX slide decks.
"""

import argparse
import json
from pathlib import Path

# Adapter registry
ADAPTERS = {
    "tech_sensing": "adapters.sensing_adapter",
    "competitive": "adapters.competitive_adapter",
    "patent": "adapters.patent_adapter",
    "regulation": "adapters.regulation_adapter",
    "talent": "adapters.talent_adapter",
    "brief": "adapters.brief_adapter",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True, choices=ADAPTERS.keys())
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--template", default="executive")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    # Import the appropriate adapter
    adapter_module = __import__(ADAPTERS[args.skill], fromlist=["build_slides"])
    slides = adapter_module.build_slides(data, template=args.template)

    # Generate PPTX
    from pptx_engine import render_pptx
    render_pptx(slides, output_path=args.output, template=args.template)

    print(json.dumps({"status": "success", "output": args.output, "slide_count": len(slides)}))
```

---

## 7. Skill 3: Competitive Intelligence

### 7.1 Overview

Monitors and analyzes the competitive landscape for specified companies, products, or market segments. Reuses the sensing pipeline's ingest infrastructure (DDG, RSS, HN) with competition-focused prompts and schemas.

### 7.2 SKILL.md

```yaml
---
name: competitive_intel
description: "Track and analyze competitors. Monitors news, funding, product launches, partnerships, and strategic moves for specified companies or market segments. Use when the user asks about competitors, competitive landscape, market positioning, or company tracking."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "detective"
  requires:
    bins: ["python3"]
    env: ["MAIN_MODEL", "API_KEY_1"]
---

# Competitive Intelligence Skill

## Available Commands

### Run competitive analysis
```bash
python3 scripts/run_competitive_analysis.py --companies "OpenAI,Anthropic,Google DeepMind,Meta AI" --domain "Foundation Models" --lookback-days 30 --user-id "$USER_ID"
```

### Track a specific company
```bash
python3 scripts/track_company.py --company "Anthropic" --aspects "products,funding,hiring,partnerships" --lookback-days 14 --user-id "$USER_ID"
```

## Output Structure

- **Company Profiles**: For each tracked company — recent news, product launches, funding events, key hires, partnerships
- **Competitive Matrix**: Side-by-side comparison across dimensions (product, market position, funding, team, technology)
- **Strategic Moves**: Significant actions with assessed strategic intent
- **Threat Assessment**: Per-competitor threat level (Critical/High/Medium/Low) with reasoning
- **Opportunity Gaps**: Market gaps identified from competitor weaknesses
- **SWOT Synthesis**: Aggregated strengths/weaknesses/opportunities/threats
```

### 7.3 Pydantic Schemas

```python
# enterprise_skills_lib/llm/output_schemas/competitive.py

class CompanyEvent(BaseModel):
    company: str
    event_type: str        # "product_launch"|"funding"|"partnership"|"acquisition"|"hire"|"regulatory"
    headline: str
    description: str
    date: str
    strategic_intent: str
    source_urls: List[str] = []

class CompetitorProfile(BaseModel):
    company_name: str
    segment: str
    recent_events: List[CompanyEvent]
    products: List[str]
    estimated_market_position: str   # "Leader"|"Challenger"|"Niche"|"Emerging"
    key_strengths: List[str]
    key_weaknesses: List[str]
    threat_level: str               # "Critical"|"High"|"Medium"|"Low"
    threat_reasoning: str

class CompetitiveMatrix(BaseModel):
    dimensions: List[str]           # Column headers
    rows: List[dict]                # {company: str, scores: dict[dimension, str]}

class OpportunityGap(BaseModel):
    gap_name: str
    description: str
    related_competitors: List[str]
    potential_value: str            # "High"|"Medium"|"Low"

class CompetitiveReport(LLMOutputBase):
    report_title: str
    domain: str
    date_range: str
    competitor_profiles: List[CompetitorProfile]
    competitive_matrix: CompetitiveMatrix
    strategic_moves: List[CompanyEvent]
    opportunity_gaps: List[OpportunityGap]
    swot_synthesis: str             # Markdown narrative
    recommendations: List[str]
```

### 7.4 Data Sources

Reuses the sensing ingest infrastructure with competition-focused queries:
- **DuckDuckGo**: `"{company} announcement"`, `"{company} funding round"`, `"{company} product launch"`, `"{company} partnership"`
- **Hacker News**: Algolia search for company name
- **RSS**: General tech feeds (same as sensing) + company-specific blogs if available
- **GitHub**: `"{company}" org:company-name` for open-source activity tracking

---

## 8. Skill 4: Patent Monitor

### 8.1 Overview

Monitors patent filings, grants, and trends in specified technology domains. Uses USPTO and Google Patents APIs.

### 8.2 SKILL.md

```yaml
---
name: patent_monitor
description: "Monitor patent filings, grants, and IP trends. Tracks patent activity by technology domain, assignee (company), or specific patent families. Use when the user asks about patents, IP landscape, patent filings, or intellectual property trends."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "scroll"
  requires:
    bins: ["python3"]
    env: ["MAIN_MODEL"]
---

# Patent Monitor Skill

## Available Commands

### Scan for recent patents
```bash
python3 scripts/run_patent_scan.py --domain "large language models" --assignees "OpenAI,Google,Microsoft" --lookback-days 90 --user-id "$USER_ID"
```

### Analyze a specific patent
```bash
python3 scripts/analyze_patent.py --patent-id "US20240001234A1" --user-id "$USER_ID"
```

## Output Structure

- **Patent Filings**: Recent filings with title, abstract, assignee, filing date, classification codes
- **Assignee Activity**: Filing frequency by company, trend direction
- **Technology Clusters**: Patent groupings by technology area (LLM classification)
- **Key Patents**: Most significant filings with LLM-assessed impact
- **IP Landscape**: Market concentration, white space opportunities
- **Trend Analysis**: Filing velocity trends, emerging areas
```

### 8.3 Data Sources

- **Google Patents Public Datasets**: via BigQuery or the patents search API
- **USPTO PatentsView API**: `https://api.patentsview.org/patents/query` — free, no auth required
- **Lens.org API**: open scholarly and patent search (optional)
- **DuckDuckGo**: supplementary news about patent litigations and IP strategy

### 8.4 Pydantic Schemas

```python
# enterprise_skills_lib/llm/output_schemas/patents.py

class PatentFiling(BaseModel):
    patent_id: str
    title: str
    abstract: str
    assignee: str
    inventors: List[str]
    filing_date: str
    publication_date: str
    classification_codes: List[str]   # CPC/IPC codes
    technology_cluster: str           # LLM-assigned category
    significance_score: float         # 0.0-1.0

class AssigneeActivity(BaseModel):
    company_name: str
    filing_count: int
    trend_direction: str              # "Increasing"|"Stable"|"Decreasing"
    top_technology_areas: List[str]
    notable_patents: List[str]        # patent_ids

class PatentReport(LLMOutputBase):
    report_title: str
    domain: str
    date_range: str
    total_patents_analyzed: int
    key_filings: List[PatentFiling]
    assignee_activity: List[AssigneeActivity]
    technology_clusters: List[dict]   # {cluster_name, count, top_patents}
    ip_landscape_summary: str         # Markdown
    white_space_opportunities: List[str]
    trend_analysis: str               # Markdown
```

---

## 9. Skill 5: Regulation Tracker

### 9.1 Overview

Monitors regulatory developments, policy changes, and compliance requirements across jurisdictions. Critical for enterprises navigating AI governance (EU AI Act, US executive orders, GDPR, etc.).

### 9.2 SKILL.md

```yaml
---
name: regulation_tracker
description: "Track regulatory changes, policy developments, and compliance requirements. Monitors AI regulations (EU AI Act, US AI executive orders), data privacy (GDPR, CCPA), and sector-specific rules. Use when the user asks about regulations, compliance, policy changes, or legal requirements."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "balance_scale"
  requires:
    bins: ["python3"]
    env: ["MAIN_MODEL"]
---

# Regulation Tracker Skill

## Available Commands

### Scan for regulatory changes
```bash
python3 scripts/run_regulation_scan.py --domains "AI governance,data privacy,financial regulation" --jurisdictions "EU,US,UK" --lookback-days 30 --user-id "$USER_ID"
```

### Run impact assessment
```bash
python3 scripts/impact_assessment.py --regulation "EU AI Act" --company-context "We deploy LLM-based customer service agents" --user-id "$USER_ID"
```

## Output Structure

- **Regulatory Updates**: Recent changes with jurisdiction, effective date, summary
- **Compliance Requirements**: Specific obligations extracted from regulatory text
- **Impact Assessment**: Per-regulation impact on specified business context
- **Timeline**: Key compliance deadlines
- **Risk Matrix**: Jurisdiction x regulation type with risk levels
- **Recommended Actions**: Prioritized compliance steps
```

### 9.3 Data Sources

- **Government RSS feeds**: EU EUR-Lex, US Federal Register, UK legislation.gov.uk
- **DuckDuckGo**: `"{regulation} update {year}"`, `"AI regulation {jurisdiction}"`
- **Hacker News**: Policy discussions in tech community
- **Specialized**: IAPP (privacy), AI Policy Observatory (OECD), Stanford HAI policy tracker

### 9.4 Pydantic Schemas

```python
# enterprise_skills_lib/llm/output_schemas/regulations.py

class RegulatoryUpdate(BaseModel):
    regulation_name: str
    jurisdiction: str
    update_type: str              # "New"|"Amendment"|"Enforcement"|"Guidance"|"Proposal"
    effective_date: str
    summary: str
    key_obligations: List[str]
    affected_sectors: List[str]
    source_urls: List[str] = []

class ComplianceDeadline(BaseModel):
    regulation: str
    deadline_date: str
    description: str
    jurisdiction: str
    penalty_for_non_compliance: str

class ImpactAssessment(BaseModel):
    regulation_name: str
    impact_level: str             # "Critical"|"High"|"Medium"|"Low"|"None"
    affected_operations: List[str]
    required_changes: List[str]
    estimated_effort: str         # "Significant"|"Moderate"|"Minor"
    reasoning: str

class RegulationReport(LLMOutputBase):
    report_title: str
    jurisdictions: List[str]
    date_range: str
    regulatory_updates: List[RegulatoryUpdate]
    compliance_deadlines: List[ComplianceDeadline]
    impact_assessments: List[ImpactAssessment]
    risk_matrix_summary: str      # Markdown
    recommended_actions: List[str]
```

---

## 10. Skill 6: Talent Radar

### 10.1 Overview

Monitors the AI/tech talent market — hiring trends, skill demand, key hires, team movements, and salary benchmarks. Helps enterprises plan hiring strategy and identify talent gaps.

### 10.2 SKILL.md

```yaml
---
name: talent_radar
description: "Monitor AI and tech talent market. Tracks hiring trends, key executive moves, skill demand shifts, and talent availability. Use when the user asks about hiring, talent market, skill gaps, team building, or workforce planning."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "busts_in_silhouette"
  requires:
    bins: ["python3"]
    env: ["MAIN_MODEL"]
---

# Talent Radar Skill

## Available Commands

### Run talent market scan
```bash
python3 scripts/run_talent_scan.py --roles "ML Engineer,AI Researcher,LLM Infrastructure" --companies "OpenAI,Anthropic,Google,Meta" --lookback-days 30 --user-id "$USER_ID"
```

### Skill gap analysis
```bash
python3 scripts/skill_gap_analysis.py --current-team-skills "Python,PyTorch,RAG,fine-tuning" --target-capabilities "multi-agent systems,MCP,tool use" --user-id "$USER_ID"
```

## Output Structure

- **Key Moves**: Notable executive/researcher hires and departures
- **Hiring Trends**: Role demand by company, growth/decline direction
- **Skill Demand Shifts**: Emerging skill requirements (e.g., "agent engineering" rising)
- **Talent Availability**: Supply-demand assessment per skill area
- **Salary Benchmarks**: Range estimates by role and seniority (where data available)
- **Skill Gap Analysis**: Current vs. needed capabilities with recommended actions
```

### 10.3 Data Sources

- **DuckDuckGo**: `"{company} hiring AI"`, `"AI engineer job market {year}"`, `"{role} demand trends"`
- **Hacker News**: "Who is hiring" threads, job-related discussions
- **GitHub**: contributor activity on major AI repos (proxy for talent pool)
- **RSS**: Tech hiring blogs, Levels.fyi blog, Blind trending topics

### 10.4 Pydantic Schemas

```python
# enterprise_skills_lib/llm/output_schemas/talent.py

class KeyMove(BaseModel):
    person_name: str
    previous_role: str
    new_role: str
    from_company: str
    to_company: str
    significance: str
    source_urls: List[str] = []

class HiringTrend(BaseModel):
    company: str
    role_category: str
    trend_direction: str          # "Rapidly Growing"|"Growing"|"Stable"|"Declining"
    estimated_openings: str       # "50+"|"10-50"|"<10"|"Unknown"
    notable_requirements: List[str]

class SkillDemand(BaseModel):
    skill_name: str
    demand_trend: str             # "Surging"|"Rising"|"Stable"|"Declining"
    top_requesting_companies: List[str]
    salary_premium: str           # "High"|"Moderate"|"None"

class SkillGap(BaseModel):
    capability: str
    current_coverage: str         # "Strong"|"Partial"|"None"
    market_difficulty: str        # "Hard to find"|"Moderate"|"Easy"
    recommended_action: str       # "Hire"|"Train"|"Contract"|"Partner"

class TalentReport(LLMOutputBase):
    report_title: str
    date_range: str
    key_moves: List[KeyMove]
    hiring_trends: List[HiringTrend]
    skill_demands: List[SkillDemand]
    skill_gaps: List[SkillGap]     # Only populated if skill_gap_analysis requested
    talent_market_summary: str     # Markdown narrative
    recommendations: List[str]
```

---

## 11. Skill 7: Executive Brief Composer

### 11.1 Overview

The synthesis skill. Consumes outputs from all other skills and produces a concise, C-suite-ready one-page brief. This is the most "agentic" skill — it orchestrates inter-agent communication to gather inputs.

### 11.2 SKILL.md

```yaml
---
name: executive_brief
description: "Compose a C-suite executive brief by synthesizing outputs from tech sensing, competitive intel, patent monitoring, regulation tracking, and talent radar. Produces a concise one-page strategic overview. Use when the user asks for an executive summary, strategic brief, C-suite report, or cross-functional synthesis."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "briefcase"
  requires:
    bins: ["python3"]
    env: ["MAIN_MODEL"]
---

# Executive Brief Composer Skill

## What This Skill Does

Synthesizes outputs from multiple skills into a single-page executive brief.

## Available Commands

### Compose brief from existing skill outputs
```bash
python3 scripts/compose_brief.py --user-id "$USER_ID" --domain "Generative AI" --inputs "sensing:report_abc123,competitive:report_def456,patent:report_ghi789"
```

### Cross-skill synthesis (automatic — gathers latest outputs)
```bash
python3 scripts/cross_skill_synthesis.py --user-id "$USER_ID" --domain "Generative AI" --lookback-days 30
```

## Output Structure

1. **Situation** (2-3 sentences): Current state of the domain
2. **Key Findings** (5-7 bullets): Most critical insights across all skills
3. **Risk/Opportunity Matrix**: 2x2 grid (probability x impact)
4. **Competitive Position**: One-line per major competitor
5. **Regulatory Exposure**: Top compliance risks
6. **Talent Implications**: Key hiring/skills message
7. **Recommended Actions**: 3-5 prioritized, time-bound actions
8. **Supporting Data**: References to detailed skill reports

## Multi-Agent Coordination

This skill may request data from the Analyst agent:
```bash
copaw agents chat --from-agent reporter --to-agent analyst --text "Provide latest tech sensing report summary for Generative AI"
copaw agents chat --from-agent reporter --to-agent analyst --text "Provide latest competitive intel for foundation model companies"
```
```

### 11.3 Pydantic Schemas

```python
# enterprise_skills_lib/llm/output_schemas/executive.py

class RiskOpportunity(BaseModel):
    item: str
    type: str                     # "Risk"|"Opportunity"
    probability: str              # "High"|"Medium"|"Low"
    impact: str                   # "High"|"Medium"|"Low"
    source_skill: str             # Which skill identified this

class ActionItem(BaseModel):
    action: str
    priority: str                 # "Immediate"|"Short-term"|"Medium-term"
    owner_suggestion: str         # "CTO"|"VP Engineering"|"Legal"|"HR"|"CEO"
    related_findings: List[str]

class ExecutiveBrief(LLMOutputBase):
    brief_title: str
    domain: str
    date: str
    situation_summary: str        # 2-3 sentences
    key_findings: List[str]       # 5-7 bullets
    risk_opportunity_matrix: List[RiskOpportunity]
    competitive_position: List[dict]   # {competitor, one_line_assessment}
    regulatory_exposure: List[str]
    talent_implications: List[str]
    recommended_actions: List[ActionItem]
    supporting_reports: List[dict]     # {skill, report_id, title, date}
```

---

## 12. Skill 8: Email Digest Composer

### 12.1 Overview

Composes and sends multi-skill email digests on a schedule. Directly reuses the source repo's `email_digest.py` and `scheduler.py`.

### 12.2 SKILL.md

```yaml
---
name: email_digest
description: "Compose and send email digests summarizing outputs from all skills. Supports scheduled recurring digests (daily, weekly, biweekly, monthly). Use when the user asks to set up email alerts, digests, notifications, or scheduled reports."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "envelope"
  requires:
    bins: ["python3"]
    env: ["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"]
---

# Email Digest Composer Skill

## Available Commands

### Send a one-time digest
```bash
python3 scripts/send_digest.py --to "exec-team@company.com" --skills "tech_sensing,competitive_intel" --user-id "$USER_ID" --domain "Generative AI"
```

### Manage subscriptions
```bash
python3 scripts/manage_subscriptions.py --action create --email "cto@company.com" --skills "tech_sensing,competitive_intel,patent_monitor" --frequency weekly --domain "Generative AI" --user-id "$USER_ID"
python3 scripts/manage_subscriptions.py --action list --user-id "$USER_ID"
python3 scripts/manage_subscriptions.py --action delete --subscription-id "$ID"
```

## Email Format

HTML email with:
- Header: company logo, report date, domain badge
- Per-skill section: key stat cards (trend count, radar items, etc.)
- Truncated executive summary (500 chars) per skill
- "View Full Report" link per section
- Footer: unsubscribe link, confidentiality notice
```

### 12.3 SMTP Implementation

Direct reuse of source repo's `core/sensing/email_digest.py`:
- Reads from env: `SMTP_HOST`, `SMTP_PORT` (default 587), `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS`
- Sends HTML+plaintext MIME multipart emails
- HTML template: responsive, mobile-friendly, dark/light mode support

---

## 13. Cross-Skill Data Contracts

### 13.1 Universal Output Envelope

Every skill writes its output in a standardized envelope:

```python
class SkillOutputEnvelope(BaseModel):
    """Universal wrapper for all skill outputs."""
    skill_name: str                    # "tech_sensing", "competitive_intel", etc.
    version: str                       # Skill version
    tracking_id: str                   # UUID for this execution
    user_id: str
    domain: str
    generated_at: str                  # ISO datetime
    execution_time_seconds: float
    status: str                        # "completed"|"partial"|"failed"
    report: dict                       # Skill-specific report (model_dump())
    meta: dict                         # Skill-specific metadata
```

### 13.2 Storage Convention

```
data/{user_id}/{skill_name}/report_{tracking_id}.json    # Report data
data/{user_id}/{skill_name}/status_{tracking_id}.json     # Execution status
```

### 13.3 Inter-Skill Data Flow

```
tech_sensing ──────> executive_brief
competitive_intel ──> executive_brief
patent_monitor ────> executive_brief
regulation_tracker -> executive_brief
talent_radar ──────> executive_brief

Any skill output ──> pptx_gen ──> .pptx file
Any skill output ──> email_digest ──> SMTP
```

The Executive Brief skill reads from `data/{user_id}/{skill_name}/` to find the latest report for each skill. The PPTX skill accepts a `--skill` flag to select the appropriate slide adapter.

---

## 14. Multi-Agent Orchestration Patterns

### 14.1 Agent Roles

| Agent | Skills | Purpose |
|-------|--------|---------|
| **Analyst** | tech_sensing, competitive_intel, patent_monitor, regulation_tracker, talent_radar | Data gathering and analysis |
| **Reporter** | pptx_gen, executive_brief | Synthesis and presentation |
| **Admin** | email_digest | Scheduling and distribution |

### 14.2 Inter-Agent Communication

CoPaw's `multi_agent_collaboration` skill enables CLI-based inter-agent messaging:

```bash
# Reporter asks Analyst for latest sensing report
copaw agents chat --from-agent reporter --to-agent analyst \
  --text "Run tech sensing for Generative AI, last 7 days" \
  --background --task-id "sensing-run-001"

# Poll for completion
copaw agents chat --from-agent reporter --to-agent analyst \
  --text "Check status of task sensing-run-001"

# Admin triggers digest across all skills
copaw agents chat --from-agent admin --to-agent analyst \
  --text "Provide latest report summaries for all skills, user xyz"
```

### 14.3 Orchestration Patterns

**Pattern 1: User-Initiated Single Skill**
```
User -> Channel (Discord/Telegram/CLI) -> CoPaw Agent -> Skill Script -> Library -> LLM -> Result -> User
```

**Pattern 2: Cross-Skill Brief**
```
User: "Give me an executive brief on AI"
  -> Reporter Agent
  -> Reads latest outputs from data/{user_id}/*/
  -> If outputs are stale (>7 days), requests fresh runs from Analyst Agent
  -> Synthesizes via executive_brief skill
  -> Returns brief to user
```

**Pattern 3: Scheduled Pipeline**
```
Scheduler (background loop) -> triggers Analyst Agent for each scheduled skill
  -> Analyst runs pipeline, saves output
  -> Admin Agent picks up new outputs, composes digest email
  -> Sends via SMTP
```

### 14.4 CoPaw Multi-Agent Manager Configuration

```python
# CoPaw's MultiAgentManager handles:
# - Lazy loading: Agents created on first request
# - Hot-reload: Config changes trigger graceful agent restart
# - Concurrent startup: All enabled agents start in parallel
# - Background tasks: Old instances with active tasks get delayed cleanup

# Each agent is a Workspace with:
# - Its own model configuration (provider + model ID)
# - Its own skills directory
# - Its own memory manager
# - Its own MCP clients
```

---

## 15. Source Repository Code Reuse Map

### 15.1 Direct Copy (adapt imports only)

These files are copied directly into `enterprise_skills_lib/` with minimal changes (update import paths from `core.*` to `enterprise_skills_lib.*`):

| Source File | Target File | Lines | Changes |
|-------------|-------------|-------|---------|
| `core/sensing/pipeline.py` | `enterprise_skills_lib/sensing/pipeline.py` | 333 | Update imports |
| `core/sensing/ingest.py` | `enterprise_skills_lib/sensing/ingest.py` | 179 | Update imports |
| `core/sensing/sources/arxiv_search.py` | `enterprise_skills_lib/sensing/sources/arxiv_search.py` | ~80 | Update imports |
| `core/sensing/sources/github_trending.py` | `enterprise_skills_lib/sensing/sources/github_trending.py` | ~70 | Update imports |
| `core/sensing/sources/hackernews.py` | `enterprise_skills_lib/sensing/sources/hackernews.py` | ~65 | Update imports |
| `core/sensing/dedup.py` | `enterprise_skills_lib/sensing/dedup.py` | ~80 | Update imports |
| `core/sensing/classify.py` | `enterprise_skills_lib/sensing/classify.py` | 117 | Update imports |
| `core/sensing/cache.py` | `enterprise_skills_lib/sensing/cache.py` | 106 | Update imports |
| `core/sensing/report_generator.py` | `enterprise_skills_lib/sensing/report_generator.py` | 165 | Update imports |
| `core/sensing/verifier.py` | `enterprise_skills_lib/sensing/verifier.py` | ~90 | Update imports |
| `core/sensing/signal_score.py` | `enterprise_skills_lib/sensing/signal_score.py` | ~70 | Update imports |
| `core/sensing/movement.py` | `enterprise_skills_lib/sensing/movement.py` | 121 | Update imports |
| `core/sensing/deep_dive.py` | `enterprise_skills_lib/sensing/deep_dive.py` | 161 | Update imports |
| `core/sensing/comparison.py` | `enterprise_skills_lib/sensing/comparison.py` | 167 | Update imports |
| `core/sensing/collaboration.py` | `enterprise_skills_lib/sensing/collaboration.py` | 177 | Update imports |
| `core/sensing/org_context.py` | `enterprise_skills_lib/sensing/org_context.py` | ~60 | Update imports |
| `core/sensing/timeline.py` | `enterprise_skills_lib/sensing/timeline.py` | ~80 | Update imports |
| `core/sensing/scheduler.py` | `enterprise_skills_lib/sensing/scheduler.py` | 243 | Update imports |
| `core/sensing/email_digest.py` | `enterprise_skills_lib/sensing/email_digest.py` | ~80 | Update imports |
| `core/sensing/config.py` | `enterprise_skills_lib/sensing/config.py` | 117 | Update imports |
| `core/llm/output_schemas/sensing_outputs.py` | `enterprise_skills_lib/llm/output_schemas/sensing.py` | 319 | Update imports |
| `core/llm/output_schemas/base.py` | `enterprise_skills_lib/llm/output_schemas/base.py` | 85 | Update imports |
| `core/llm/prompts/sensing_prompts.py` | `enterprise_skills_lib/llm/prompts/sensing_prompts.py` | ~200 | Update imports |
| `core/utils/llm_output_sanitizer.py` | `enterprise_skills_lib/llm/output_sanitizer.py` | ~200 | Update imports |

### 15.2 Significant Adaptation (refactor for library use)

| Source File | Target File | Changes |
|-------------|-------------|---------|
| `core/llm/client.py` | `enterprise_skills_lib/llm/client.py` | Remove LangChain `MyServerLLM` dependency. Replace with direct `httpx`/`openai` calls to vLLM. Keep all retry, fallback, self-correction, parse pipeline logic intact. Remove `contextvars` sticky fallback if not running in async server context. |
| `core/config.py` | `enterprise_skills_lib/config.py` | Simplify to only the fields needed (remove MongoDB, auth, document parsing settings). Keep all LLM/API key fields. |
| `core/constants.py` | `enterprise_skills_lib/constants.py` | Keep `SWITCHES`, `GPULLMConfig`, `GPU_SENSING_*` configs, model constants. Remove graph node names, document parsing constants. |

### 15.3 New Code (must be written)

| File | Purpose |
|------|---------|
| `enterprise_skills_lib/copaw_provider.py` | FallbackProvider + FallbackChatModel |
| `enterprise_skills_lib/llm/output_schemas/competitive.py` | Competitive intel Pydantic models |
| `enterprise_skills_lib/llm/output_schemas/patents.py` | Patent monitor Pydantic models |
| `enterprise_skills_lib/llm/output_schemas/regulations.py` | Regulation tracker Pydantic models |
| `enterprise_skills_lib/llm/output_schemas/talent.py` | Talent radar Pydantic models |
| `enterprise_skills_lib/llm/output_schemas/executive.py` | Executive brief Pydantic models |
| `enterprise_skills_lib/llm/prompts/competitive_prompts.py` | Competitive intel prompt templates |
| `enterprise_skills_lib/llm/prompts/patent_prompts.py` | Patent monitor prompt templates |
| `enterprise_skills_lib/llm/prompts/regulation_prompts.py` | Regulation tracker prompt templates |
| `enterprise_skills_lib/llm/prompts/talent_prompts.py` | Talent radar prompt templates |
| `enterprise_skills_lib/llm/prompts/executive_prompts.py` | Executive brief prompt templates |
| All `skills/*/SKILL.md` files | Skill definitions |
| All `skills/*/scripts/*.py` files | CLI entry points for each skill |

### 15.4 Dependencies

```toml
# pyproject.toml [project.dependencies]

# CoPaw framework
copaw = ">=1.0.0"

# LLM clients
openai = ">=1.30.0"           # OpenAI API + vLLM (OpenAI-compatible)
google-genai = ">=1.0.0"      # Gemini API (google.genai)

# Data ingestion
feedparser = ">=6.0.0"        # RSS/Atom parsing
trafilatura = ">=1.6.0"       # Web page text extraction
duckduckgo-search = ">=6.0.0" # DDG web search
httpx = ">=0.27.0"            # Async HTTP client

# Structured output
pydantic = ">=2.0.0"
pydantic-settings = ">=2.0.0"
json-repair = ">=0.28.0"      # Malformed JSON repair

# Async
aiofiles = ">=23.0.0"         # Async file I/O

# PPTX
python-pptx = ">=0.6.23"      # Programmatic PPTX generation

# Utilities
difflib                        # stdlib (fuzzy matching)
```

---

## 16. Pydantic Schema Reference

### 16.1 Base Class

All LLM output schemas extend `LLMOutputBase`:

```python
class LLMOutputBase(BaseModel):
    """
    Auto-sanitizes all string fields:
    1. @field_validator("*", mode="before"): replaces Unicode whitespace,
       removes zero-width chars in strings and string lists
    2. @model_validator(mode="after"): recursively applies normalize_answer_content()
       to all string fields (fixes double-escaped newlines, quotes, tabs)
    """
```

### 16.2 Tech Sensing Schemas (complete field reference)

**ClassifiedArticle(BaseModel):**
- `title: str`, `source: str`, `url: str`, `published_date: str`
- `summary: str` — 2-3 sentence summary
- `relevance_score: float` — 0.0-1.0
- `quadrant: str` — "Techniques"|"Platforms"|"Tools"|"Languages & Frameworks"
- `ring: str` — "Adopt"|"Trial"|"Assess"|"Hold"
- `technology_name: str` — Short label for radar blip
- `reasoning: str`
- `topic_category: str = ""` — Foundation Models & Agents | Safety & Governance | Infrastructure & Tooling | Applications & Industry | Research & Breakthroughs
- `industry_segment: str = ""` — Frontier Labs | Big Tech Platforms | Enterprise & B2B | Open Source & Community | Startups & VC

**TrendItem(BaseModel):**
- `trend_name: str`, `description: str`, `evidence: List[str]`
- `impact_level: str` — High|Medium|Low
- `time_horizon: str` — Immediate|Near-term|Medium-term|Long-term
- `source_urls: List[str] = []`

**RadarItem(BaseModel):**
- `name: str`, `quadrant: str`, `ring: str`, `description: str`
- `is_new: bool`, `moved_in: Optional[str] = None`
- `signal_strength: float = 0.0`, `source_count: int = 0`

**RadarItemDetail(BaseModel):**
- `technology_name: str`, `what_it_is: str`, `why_it_matters: str`
- `current_state: str`, `key_players: List[str]`, `practical_applications: List[str]`
- `source_urls: List[str] = []`

**HeadlineMove(BaseModel):**
- `headline: str`, `actor: str`, `segment: str`, `source_urls: List[str] = []`

**MarketSignal(BaseModel):**
- `company_or_player: str`, `signal: str`, `strategic_intent: str`
- `industry_impact: str`, `segment: str = ""`
- `related_technologies: List[str]`, `source_urls: List[str] = []`

**ReportSection(BaseModel):**
- `section_title: str`, `content: str`, `source_urls: List[str] = []`

**Recommendation(BaseModel):**
- `title: str`, `description: str`
- `priority: str` — Critical|High|Medium|Low
- `related_trends: List[str]`

**TechSensingReportSkeleton(LLMOutputBase):**
- `report_title: str`, `executive_summary: str`, `domain: str`, `date_range: str`
- `total_articles_analyzed: int`
- `headline_moves: List[HeadlineMove]`
- `key_trends: List[TrendItem]`
- `report_sections: List[ReportSection]`
- `radar_items: List[RadarItem]`
- `market_signals: List[MarketSignal]`
- `recommendations: List[Recommendation]`
- `notable_articles: List[ClassifiedArticle]`

**RadarDetailsOutput(LLMOutputBase):**
- `radar_item_details: List[RadarItemDetail]`

**TechSensingReport(LLMOutputBase):**
- All fields from `TechSensingReportSkeleton` + `radar_item_details: List[RadarItemDetail]`

**DeepDiveReport(LLMOutputBase):**
- `technology_name: str`
- `comprehensive_analysis: str` — 500-1000 words markdown
- `technical_architecture: str` — 200-400 words
- `competitive_landscape: List[CompetitorEntry]` — 3-6 items (name, approach, strengths, weaknesses)
- `adoption_roadmap: str` — 200-300 words
- `risk_assessment: str` — 150-300 words
- `key_resources: List[KeyResource]` — 5-10 items (title, url, type: paper|repo|article|docs)
- `recommendations: List[str]` — 3-5 items

**VerifiedItems(LLMOutputBase):**
- `relevant_radar_items: List[str]`
- `relevant_market_signals: List[str]`
- `relevant_trends: List[str]`
- `attribution_warnings: List[str] = []` — Format: `"tech_name: entity_to_remove | reason"`

---

## 17. LLM Prompt Engineering Reference

### 17.1 Prompt Structure Convention

All prompts follow the 2-message chat format:
```python
[
    {"role": "system", "parts": [{"text": system_prompt}]},
    {"role": "user", "parts": [{"text": user_prompt}]},
]
```

`invoke_llm()` serializes these to a flat string with `[SYSTEM]` and `[USER]` headers, then wraps with schema injection.

### 17.2 Classification Prompt Structure

```
SYSTEM: You are a senior technology analyst. Classify each article:
- summary (2-3 sentences)
- relevance_score (0.0-1.0)
- quadrant (Techniques|Platforms|Tools|Languages & Frameworks)
- ring (Adopt|Trial|Assess|Hold)
- technology_name (short label)
- topic_category (5 categories defined)
- industry_segment (5 segments defined)
[Optional: KEY PEOPLE WATCHLIST block — boosts relevance +0.1]
Output: JSON with "articles" array. Filter relevance < 0.3.

USER: ARTICLES TO CLASSIFY:
--- Article 1 ---
Title: ...
Source: ...
URL: ...
Date: ...
Content: {content[:2000]}
...
```

### 17.3 Report Skeleton Prompt Structure

```
SYSTEM: You are a senior technology strategist. Create a weekly Tech Sensing Report.
Requirements:
- Top 10 headline moves
- 5-10 trends with evidence and time horizons
- 15-30 radar items across 4 quadrants and 4 rings
- 5-10 market signals with strategic intent
- 3-6 deep-dive report sections
- Recommendations prioritized Critical/High/Medium/Low
- 5-10 notable articles
Grounding: MUST use article source_urls. No fabricated URLs.
Attribution: Distinguish research authors from implementation authors.
[Optional: ORGANIZATIONAL CONTEXT block]
[Optional: CUSTOM REQUIREMENTS block]
Output: JSON object with specific top-level keys (NO radar_item_details).

USER: DATE RANGE: {date_range}
DOMAIN: {domain}
CLASSIFIED ARTICLES:
{classified_articles_json}
```

### 17.4 Radar Details Prompt Structure

```
SYSTEM: Generate detailed write-ups for each radar item:
- what_it_is, why_it_matters, current_state
- key_players, practical_applications, source_urls
Attribution and grounding rules.
Output: JSON with "radar_item_details" array.

USER: RADAR ITEMS:
{radar_items_json}
CLASSIFIED ARTICLES:
{classified_articles_json}
```

### 17.5 Prompt Best Practices (from production experience)

1. **Always inject the Pydantic schema** via `PydanticOutputParser.get_format_instructions()` — the LLM needs the exact field names and types
2. **Add explicit "CRITICAL OUTPUT RULES"** at the end: no markdown fences, no schema echo, exact JSON object
3. **Content excerpts improve grounding** — include 800-char content snippets per article in report generation
4. **Self-correction works** — when a parse fails, injecting the failed output + error into the next prompt fixes it ~80% of the time
5. **Batch size of 6** is optimal for classification — larger batches cause quality degradation on smaller models
6. **Temperature 0.2** for all structured output tasks (report generation, classification, verification)

---

## 18. Data Storage & Persistence

### 18.1 File-Based Storage Layout

```
data/
|-- sensing_cache/                    # Classification cache
|   |-- {url_hash_16}.json           # {cached_at, article: ClassifiedArticle.model_dump()}
|
|-- sensing_schedules.json            # All schedules (global file)
|
|-- shared_reports/                   # Collaboration
|   |-- {share_id_8}.json           # SharedReport with votes + comments
|
|-- {user_id}/
|   |-- sensing/
|   |   |-- org_context.json         # OrgTechContext
|   |   |-- report_{tracking_id}.json # {report: TechSensingReport.model_dump(), meta: {...}}
|   |   |-- status_{tracking_id}.json # {status, started_at, completed_at, error}
|   |   |-- deepdive_{tracking_id}.json
|   |   |-- deepdive_status_{tracking_id}.json
|   |-- competitive/
|   |   |-- report_{tracking_id}.json
|   |   |-- status_{tracking_id}.json
|   |-- patents/
|   |   |-- report_{tracking_id}.json
|   |   |-- status_{tracking_id}.json
|   |-- regulations/
|   |   |-- report_{tracking_id}.json
|   |   |-- status_{tracking_id}.json
|   |-- talent/
|   |   |-- report_{tracking_id}.json
|   |   |-- status_{tracking_id}.json
|   |-- briefs/
|   |   |-- brief_{tracking_id}.json
|   |   |-- status_{tracking_id}.json
```

### 18.2 Cache Strategy

| Cache | Location | TTL | Key | Purpose |
|-------|----------|-----|-----|---------|
| Classification | `data/sensing_cache/{hash}.json` | 30 days | SHA-256(url)[:16] | Avoid re-classifying known articles |
| LLM instances | In-memory dict | Session | `(model, port)` | Reuse model connections |
| API keys | In-memory cycle | Session | Round-robin index | Gemini key rotation |

### 18.3 Status File Convention

Every async operation writes a status file for polling:

```json
{
  "status": "pending|running|completed|failed",
  "started_at": "2026-04-01T10:00:00Z",
  "completed_at": "2026-04-01T10:02:30Z",
  "progress": 85,
  "stage": "report",
  "message": "Generating report with LLM...",
  "error": null
}
```

---

## 19. API & Real-Time Communication

### 19.1 REST API (Optional Layer)

If deploying with a web frontend, add a FastAPI layer wrapping the skill scripts:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/skills/{skill_name}/run` | Trigger async skill execution |
| GET | `/skills/{skill_name}/status/{tracking_id}` | Poll execution status |
| GET | `/skills/{skill_name}/history` | List past reports for user |
| DELETE | `/skills/{skill_name}/report/{id}` | Delete a report |
| POST | `/schedules` | Create recurring schedule |
| GET | `/schedules` | List user's schedules |
| PUT | `/schedules/{id}` | Update schedule |
| DELETE | `/schedules/{id}` | Delete schedule |
| GET | `/timeline` | Cross-report technology timeline |
| GET | `/org-context` | Get org tech context |
| PUT | `/org-context` | Update org tech context |
| POST | `/share/{report_id}` | Create shared report link |
| GET | `/shared/{share_id}` | Load shared report |
| POST | `/shared/{share_id}/vote` | Vote on radar item ring |
| POST | `/shared/{share_id}/comment` | Comment on report |
| GET | `/shared/{share_id}/feedback` | Get all feedback |
| POST | `/brief/compose` | Trigger executive brief |
| POST | `/pptx/generate` | Generate PPTX from skill output |
| POST | `/digest/send` | Send one-time email digest |

### 19.2 Socket.IO Events (for real-time progress)

Event pattern: `{user_id}/{skill_name}_progress`

Payload:
```json
{
  "tracking_id": "uuid",
  "stage": "ingest|dedup|extract|classify|report|verify|movement|complete|error",
  "progress": 0-100,
  "message": "Human-readable status..."
}
```

### 19.3 Authentication

- JWT-based (HS256) via `SECRET_KEY`
- Socket.IO: validate JWT from `auth.token` in connect handler
- REST: validate via middleware on `request.state.user`
- Stale timeout: 60 minutes for sensing operations (overrides default 8-minute timeout)

---

## 20. Configuration & Environment

### 20.1 CoPaw Configuration (`~/.copaw/config.json`)

```json
{
  "agents": [
    {
      "id": "analyst",
      "name": "Enterprise Analyst",
      "provider_id": "fallback",
      "model_id": "gpt-oss-20b",
      "skills": {
        "tech_sensing": {"enabled": true},
        "competitive_intel": {"enabled": true},
        "patent_monitor": {"enabled": true},
        "regulation_tracker": {"enabled": true},
        "talent_radar": {"enabled": true}
      }
    },
    {
      "id": "reporter",
      "name": "Report Generator",
      "provider_id": "fallback",
      "model_id": "gpt-oss-20b",
      "skills": {
        "pptx_gen": {"enabled": true},
        "executive_brief": {"enabled": true}
      }
    },
    {
      "id": "admin",
      "name": "Platform Admin",
      "provider_id": "fallback",
      "model_id": "gpt-oss-20b",
      "skills": {
        "email_digest": {"enabled": true}
      }
    }
  ],
  "mcp": {
    "clients": []
  },
  "channels": {
    "console": {"enabled": true},
    "discord": {"enabled": false, "token": ""},
    "telegram": {"enabled": false, "token": ""},
    "slack": {"enabled": false, "token": ""}
  }
}
```

### 20.2 Feature Switches

```python
# enterprise_skills_lib/constants.py

SWITCHES = {
    # LLM fallback chain
    "FALLBACK_TO_GEMINI": True,
    "FALLBACK_TO_OPENAI": True,
    "USE_INTERNAL": False,
    "REMOTE_GPU": False,
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
```

### 20.3 GPU Model Configurations

```python
# All sensing skills share these configs
GPU_SENSING_CLASSIFY_LLM = GPULLMConfig(model=settings.MAIN_MODEL, port=PORT1)
GPU_SENSING_REPORT_LLM = GPULLMConfig(model=settings.MAIN_MODEL, port=PORT1)

# Additional skills can use the same or different models
GPU_COMPETITIVE_LLM = GPULLMConfig(model=settings.MAIN_MODEL, port=PORT1)
GPU_PATENT_LLM = GPULLMConfig(model=settings.MAIN_MODEL, port=PORT1)
GPU_REGULATION_LLM = GPULLMConfig(model=settings.MAIN_MODEL, port=PORT1)
GPU_TALENT_LLM = GPULLMConfig(model=settings.MAIN_MODEL, port=PORT1)
GPU_EXECUTIVE_LLM = GPULLMConfig(model=settings.MAIN_MODEL, port=PORT1)

PORT1 = 11434  # Primary GPU server port
```

---

## 21. Testing Strategy

### 21.1 Test Structure

```
tests/
|-- unit/
|   |-- test_dedup.py              # URL normalization, fuzzy matching
|   |-- test_classify.py           # Batch formatting, cache hits
|   |-- test_signal_score.py       # Authority weights, composite scoring
|   |-- test_comparison.py         # Report diffing logic
|   |-- test_movement.py           # Ring change detection
|   |-- test_collaboration.py      # Share, vote, comment CRUD
|   |-- test_timeline.py           # Timeline aggregation
|   |-- test_output_sanitizer.py   # JSON sanitization pipeline
|   |-- test_schemas.py            # Pydantic model validation
|   |-- test_config.py             # Settings loading
|-- integration/
|   |-- test_ingest.py             # Live RSS/DDG/arXiv/GitHub/HN fetches
|   |-- test_invoke_llm.py         # Full fallback chain (requires GPU or API keys)
|   |-- test_pipeline.py           # End-to-end sensing pipeline
|   |-- test_provider.py           # FallbackProvider with CoPaw
|-- conftest.py                    # Shared fixtures
```

### 21.2 Test Fixtures

```python
# tests/conftest.py

import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_invoke_llm():
    """Mock invoke_llm to return predefined structured outputs."""
    with patch("enterprise_skills_lib.llm.client.invoke_llm") as mock:
        mock.return_value = {...}  # Schema-valid dict
        yield mock

@pytest.fixture
def sample_raw_articles():
    """10 diverse RawArticle instances for testing."""
    return [RawArticle(title=f"Article {i}", url=f"https://example.com/{i}", source="Test") for i in range(10)]

@pytest.fixture
def sample_classified_articles():
    """10 ClassifiedArticle instances with varied quadrants/rings."""
    ...

@pytest.fixture
def sample_report():
    """Complete TechSensingReport for testing comparison, movement, timeline."""
    ...
```

### 21.3 Testing Guidelines

- **Unit tests**: No network, no LLM, no disk I/O. Mock everything external.
- **Integration tests**: Require at least one LLM backend (GPU or API keys). Mark with `@pytest.mark.integration`.
- **Coverage target**: 75% on `enterprise_skills_lib/`.
- **Async**: Use `pytest-asyncio` with `asyncio_mode = "auto"`.

---

## 22. Deployment & Security

### 22.1 Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-impress \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY pyproject.toml .
RUN pip install -e .

# Application code
COPY enterprise_skills_lib/ enterprise_skills_lib/
COPY skills/ skills/
COPY copaw_config/ copaw_config/
COPY api/ api/

# CoPaw setup
RUN copaw init
COPY copaw_config/config.json ~/.copaw/config.json

# Install skills
RUN for skill_dir in skills/*/; do \
      copaw skill install "$skill_dir"; \
    done

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 22.2 Docker Compose

```yaml
version: "3.8"
services:
  platform:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./data:/app/data
    depends_on:
      - vllm

  vllm:
    image: vllm/vllm-openai:latest
    ports:
      - "11434:8000"
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
    command: >
      --model gpt-oss-20b
      --dtype bfloat16
      --gpu-memory-utilization 0.82
      --max-model-len 8192
      --trust-remote-code
```

### 22.3 Security Considerations

1. **API keys never in skill scripts** — all keys in `.env`, accessed via `enterprise_skills_lib/config.py`
2. **Provider key masking** — CoPaw's `ProviderInfo.get_info()` masks API keys in responses
3. **Skill security scanning** — CoPaw's `skills_manager.py` includes security scanning on skill install
4. **File path traversal** — validate all user-provided paths resolve within `data/` directory
5. **SMTP credentials** — stored in `.env`, never logged
6. **JWT validation** — on every Socket.IO connect and REST request
7. **Rate limiting** — `invoke_llm` has built-in rate limiter (3 calls/min for INTERNAL API)

---

## 23. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

1. **Set up repository structure** — Create `copaw-enterprise-skills/` with directory layout from Section 2.2
2. **Extract `enterprise_skills_lib/`** — Copy all source repo files per the reuse map (Section 15.1), update imports
3. **Adapt `invoke_llm()`** — Remove LangChain dependency, use direct httpx/openai for GPU calls, keep all fallback/retry/parse logic
4. **Implement `FallbackProvider`** — Wire into CoPaw's provider system
5. **Verify**: `invoke_llm()` works standalone with a simple schema test

### Phase 2: Tech Sensing Skill (Week 2-3)

1. **Write `skills/tech_sensing/SKILL.md`** — Per Section 5.2
2. **Write all CLI scripts** in `skills/tech_sensing/scripts/`
3. **Test end-to-end**: CoPaw agent can run tech sensing via natural language command
4. **Port scheduler** for recurring sensing reports
5. **Port collaboration features** (share, vote, comment)

### Phase 3: PPTX Generation (Week 3-4)

1. **Build on CoPaw's built-in PPTX skill** — extend with enterprise templates
2. **Write sensing-to-slides adapter**
3. **Write design system** (colors, fonts, layouts)
4. **Test**: Generate a complete deck from a sensing report

### Phase 4: Remaining Skills (Week 4-7)

1. **Competitive Intelligence** — New schemas + prompts, reuse ingest infrastructure
2. **Patent Monitor** — New data sources (USPTO, Google Patents), new schemas
3. **Regulation Tracker** — New data sources (government feeds), new schemas
4. **Talent Radar** — New data sources, new schemas
5. Each skill follows the same pattern: `SKILL.md` + `scripts/` + library schemas/prompts

### Phase 5: Cross-Skill Integration (Week 7-8)

1. **Executive Brief** — Cross-skill synthesis, multi-agent coordination
2. **Email Digest** — Multi-skill digest composition, subscription management
3. **PPTX adapters** for all remaining skills
4. **Inter-agent communication testing** — Analyst <-> Reporter <-> Admin flows

### Phase 6: Polish & Deploy (Week 8-9)

1. **REST API layer** (if needed for web frontend)
2. **Socket.IO integration** for real-time progress
3. **Docker packaging**
4. **Channel configuration** (Discord, Telegram, Slack)
5. **Documentation and user guides**
6. **Load testing** — ensure scheduler handles concurrent skill runs

---

## Appendix A: Quick Start for New Instance

If you are a Claude Code instance receiving this specification in a new repository:

1. **Read this entire document first** — it is your ground truth
2. **Start with Phase 1** — set up the directory structure and extract the library
3. **The source repo is at**: `c:\Users\pranaldongare\Projects\Multi-Modal-Enterprise-Knowledge-Synthesis-Platform`
4. **Copy files per Section 15.1** — update imports from `core.*` to `enterprise_skills_lib.*`
5. **The most critical file to get right** is `enterprise_skills_lib/llm/client.py` — this is the `invoke_llm()` function with the full GPU->Gemini->OpenAI fallback chain, 4-retry self-correction, and 3-strategy JSON parse pipeline. See Section 4.2 for the complete behavior specification.
6. **Install CoPaw**: `pip install copaw && copaw init`
7. **Test the FallbackProvider first** before building any skills
8. **Each skill is a directory with `SKILL.md`** — CoPaw discovers them by filesystem scanning, NOT Python imports

## Appendix B: Known Gotchas from Source Repo

1. **`json_repair` library** is essential — LLMs frequently produce malformed JSON. The 3-strategy parse pipeline handles this, but `json_repair` is the last-resort strategy.
2. **Gemini 6-key rotation** is needed because individual API keys get rate-limited. The round-robin with `asyncio.Lock` prevents key starvation.
3. **Self-correction prompt injection** must truncate failed output to 2000 chars — otherwise the context gets too long and the LLM loses focus.
4. **`_check_empty_lists()`** is critical — without it, LLMs sometimes return valid JSON with all empty arrays `[]`, which passes Pydantic validation but is useless.
5. **Unicode sanitization** in `LLMOutputBase` catches a real production issue — local models (especially via vLLM) emit non-breaking spaces and zero-width characters that break downstream rendering.
6. **Classification cache** saves significant time and cost — articles that appeared in last week's report don't need re-classification.
7. **Content excerpts in report prompts** dramatically improve grounding — without them, the LLM fabricates technology details.
8. **Attribution warnings in verifier** catch a specific failure mode where the LLM attributes a technology to the wrong company (e.g., saying Google created GPT-4).
9. **Scheduler uses `asyncio.create_task()`** not `BackgroundTasks` — this matters for CoPaw integration since CoPaw runs its own event loop.
10. **Stale timeout is 60 minutes** for sensing operations, not the default 8 minutes — full pipeline runs can take 5-15 minutes depending on article count and LLM response times.
