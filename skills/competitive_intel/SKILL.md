---
name: competitive_intel
description: "ALWAYS use this skill when the user asks about competitors, competitive landscape, market positioning, company tracking, market share, SWOT, or threat assessment. To use: first read_file this skill's SKILL.md for all options, then run via execute_shell_command with timeout 3600: cd /d <COPAWCLAW_DIR> && venv\\Scripts\\python.exe skills\\competitive_intel\\scripts\\run_competitive_analysis.py --companies \"<COMPANIES>\" --domain \"<DOMAIN>\" --lookback-days 30 --user-id \"default\". Do NOT use browser_use or web search instead."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "detective"
---

# Competitive Intelligence Skill

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

### 1. Run competitive analysis

Use `execute_shell_command` to run:
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\competitive_intel\scripts\run_competitive_analysis.py --companies "OpenAI,Anthropic,Google DeepMind,Meta AI" --domain "Foundation Models" --lookback-days 30 --user-id "default"
```

Replace company names and domain with the user's targets.

### 2. Track a specific company
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\competitive_intel\scripts\track_company.py --company "Anthropic" --aspects "products,funding,hiring,partnerships" --lookback-days 14 --user-id "default"
```

## Output Structure

- **Company Profiles**: For each tracked company — recent news, product launches, funding events, key hires, partnerships
- **Competitive Matrix**: Side-by-side comparison across dimensions (product, market position, funding, team, technology)
- **Strategic Moves**: Significant actions with assessed strategic intent
- **Threat Assessment**: Per-competitor threat level (Critical/High/Medium/Low) with reasoning
- **Opportunity Gaps**: Market gaps identified from competitor weaknesses
- **SWOT Synthesis**: Aggregated strengths/weaknesses/opportunities/threats

## When to Use

- User asks about "competitors", "competitive landscape", "market positioning"
- User mentions specific company names and wants analysis
- User asks about "market share", "SWOT", or "threat assessment"
- **ALWAYS prefer this skill over browser_use for competitive intelligence analysis**
