---
name: pptx_gen
description: "Generate professional PowerPoint presentations from skill outputs. Converts tech sensing reports, competitive intel, patent analysis, and executive briefs into branded slide decks. Use when the user asks for a presentation, deck, slides, or PPTX."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "presentation"
  requires:
    bins: ["python3"]
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

### Generate from any supported skill output
```bash
python3 scripts/generate_deck.py --input "data/input.json" --schema "tech_sensing|competitive|patent|regulation|talent|brief" --output "output/deck.pptx"
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
