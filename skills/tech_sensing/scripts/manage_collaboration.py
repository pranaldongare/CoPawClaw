#!/usr/bin/env python3
"""Manage report collaboration — share, vote, comment, get feedback."""

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from enterprise_skills_lib.sensing.collaboration import (
    add_comment,
    add_vote,
    get_shared_report,
    list_shared_reports,
    share_report,
)


async def main():
    parser = argparse.ArgumentParser(description="Manage sensing report collaboration")
    parser.add_argument("--action", required=True, choices=["share", "vote", "comment", "feedback", "list"])
    parser.add_argument("--report-id", help="Report tracking ID (for share)")
    parser.add_argument("--share-id", help="Shared report ID (for vote/comment/feedback)")
    parser.add_argument("--user-id", default="default", help="User identifier")
    parser.add_argument("--item", help="Radar item name (for vote)")
    parser.add_argument("--ring", help="Proposed ring (for vote)")
    parser.add_argument("--text", help="Comment text")
    args = parser.parse_args()

    if args.action == "share":
        if not args.report_id:
            print(json.dumps({"status": "error", "message": "--report-id required for share"}))
            return

        # Load the report
        report_path = os.path.join("data", args.user_id, "sensing", f"report_{args.report_id}.json")
        if not os.path.exists(report_path):
            print(json.dumps({"status": "error", "message": f"Report not found: {report_path}"}))
            return

        share_id = await share_report(
            tracking_id=args.report_id,
            user_id=args.user_id,
        )
        print(json.dumps({"status": "success", "action": "shared", "share_id": share_id}))

    elif args.action == "vote":
        if not all([args.share_id, args.item, args.ring]):
            print(json.dumps({"status": "error", "message": "--share-id, --item, --ring required"}))
            return
        await add_vote(
            share_id=args.share_id,
            user_id=args.user_id,
            item_name=args.item,
            proposed_ring=args.ring,
        )
        print(json.dumps({"status": "success", "action": "voted", "item": args.item, "ring": args.ring}))

    elif args.action == "comment":
        if not args.share_id or not args.text:
            print(json.dumps({"status": "error", "message": "--share-id and --text required"}))
            return
        await add_comment(
            share_id=args.share_id,
            user_id=args.user_id,
            text=args.text,
        )
        print(json.dumps({"status": "success", "action": "commented"}))

    elif args.action == "feedback":
        if not args.share_id:
            print(json.dumps({"status": "error", "message": "--share-id required"}))
            return
        shared = await get_shared_report(share_id=args.share_id)
        if shared:
            print(json.dumps({
                "status": "success",
                "votes": [v.model_dump(mode="json") if hasattr(v, "model_dump") else v for v in shared.votes],
                "comments": [c.model_dump(mode="json") if hasattr(c, "model_dump") else c for c in shared.comments],
            }, default=str))
        else:
            print(json.dumps({"status": "error", "message": "Shared report not found"}))

    elif args.action == "list":
        reports = await list_shared_reports()
        print(json.dumps({
            "status": "success",
            "shared_reports": [r.model_dump(mode="json") if hasattr(r, "model_dump") else r for r in reports],
        }, default=str))


if __name__ == "__main__":
    asyncio.run(main())
