---
name: tech_sensing
description: "Run a comprehensive Technology Radar analysis. Ingests articles from RSS, DuckDuckGo, GitHub Trending, arXiv, and Hacker News, then classifies, generates radar reports, deep dives, comparisons, and timelines. Use this skill when the user asks about technology trends, emerging tech, or wants a sensing report."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "radar"
  requires:
    bins: ["python3"]
    env: ["MAIN_MODEL", "API_KEY_1"]
---

# Tech Sensing Skill

## What This Skill Does

Generates Technology Radar reports by scanning 5 data sources and analyzing trends via LLM.

## Available Commands

### Generate a full sensing report
```bash
python3 scripts/run_pipeline.py --domain "Generative AI" --lookback-days 7 --user-id "$USER_ID"
```

Optional arguments:
- `--custom-requirements "Focus on LLM agents"` — additional guidance for the LLM
- `--must-include "RAG,agents,MCP"` — comma-separated keywords to prioritize
- `--dont-include "crypto,blockchain"` — comma-separated keywords to exclude
- `--feed-urls "url1,url2"` — override default RSS feeds
- `--search-queries "query1,query2"` — override default DuckDuckGo queries
- `--key-people "Sam Altman,Demis Hassabis"` — people to watch for

Output: JSON file at `data/{user_id}/sensing/report_{tracking_id}.json`

### Deep dive into a specific technology
```bash
python3 scripts/run_deep_dive.py --technology "Model Context Protocol" --domain "Generative AI" --user-id "$USER_ID"
```

Output: JSON with comprehensive_analysis, technical_architecture, competitive_landscape, adoption_roadmap, risk_assessment, key_resources

### Compare two reports
```bash
python3 scripts/run_comparison.py --report-a "$TRACKING_ID_A" --report-b "$TRACKING_ID_B" --user-id "$USER_ID"
```

Output: Radar diff (added/removed/moved/unchanged items), trend diff, signal diffs

### Build technology timeline
```bash
python3 scripts/run_timeline.py --user-id "$USER_ID" --domain "Generative AI"
```

Output: Per-technology ring evolution across all historical reports

### Manage schedules
```bash
python3 scripts/manage_schedule.py --action create --domain "Generative AI" --frequency weekly --user-id "$USER_ID"
python3 scripts/manage_schedule.py --action list --user-id "$USER_ID"
python3 scripts/manage_schedule.py --action delete --schedule-id "$ID"
```

### Manage collaboration (share, vote, comment)
```bash
python3 scripts/manage_collaboration.py --action share --report-id "$TRACKING_ID" --user-id "$USER_ID"
python3 scripts/manage_collaboration.py --action vote --share-id "$ID" --item "GPT-5" --ring "Trial" --user-id "$USER_ID"
python3 scripts/manage_collaboration.py --action comment --share-id "$ID" --text "Interesting trend" --user-id "$USER_ID"
python3 scripts/manage_collaboration.py --action feedback --share-id "$ID"
```

### Manage organizational context
```bash
python3 scripts/manage_org_context.py --action get --user-id "$USER_ID"
python3 scripts/manage_org_context.py --action update --user-id "$USER_ID" --tech-stack "Python,React,PostgreSQL" --industry "Financial Services" --priorities "AI automation,Cost reduction"
```

## Report Structure

The generated report contains:
- **Executive Summary** — High-level overview
- **Headline Moves** — Top 10 significant industry moves (actor + segment + sources)
- **Key Trends** — 5-10 trends with evidence, impact level (High/Medium/Low), time horizon
- **Technology Radar** — 15-30 items across 4 quadrants (Techniques/Platforms/Tools/Languages & Frameworks) and 4 rings (Adopt/Trial/Assess/Hold)
- **Radar Item Details** — Deep write-up per item: what_it_is, why_it_matters, current_state, key_players, practical_applications
- **Market Signals** — Company/player strategic moves with industry impact assessment
- **Report Sections** — 3-6 deep-dive narrative sections
- **Recommendations** — Prioritized (Critical/High/Medium/Low) with related trends
- **Notable Articles** — Top source articles with relevance scores

## When to Use

- User asks about "technology trends", "what's new in AI", "emerging technologies"
- User wants a "tech radar", "sensing report", "technology landscape"
- User asks to "monitor" or "track" technology areas
- User wants to compare reports or see how technologies have evolved
- User wants to schedule recurring reports
