#!/usr/bin/env python3
"""Run the full tech sensing pipeline and save the report."""

import argparse
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from enterprise_skills_lib.sensing.pipeline import run_sensing_pipeline


async def main():
    parser = argparse.ArgumentParser(description="Run tech sensing pipeline")
    parser.add_argument("--domain", default="Generative AI", help="Technology domain to scan")
    parser.add_argument("--lookback-days", type=int, default=7, help="Days to look back")
    parser.add_argument("--user-id", default="default", help="User identifier")
    parser.add_argument("--custom-requirements", default="", help="Additional LLM guidance")
    parser.add_argument("--must-include", default="", help="Comma-separated priority keywords")
    parser.add_argument("--dont-include", default="", help="Comma-separated exclusion keywords")
    parser.add_argument("--feed-urls", default="", help="Comma-separated RSS feed URLs")
    parser.add_argument("--search-queries", default="", help="Comma-separated search queries")
    parser.add_argument("--key-people", default="", help="Comma-separated key people to watch")
    args = parser.parse_args()

    must_include = [k.strip() for k in args.must_include.split(",") if k.strip()] or None
    dont_include = [k.strip() for k in args.dont_include.split(",") if k.strip()] or None
    feed_urls = [u.strip() for u in args.feed_urls.split(",") if u.strip()] or None
    search_queries = [q.strip() for q in args.search_queries.split(",") if q.strip()] or None
    key_people = [p.strip() for p in args.key_people.split(",") if p.strip()] or None

    async def progress(stage, pct, msg=""):
        print(f"[{pct:3d}%] {stage}: {msg}")

    result = await run_sensing_pipeline(
        domain=args.domain,
        custom_requirements=args.custom_requirements,
        feed_urls=feed_urls,
        search_queries=search_queries,
        must_include=must_include,
        dont_include=dont_include,
        lookback_days=args.lookback_days,
        progress_callback=progress,
        user_id=args.user_id,
        key_people=key_people,
    )

    # Save report
    tracking_id = uuid.uuid4().hex[:12]
    output_dir = os.path.join("data", args.user_id, "sensing")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"report_{tracking_id}.json")

    report_data = result.report.model_dump(mode="json")
    report_data["_meta"] = {
        "tracking_id": tracking_id,
        "domain": args.domain,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_article_count": result.raw_article_count,
        "deduped_article_count": result.deduped_article_count,
        "classified_article_count": result.classified_article_count,
        "execution_time_seconds": result.execution_time_seconds,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"\nReport saved to: {output_path}")
    print(f"Tracking ID: {tracking_id}")
    print(f"Articles: {result.raw_article_count} raw → {result.deduped_article_count} unique → {result.classified_article_count} classified")
    print(f"Execution time: {result.execution_time_seconds}s")

    # Output JSON summary for CoPaw agent consumption
    print(json.dumps({
        "status": "success",
        "tracking_id": tracking_id,
        "output_path": output_path,
        "stats": {
            "raw": result.raw_article_count,
            "unique": result.deduped_article_count,
            "classified": result.classified_article_count,
            "time_seconds": result.execution_time_seconds,
        },
    }))


if __name__ == "__main__":
    asyncio.run(main())
