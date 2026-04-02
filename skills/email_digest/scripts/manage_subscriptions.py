#!/usr/bin/env python3
"""Manage email digest subscriptions."""

import argparse
import asyncio
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

SUBSCRIPTIONS_FILE = os.path.join("data", "email_subscriptions.json")


def _load_subscriptions() -> list[dict]:
    if os.path.exists(SUBSCRIPTIONS_FILE):
        with open(SUBSCRIPTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_subscriptions(subs: list[dict]):
    os.makedirs(os.path.dirname(SUBSCRIPTIONS_FILE), exist_ok=True)
    with open(SUBSCRIPTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(subs, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Manage email subscriptions")
    parser.add_argument("--action", required=True, choices=["create", "list", "delete"])
    parser.add_argument("--email", default="", help="Subscriber email")
    parser.add_argument("--skills", default="tech_sensing", help="Comma-separated skills")
    parser.add_argument("--frequency", default="weekly", choices=["daily", "weekly", "biweekly", "monthly"])
    parser.add_argument("--domain", default="Generative AI")
    parser.add_argument("--user-id", default="default")
    parser.add_argument("--subscription-id", default="", help="Subscription ID (for delete)")
    args = parser.parse_args()

    subs = _load_subscriptions()

    if args.action == "create":
        if not args.email:
            print(json.dumps({"status": "error", "message": "--email required"}))
            return

        sub_id = uuid.uuid4().hex[:8]
        new_sub = {
            "id": sub_id,
            "email": args.email,
            "skills": [s.strip() for s in args.skills.split(",")],
            "frequency": args.frequency,
            "domain": args.domain,
            "user_id": args.user_id,
        }
        subs.append(new_sub)
        _save_subscriptions(subs)
        print(json.dumps({"status": "success", "action": "created", "subscription_id": sub_id}))

    elif args.action == "list":
        user_subs = [s for s in subs if s.get("user_id") == args.user_id]
        print(json.dumps({"status": "success", "subscriptions": user_subs}))

    elif args.action == "delete":
        if not args.subscription_id:
            print(json.dumps({"status": "error", "message": "--subscription-id required"}))
            return
        subs = [s for s in subs if s.get("id") != args.subscription_id]
        _save_subscriptions(subs)
        print(json.dumps({"status": "success", "action": "deleted", "subscription_id": args.subscription_id}))


if __name__ == "__main__":
    main()
