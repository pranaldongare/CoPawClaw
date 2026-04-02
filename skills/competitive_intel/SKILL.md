---
name: competitive_intel
description: "Track and analyze competitors. Monitors news, funding, product launches, partnerships, and strategic moves for specified companies or market segments. Use when the user asks about competitors, competitive landscape, market positioning, or company tracking."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "detective"
  requires:
    bins: ["python3"]
    env: ["MAIN_MODEL", "API_KEY_1"]
---

# Competitive Intelligence Skill

## Available Commands

### Run competitive analysis
```bash
python3 scripts/run_competitive_analysis.py --companies "OpenAI,Anthropic,Google DeepMind,Meta AI" --domain "Foundation Models" --lookback-days 30 --user-id "$USER_ID"
```

### Track a specific company
```bash
python3 scripts/track_company.py --company "Anthropic" --aspects "products,funding,hiring,partnerships" --lookback-days 14 --user-id "$USER_ID"
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
