---
name: executive_brief
description: "Compose a C-suite executive brief by synthesizing outputs from tech sensing, competitive intel, patent monitoring, regulation tracking, and talent radar. Produces a concise one-page strategic overview. Use when the user asks for an executive summary, strategic brief, C-suite report, or cross-functional synthesis."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "briefcase"
  requires:
    bins: ["python3"]
    env: ["MAIN_MODEL"]
---

# Executive Brief Composer Skill

## What This Skill Does

Synthesizes outputs from multiple skills into a single-page executive brief.

## Available Commands

### Compose brief from existing skill outputs
```bash
python3 scripts/compose_brief.py --user-id "$USER_ID" --domain "Generative AI" --inputs "sensing:report_abc123,competitive:report_def456"
```

### Cross-skill synthesis (automatic — gathers latest outputs)
```bash
python3 scripts/cross_skill_synthesis.py --user-id "$USER_ID" --domain "Generative AI"
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
