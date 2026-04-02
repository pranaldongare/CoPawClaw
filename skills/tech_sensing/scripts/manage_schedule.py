#!/usr/bin/env python3
"""Manage sensing report schedules (create, list, update, delete)."""

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from enterprise_skills_lib.sensing.scheduler import (
    add_schedule,
    list_schedules,
    remove_schedule,
    update_schedule,
)


async def main():
    parser = argparse.ArgumentParser(description="Manage sensing schedules")
    parser.add_argument("--action", required=True, choices=["create", "list", "update", "delete"])
    parser.add_argument("--user-id", default="default", help="User identifier")
    parser.add_argument("--domain", default="Generative AI", help="Domain for the schedule")
    parser.add_argument("--frequency", default="weekly", choices=["daily", "weekly", "biweekly", "monthly"])
    parser.add_argument("--schedule-id", help="Schedule ID (for update/delete)")
    parser.add_argument("--must-include", default="", help="Comma-separated priority keywords")
    parser.add_argument("--dont-include", default="", help="Comma-separated exclusion keywords")
    parser.add_argument("--email", default="", help="Email for notifications")
    args = parser.parse_args()

    if args.action == "create":
        must_include = [k.strip() for k in args.must_include.split(",") if k.strip()] or None
        dont_include = [k.strip() for k in args.dont_include.split(",") if k.strip()] or None

        schedule_id = await add_schedule(
            user_id=args.user_id,
            domain=args.domain,
            frequency=args.frequency,
            must_include=must_include,
            dont_include=dont_include,
            email=args.email or None,
        )
        print(json.dumps({
            "status": "success",
            "action": "created",
            "schedule_id": schedule_id,
            "frequency": args.frequency,
            "domain": args.domain,
        }))

    elif args.action == "list":
        schedules = await list_schedules(user_id=args.user_id)
        print(json.dumps({
            "status": "success",
            "schedules": [s.model_dump(mode="json") if hasattr(s, "model_dump") else s for s in schedules],
        }, default=str))

    elif args.action == "update":
        if not args.schedule_id:
            print(json.dumps({"status": "error", "message": "--schedule-id required for update"}))
            return
        await update_schedule(
            schedule_id=args.schedule_id,
            frequency=args.frequency,
        )
        print(json.dumps({"status": "success", "action": "updated", "schedule_id": args.schedule_id}))

    elif args.action == "delete":
        if not args.schedule_id:
            print(json.dumps({"status": "error", "message": "--schedule-id required for delete"}))
            return
        await remove_schedule(schedule_id=args.schedule_id)
        print(json.dumps({"status": "success", "action": "deleted", "schedule_id": args.schedule_id}))


if __name__ == "__main__":
    asyncio.run(main())
