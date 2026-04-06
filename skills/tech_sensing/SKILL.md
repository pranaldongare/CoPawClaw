---
name: tech_sensing
description: "ALWAYS use this skill when the user asks about technology trends, emerging tech, tech radar, sensing report, technology landscape, or what's new in any technology domain. To use: first read_file this skill's SKILL.md for all options, then run via execute_shell_command with timeout 3600: cd /d <COPAWCLAW_DIR> && venv\\Scripts\\python.exe skills\\tech_sensing\\scripts\\run_pipeline.py --domain \"<TOPIC>\" --lookback-days 7 --user-id \"default\". Do NOT use browser_use or web search instead."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "radar"
---

# Tech Sensing Skill

**IMPORTANT: This skill MUST be invoked by running the Python scripts below using `execute_shell_command` with timeout set to 3600 seconds. Do NOT attempt to replicate this skill's functionality using `browser_use`, web scraping, or manual web searches. The scripts automate a 7-stage pipeline that cannot be replicated manually.**

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

### 1. Generate a full sensing report

Use `execute_shell_command` to run:
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\tech_sensing\scripts\run_pipeline.py --domain "<DOMAIN>" --lookback-days 7 --user-id "default"
```

Replace `<DOMAIN>` with the user's topic (e.g., "Generative AI", "Cybersecurity", "Cloud Computing").

Optional flags:
- `--custom-requirements "Focus on LLM agents"` — additional guidance
- `--must-include "RAG,agents,MCP"` — priority keywords
- `--dont-include "crypto,blockchain"` — exclusion keywords
- `--lookback-days 14` — scan more days (default: 7)
- `--key-people "Sam Altman,Demis Hassabis"` — people to watch

Output: JSON at `data/default/sensing/report_{tracking_id}.json`

### 2. Deep dive into a technology
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\tech_sensing\scripts\run_deep_dive.py --technology "<TECH_NAME>" --domain "<DOMAIN>" --user-id "default"
```

### 3. Compare two reports
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\tech_sensing\scripts\run_comparison.py --report-a "<TRACKING_ID_A>" --report-b "<TRACKING_ID_B>" --user-id "default"
```

### 4. Build technology timeline
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\tech_sensing\scripts\run_timeline.py --user-id "default" --domain "<DOMAIN>"
```

### 5. Manage schedules
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\tech_sensing\scripts\manage_schedule.py --action create --domain "<DOMAIN>" --frequency weekly --user-id "default"
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\tech_sensing\scripts\manage_schedule.py --action list --user-id "default"
```

### 6. Share and collaborate
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\tech_sensing\scripts\manage_collaboration.py --action share --report-id "<TRACKING_ID>" --user-id "default"
```

## Report Structure

The generated report contains:
- **Executive Summary** — High-level overview
- **Headline Moves** — Top 10 significant industry moves
- **Key Trends** — 5-10 trends with impact levels
- **Technology Radar** — 15-30 items across 4 quadrants and 4 rings (Adopt/Trial/Assess/Hold)
- **Radar Item Details** — Per-item analysis
- **Market Signals** — Strategic moves with impact assessment
- **Recommendations** — Prioritized action items

## When to Use

- User asks about "technology trends", "what's new in AI", "emerging technologies"
- User wants a "tech radar", "sensing report", "technology landscape"
- User asks to "monitor" or "track" technology areas
- User mentions "tech sensing" or "sensing" in any form
- User wants to compare reports or see how technologies evolved
- **ALWAYS prefer this skill over browser_use or news skills for technology analysis**
