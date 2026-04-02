#!/usr/bin/env python3
"""Manage organizational context for personalized reports."""

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from enterprise_skills_lib.sensing.org_context import (
    OrgTechContext,
    load_org_context,
    save_org_context,
)


async def main():
    parser = argparse.ArgumentParser(description="Manage org context")
    parser.add_argument("--action", required=True, choices=["get", "update"])
    parser.add_argument("--user-id", default="default", help="User identifier")
    parser.add_argument("--tech-stack", default="", help="Comma-separated tech stack")
    parser.add_argument("--industry", default="", help="Industry/sector")
    parser.add_argument("--priorities", default="", help="Comma-separated strategic priorities")
    parser.add_argument("--competitors", default="", help="Comma-separated competitors")
    args = parser.parse_args()

    if args.action == "get":
        ctx = await load_org_context(user_id=args.user_id)
        if ctx:
            print(json.dumps({
                "status": "success",
                "org_context": ctx.model_dump(mode="json"),
            }))
        else:
            print(json.dumps({"status": "success", "org_context": None, "message": "No org context set"}))

    elif args.action == "update":
        ctx = OrgTechContext(
            tech_stack=[t.strip() for t in args.tech_stack.split(",") if t.strip()],
            industry=args.industry or "Technology",
            priorities=[p.strip() for p in args.priorities.split(",") if p.strip()],
            competitors=[c.strip() for c in args.competitors.split(",") if c.strip()],
        )
        await save_org_context(user_id=args.user_id, context=ctx)
        print(json.dumps({
            "status": "success",
            "action": "updated",
            "org_context": ctx.model_dump(mode="json"),
        }))


if __name__ == "__main__":
    asyncio.run(main())
