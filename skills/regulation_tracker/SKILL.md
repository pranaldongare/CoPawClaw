---
name: regulation_tracker
description: "Track regulatory changes, policy developments, and compliance requirements. Monitors AI regulations (EU AI Act, US AI executive orders), data privacy (GDPR, CCPA), and sector-specific rules. Use when the user asks about regulations, compliance, policy changes, or legal requirements."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "balance_scale"
  requires:
    bins: ["python3"]
    env: ["MAIN_MODEL"]
---

# Regulation Tracker Skill

## Available Commands

### Scan for regulatory changes
```bash
python3 scripts/run_regulation_scan.py --domains "AI governance,data privacy,financial regulation" --jurisdictions "EU,US,UK" --lookback-days 30 --user-id "$USER_ID"
```

### Run impact assessment
```bash
python3 scripts/impact_assessment.py --regulation "EU AI Act" --company-context "We deploy LLM-based customer service agents" --user-id "$USER_ID"
```

## Output Structure

- **Regulatory Updates**: Recent changes with jurisdiction, effective date, summary
- **Compliance Requirements**: Specific obligations extracted from regulatory text
- **Impact Assessment**: Per-regulation impact on specified business context
- **Timeline**: Key compliance deadlines
- **Risk Matrix**: Jurisdiction x regulation type with risk levels
- **Recommended Actions**: Prioritized compliance steps

## When to Use

- User asks about "regulations", "compliance", "policy changes"
- User mentions specific regulations (EU AI Act, GDPR, etc.)
- User asks about "legal requirements" or "regulatory risk"
