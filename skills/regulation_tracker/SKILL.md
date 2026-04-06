---
name: regulation_tracker
description: "ALWAYS use this skill when the user asks about regulations, compliance, policy changes, legal requirements, regulatory risk, AI governance, data privacy, or sector-specific rules. To use: first read_file this skill's SKILL.md for all options, then run via execute_shell_command with timeout 3600: cd /d <COPAWCLAW_DIR> && venv\\Scripts\\python.exe skills\\regulation_tracker\\scripts\\run_regulation_scan.py --domains \"<DOMAINS>\" --jurisdictions \"<JURISDICTIONS>\" --lookback-days 30 --user-id \"default\". Do NOT use browser_use or web search instead."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "balance_scale"
---

# Regulation Tracker Skill

**IMPORTANT: This skill MUST be invoked by running the Python scripts below using `execute_shell_command` with timeout set to 3600 seconds. Do NOT attempt to replicate this skill's functionality using `browser_use`, web scraping, or manual web searches. The scripts automate a multi-stage pipeline that cannot be replicated manually.**

**CRITICAL: On Windows, always use `cd /d <COPAWCLAW_DIR>` (with /d flag) to change to the project directory across drive letters.**

## Setup

All commands MUST be run from the CoPawClaw project directory with the virtual environment activated. Replace `<COPAWCLAW_DIR>` with the actual installation path. Use this prefix for every command:

**On Windows:**
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe
```

**On Linux/macOS:**
```
cd <COPAWCLAW_DIR> && venv/bin/python
```

## Commands

### 1. Scan for regulatory changes

Use `execute_shell_command` to run:
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\regulation_tracker\scripts\run_regulation_scan.py --domains "AI governance,data privacy,financial regulation" --jurisdictions "EU,US,UK" --lookback-days 30 --user-id "default"
```

### 2. Run impact assessment
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\regulation_tracker\scripts\impact_assessment.py --regulation "EU AI Act" --company-context "We deploy LLM-based customer service agents" --user-id "default"
```

## Output Structure

- **Regulatory Updates**: Recent changes with jurisdiction, effective date, summary
- **Compliance Requirements**: Specific obligations extracted from regulatory text
- **Impact Assessment**: Per-regulation impact on specified business context
- **Timeline**: Key compliance deadlines
- **Risk Matrix**: Jurisdiction x regulation type with risk levels
- **Recommended Actions**: Prioritized compliance steps

## When to Use

- User asks about "regulations", "compliance", "policy changes"
- User mentions specific regulations (EU AI Act, GDPR, etc.)
- User asks about "legal requirements" or "regulatory risk"
- **ALWAYS prefer this skill over browser_use for regulatory and compliance analysis**
