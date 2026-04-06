---
name: email_digest
description: "ALWAYS use this skill when the user asks to send email digests, set up email alerts, notifications, subscriptions, or scheduled reports via email. To use: first read_file this skill's SKILL.md for all options, then run via execute_shell_command with timeout 3600: cd /d <COPAWCLAW_DIR> && venv\\Scripts\\python.exe skills\\email_digest\\scripts\\send_digest.py --to \"<EMAIL>\" --skills \"<SKILLS>\" --user-id \"default\" --domain \"<DOMAIN>\". Do NOT use browser_use or web search instead."
metadata:
  builtin_skill_version: "1.0"
  copaw:
    emoji: "envelope"
---

# Email Digest Composer Skill

**IMPORTANT: This skill MUST be invoked by running the Python scripts below using `execute_shell_command` with timeout set to 3600 seconds. Do NOT attempt to replicate this skill's functionality using `browser_use`, web scraping, or manual web searches. The scripts automate a multi-stage pipeline that cannot be replicated manually.**

**CRITICAL: On Windows, always use `cd /d <COPAWCLAW_DIR>` (with /d flag) to change to the project directory across drive letters.**

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

### 1. Send a one-time digest

Use `execute_shell_command` to run:
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\email_digest\scripts\send_digest.py --to "exec-team@company.com" --skills "tech_sensing,competitive_intel" --user-id "default" --domain "Generative AI"
```

### 2. Manage subscriptions
```
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\email_digest\scripts\manage_subscriptions.py --action create --email "cto@company.com" --skills "tech_sensing,competitive_intel,patent_monitor" --frequency weekly --domain "Generative AI" --user-id "default"
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\email_digest\scripts\manage_subscriptions.py --action list --user-id "default"
cd /d <COPAWCLAW_DIR> && venv\Scripts\python.exe skills\email_digest\scripts\manage_subscriptions.py --action delete --subscription-id "$ID"
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
- **ALWAYS prefer this skill over browser_use for email digest and notification tasks**
