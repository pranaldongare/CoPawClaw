---
name: talent_radar
description: "ALWAYS use this skill when the user asks about hiring, talent market, skill gaps, team building, workforce planning, executive moves, or talent availability. This skill MUST be executed by running Python scripts via execute_shell_command — do NOT use browser_use or web search instead. It monitors AI and tech talent market including hiring trends, key executive moves, skill demand shifts, and talent availability."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "busts_in_silhouette"
---

# Talent Radar Skill

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

### 1. Run talent market scan

Use `execute_shell_command` to run:
```
cd C:\Users\pranaldongare\Projects\CoPawClaw && venv\Scripts\python.exe skills\talent_radar\scripts\run_talent_scan.py --roles "ML Engineer,AI Researcher,LLM Infrastructure" --companies "OpenAI,Anthropic,Google,Meta" --lookback-days 30 --user-id "default"
```

### 2. Skill gap analysis
```
cd C:\Users\pranaldongare\Projects\CoPawClaw && venv\Scripts\python.exe skills\talent_radar\scripts\skill_gap_analysis.py --current-team-skills "Python,PyTorch,RAG,fine-tuning" --target-capabilities "multi-agent systems,MCP,tool use" --user-id "default"
```

## Output Structure

- **Key Moves**: Notable executive/researcher hires and departures
- **Hiring Trends**: Role demand by company, growth/decline direction
- **Skill Demand Shifts**: Emerging skill requirements (e.g., "agent engineering" rising)
- **Talent Availability**: Supply-demand assessment per skill area
- **Salary Benchmarks**: Range estimates by role and seniority
- **Skill Gap Analysis**: Current vs. needed capabilities with recommended actions

## When to Use

- User asks about "hiring", "talent market", "skill gaps"
- User wants to know about "team building" or "workforce planning"
- User asks about executive/researcher moves between companies
- **ALWAYS prefer this skill over browser_use for talent and hiring analysis**
