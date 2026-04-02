---
name: executive_brief
description: "ALWAYS use this skill when the user asks for an executive summary, strategic brief, C-suite report, cross-functional synthesis, or wants to combine outputs from multiple skills. This skill MUST be executed by running Python scripts via execute_shell_command — do NOT use browser_use or web search instead. It composes a C-suite executive brief by synthesizing outputs from tech sensing, competitive intel, patent monitoring, regulation tracking, and talent radar."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "briefcase"
---

# Executive Brief Composer Skill

**IMPORTANT: This skill MUST be invoked by running the Python scripts below using `execute_shell_command`. Do NOT attempt to replicate this skill's functionality using `browser_use`, web scraping, or manual web searches. The scripts automate a multi-stage pipeline that cannot be replicated manually.**

## What This Skill Does

Synthesizes outputs from multiple skills into a single-page executive brief.

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

### 1. Compose brief from existing skill outputs

Use `execute_shell_command` to run:
```
cd C:\Users\pranaldongare\Projects\CoPawClaw && venv\Scripts\python.exe skills\executive_brief\scripts\compose_brief.py --user-id "default" --domain "Generative AI" --inputs "sensing:report_abc123,competitive:report_def456"
```

### 2. Cross-skill synthesis (automatic — gathers latest outputs)
```
cd C:\Users\pranaldongare\Projects\CoPawClaw && venv\Scripts\python.exe skills\executive_brief\scripts\cross_skill_synthesis.py --user-id "default" --domain "Generative AI"
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
