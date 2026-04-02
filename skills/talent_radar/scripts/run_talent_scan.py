#!/usr/bin/env python3
"""Scan talent market for hiring trends and key moves."""

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
from enterprise_skills_lib.llm.output_schemas.talent import TalentReport
from enterprise_skills_lib.llm.prompts.talent_prompts import talent_scan_prompt
from enterprise_skills_lib.sensing.ingest import search_duckduckgo
from enterprise_skills_lib.sensing.dedup import deduplicate_articles
from enterprise_skills_lib.sensing.sources.hackernews import fetch_hackernews


async def main():
    parser = argparse.ArgumentParser(description="Run talent market scan")
    parser.add_argument("--roles", required=True, help="Comma-separated role categories")
    parser.add_argument("--companies", default="", help="Comma-separated companies to track")
    parser.add_argument("--lookback-days", type=int, default=30)
    parser.add_argument("--user-id", default="default")
    args = parser.parse_args()

    roles = [r.strip() for r in args.roles.split(",")]
    companies = [c.strip() for c in args.companies.split(",") if c.strip()] or None

    print(f"Scanning talent market for: {', '.join(roles)}")

    all_articles = []

    # DDG search
    queries = [f"{role} hiring trends 2026" for role in roles[:3]]
    queries.extend([f"AI engineer job market", "tech layoffs hiring 2026"])
    if companies:
        queries.extend(f"{c} hiring AI" for c in companies[:4])
    ddg = await search_duckduckgo(queries, "AI talent", lookback_days=args.lookback_days)
    all_articles.extend(ddg)

    # HN "Who is hiring" and talent discussions
    hn = await fetch_hackernews("AI hiring talent", lookback_days=args.lookback_days)
    all_articles.extend(hn)

    unique = deduplicate_articles(all_articles)
    print(f"Found {len(all_articles)} articles, {len(unique)} unique")

    articles_text = ""
    for a in unique[:40]:
        articles_text += f"TITLE: {a.title}\nURL: {a.url}\nSOURCE: {a.source}\n"
        articles_text += f"CONTENT: {(a.content or a.snippet)[:400]}\n\n"

    messages = talent_scan_prompt(
        articles_text=articles_text,
        roles=roles,
        companies=companies,
    )

    report = await invoke_llm(
        gpu_model=GPU_SENSING_REPORT_LLM.model,
        response_schema=TalentReport,
        contents=messages,
        port=PORT1,
    )

    tracking_id = uuid.uuid4().hex[:12]
    output_dir = os.path.join("data", args.user_id, "talent")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"report_{tracking_id}.json")

    report_data = report.model_dump(mode="json")
    report_data["_meta"] = {
        "tracking_id": tracking_id,
        "roles": roles,
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
