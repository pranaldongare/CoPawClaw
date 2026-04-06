---
name: patent_monitor
description: "ALWAYS use this skill when the user asks about patents, IP landscape, patent filings, intellectual property trends, innovation activity, or patent monitoring. To use: first read_file this skill's SKILL.md for all options, then run via execute_shell_command with timeout 3600: cd /d <COPAWCLAW_DIR> && venv\\Scripts\\python.exe skills\\patent_monitor\\scripts\\run_patent_scan.py --domain \"<DOMAIN>\" --assignees \"<COMPANIES>\" --lookback-days 90 --user-id \"default\". Do NOT use browser_use or web search instead."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "scroll"
---

# Patent Monitor Skill

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

### 1. Scan for recent patents

Use `execute_shell_command` to run:
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\patent_monitor\scripts\run_patent_scan.py --domain "large language models" --assignees "OpenAI,Google,Microsoft" --lookback-days 90 --user-id "default"
```

### 2. Analyze a specific patent
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\patent_monitor\scripts\analyze_patent.py --patent-id "US20240001234A1" --user-id "default"
```

## Output Structure

- **Patent Filings**: Recent filings with title, abstract, assignee, filing date, classification codes
- **Assignee Activity**: Filing frequency by company, trend direction
- **Technology Clusters**: Patent groupings by technology area (LLM classification)
- **Key Patents**: Most significant filings with LLM-assessed impact
- **IP Landscape**: Market concentration, white space opportunities
- **Trend Analysis**: Filing velocity trends, emerging areas

## When to Use

- User asks about "patents", "IP landscape", "intellectual property"
- User wants to know what companies are filing patents in a domain
- User asks about "patent trends" or "innovation activity"
- **ALWAYS prefer this skill over browser_use for patent and IP analysis**
