---
name: talent_radar
description: "Monitor AI and tech talent market. Tracks hiring trends, key executive moves, skill demand shifts, and talent availability. Use when the user asks about hiring, talent market, skill gaps, team building, or workforce planning."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "busts_in_silhouette"
  requires:
    bins: ["python3"]
    env: ["MAIN_MODEL"]
---

# Talent Radar Skill

## Available Commands

### Run talent market scan
```bash
python3 scripts/run_talent_scan.py --roles "ML Engineer,AI Researcher,LLM Infrastructure" --companies "OpenAI,Anthropic,Google,Meta" --lookback-days 30 --user-id "$USER_ID"
```

### Skill gap analysis
```bash
python3 scripts/skill_gap_analysis.py --current-team-skills "Python,PyTorch,RAG,fine-tuning" --target-capabilities "multi-agent systems,MCP,tool use" --user-id "$USER_ID"
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
