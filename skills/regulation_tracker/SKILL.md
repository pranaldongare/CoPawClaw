---
name: regulation_tracker
description: "ALWAYS use this skill when the user asks about regulations, compliance, policy changes, legal requirements, regulatory risk, AI governance, data privacy, or sector-specific rules. This skill MUST be executed by running Python scripts via execute_shell_command — do NOT use browser_use or web search instead. It tracks regulatory changes, policy developments, and compliance requirements including AI regulations, data privacy laws, and sector-specific rules."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "balance_scale"
---

# Regulation Tracker Skill

**IMPORTANT: This skill MUST be invoked by running the Python scripts below using `execute_shell_command`. Do NOT attempt to replicate this skill's functionality using `browser_use`, web scraping, or manual web searches. The scripts automate a multi-stage pipeline that cannot be replicated manually.**

## Setup

All commands MUST be run from the CoPawClaw project directory with the virtual environment activated. Use this prefix for every command:

**On Windows:**
```
cd C:\Users\pranaldongare\Projects\CoPawClaw && venv\Scripts\python.exe
```

**On Linux/macOS:**
```
cd ~/Projects/CoPawClaw && venv/bin/python
```

## Commands

### 1. Scan for regulatory changes

Use `execute_shell_command` to run:
```
cd C:\Users\pranaldongare\Projects\CoPawClaw && venv\Scripts\python.exe skills\regulation_tracker\scripts\run_regulation_scan.py --domains "AI governance,data privacy,financial regulation" --jurisdictions "EU,US,UK" --lookback-days 30 --user-id "default"
```

### 2. Run impact assessment
```
cd C:\Users\pranaldongare\Projects\CoPawClaw && venv\Scripts\python.exe skills\regulation_tracker\scripts\impact_assessment.py --regulation "EU AI Act" --company-context "We deploy LLM-based customer service agents" --user-id "default"
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
