---
name: patent_monitor
description: "Monitor patent filings, grants, and IP trends. Tracks patent activity by technology domain, assignee (company), or specific patent families. Use when the user asks about patents, IP landscape, patent filings, or intellectual property trends."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "scroll"
  requires:
    bins: ["python3"]
    env: ["MAIN_MODEL"]
---

# Patent Monitor Skill

## Available Commands

### Scan for recent patents
```bash
python3 scripts/run_patent_scan.py --domain "large language models" --assignees "OpenAI,Google,Microsoft" --lookback-days 90 --user-id "$USER_ID"
```

### Analyze a specific patent
```bash
python3 scripts/analyze_patent.py --patent-id "US20240001234A1" --user-id "$USER_ID"
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
