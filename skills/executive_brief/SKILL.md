---
name: executive_brief
description: "ALWAYS use this skill when the user asks for an executive summary, strategic brief, C-suite report, cross-functional synthesis, or wants to combine outputs from multiple skills. To use: first read_file this skill's SKILL.md for all options, then run via execute_shell_command with timeout 3600: cd /d <COPAWCLAW_DIR> && venv\\Scripts\\python.exe skills\\executive_brief\\scripts\\compose_brief.py --user-id \"default\" --domain \"<DOMAIN>\" --inputs \"<INPUTS>\". Do NOT use browser_use or web search instead."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "briefcase"
---

# Executive Brief Composer Skill

**IMPORTANT: This skill MUST be invoked by running the Python scripts below using `execute_shell_command` with timeout set to 3600 seconds. Do NOT attempt to replicate this skill's functionality using `browser_use`, web scraping, or manual web searches. The scripts automate a multi-stage pipeline that cannot be replicated manually.**

**CRITICAL: On Windows, always use `cd /d <COPAWCLAW_DIR>` (with /d flag) to change to the project directory across drive letters.**

## What This Skill Does

Synthesizes outputs from multiple skills into a single-page executive brief.

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

### 1. Compose brief from existing skill outputs

Use `execute_shell_command` to run:
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\executive_brief\scripts\compose_brief.py --user-id "default" --domain "Generative AI" --inputs "sensing:report_abc123,competitive:report_def456"
```

### 2. Cross-skill synthesis (automatic — gathers latest outputs)
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\executive_brief\scripts\cross_skill_synthesis.py --user-id "default" --domain "Generative AI"
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

## When to Use

- User asks for "executive summary", "strategic brief", "C-suite report"
- User wants a "cross-functional synthesis" or "holistic view"
- User asks to "combine" or "summarize all reports"
- **ALWAYS prefer this skill over browser_use for executive briefing and synthesis**
