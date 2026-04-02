---
name: email_digest
description: "Compose and send email digests summarizing outputs from all skills. Supports scheduled recurring digests (daily, weekly, biweekly, monthly). Use when the user asks to set up email alerts, digests, notifications, or scheduled reports."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "envelope"
  requires:
    bins: ["python3"]
    env: ["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"]
---

# Email Digest Composer Skill

## Available Commands

### Send a one-time digest
```bash
python3 scripts/send_digest.py --to "exec-team@company.com" --skills "tech_sensing,competitive_intel" --user-id "$USER_ID" --domain "Generative AI"
```

### Manage subscriptions
```bash
python3 scripts/manage_subscriptions.py --action create --email "cto@company.com" --skills "tech_sensing,competitive_intel,patent_monitor" --frequency weekly --domain "Generative AI" --user-id "$USER_ID"
python3 scripts/manage_subscriptions.py --action list --user-id "$USER_ID"
python3 scripts/manage_subscriptions.py --action delete --subscription-id "$ID"
```

## Email Format

HTML email with:
- Header: report date, domain badge
- Per-skill section: key stat cards
- Truncated executive summary (500 chars) per skill
- Footer: confidentiality notice

## When to Use

- User asks to "send email", "email digest", "email alert"
- User wants to "subscribe" to reports or set up "notifications"
- User asks about "scheduled reports" via email
