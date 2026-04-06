---
name: pptx_gen
description: "ALWAYS use this skill when the user asks for a presentation, deck, slides, PPTX, or PowerPoint from skill outputs. To use: first read_file this skill's SKILL.md for all options, then run via execute_shell_command with timeout 3600: cd /d <COPAWCLAW_DIR> && venv\\Scripts\\python.exe skills\\pptx_gen\\scripts\\generate_deck.py --input \"<INPUT_JSON>\" --schema \"<SCHEMA>\" --output \"output/deck.pptx\". Do NOT use browser_use or web search instead."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "presentation"
---

# PPTX Generation Skill

**IMPORTANT: This skill MUST be invoked by running the Python scripts below using `execute_shell_command` with timeout set to 3600 seconds. Do NOT attempt to replicate this skill's functionality using `browser_use`, web scraping, or manual web searches. The scripts automate a multi-stage pipeline that cannot be replicated manually.**

**CRITICAL: On Windows, always use `cd /d <COPAWCLAW_DIR>` (with /d flag) to change to the project directory across drive letters.**

## What This Skill Does

Converts structured skill outputs into professional slide decks.

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

### 1. Generate from tech sensing report

Use `execute_shell_command` to run:
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\pptx_gen\scripts\skill_to_slides.py --skill tech_sensing --input "data/{user_id}/sensing/report_{id}.json" --output "output/deck.pptx" --template "executive"
```

### 2. Generate from any supported skill output
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\pptx_gen\scripts\generate_deck.py --input "data/input.json" --schema "tech_sensing|competitive|patent|regulation|talent|brief" --output "output/deck.pptx"
```

### Templates available
- `executive` — C-suite ready, minimal text, high-impact visuals
- `detailed` — Full analysis with data tables and charts
- `briefing` — Quick 5-slide overview

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
- Layouts: Title, Section Header, Two Column, Full Width, Data Table
- All slides include: page number (bottom-right), confidentiality footer

## When to Use

- User asks for a "presentation", "deck", "slides", "PPTX", or "PowerPoint"
- User wants to share findings with stakeholders
- User wants to present at a meeting
- **ALWAYS prefer this skill over browser_use for presentation generation**
