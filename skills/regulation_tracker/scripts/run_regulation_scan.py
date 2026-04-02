#!/usr/bin/env python3
"""Scan for regulatory changes across jurisdictions."""

import argparse
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from enterprise_skills_lib.constants import GPU_SENSING_REPORT_LLM, PORT1
from enterprise_skills_lib.llm.client import invoke_llm
from enterprise_skills_lib.llm.output_schemas.regulations import RegulationReport
from enterprise_skills_lib.llm.prompts.regulation_prompts import regulation_scan_prompt
from enterprise_skills_lib.sensing.ingest import fetch_rss_feeds, search_duckduckgo
from enterprise_skills_lib.sensing.dedup import deduplicate_articles
from enterprise_skills_lib.sensing.sources.hackernews import fetch_hackernews


REGULATION_RSS_FEEDS = [
    "https://www.federalregister.gov/api/v1/documents.rss",
    "https://feeds.feedburner.com/IappDailyDash",
]


async def main():
    parser = argparse.ArgumentParser(description="Scan for regulatory changes")
    parser.add_argument("--domains", default="AI governance,data privacy",
                        help="Comma-separated regulatory domains")
    parser.add_argument("--jurisdictions", default="EU,US,UK",
                        help="Comma-separated jurisdictions")
    parser.add_argument("--lookback-days", type=int, default=30)
    parser.add_argument("--user-id", default="default")
    args = parser.parse_args()

    domains = [d.strip() for d in args.domains.split(",")]
    jurisdictions = [j.strip() for j in args.jurisdictions.split(",")]

    print(f"Scanning regulations: {', '.join(domains)} in {', '.join(jurisdictions)}")

    all_articles = []

    # RSS feeds
    rss = await fetch_rss_feeds(REGULATION_RSS_FEEDS, lookback_days=args.lookback_days)
    all_articles.extend(rss)

    # DDG search
    queries = []
    for d in domains:
        for j in jurisdictions:
            queries.append(f"{d} regulation {j} 2026")
    queries.extend([f"{d} compliance update" for d in domains])
    ddg = await search_duckduckgo(queries, "regulation", lookback_days=args.lookback_days)
    all_articles.extend(ddg)

    # HN
    for d in domains[:2]:
        hn = await fetch_hackernews(f"{d} regulation", lookback_days=args.lookback_days)
        all_articles.extend(hn)

    unique = deduplicate_articles(all_articles)
    print(f"Found {len(all_articles)} articles, {len(unique)} unique")

    articles_text = ""
    for a in unique[:40]:
        articles_text += f"TITLE: {a.title}\nURL: {a.url}\nSOURCE: {a.source}\n"
        articles_text += f"CONTENT: {(a.content or a.snippet)[:400]}\n\n"

    messages = regulation_scan_prompt(
        articles_text=articles_text,
        domains=domains,
        jurisdictions=jurisdictions,
    )

    report = await invoke_llm(
        gpu_model=GPU_SENSING_REPORT_LLM.model,
        response_schema=RegulationReport,
        contents=messages,
        port=PORT1,
    )

    tracking_id = uuid.uuid4().hex[:12]
    output_dir = os.path.join("data", args.user_id, "regulations")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"report_{tracking_id}.json")

    report_data = report.model_dump(mode="json")
    report_data["_meta"] = {
        "tracking_id": tracking_id,
        "domains": domains,
        "jurisdictions": jurisdictions,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"Report saved to: {output_path}")
    print(json.dumps({
        "status": "success", "tracking_id": tracking_id,
        "output_path": output_path, "articles_analyzed": len(unique),
    }))


if __name__ == "__main__":
    asyncio.run(main())
