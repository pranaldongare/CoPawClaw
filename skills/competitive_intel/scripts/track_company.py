#!/usr/bin/env python3
"""Track a single company in detail."""

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
from enterprise_skills_lib.llm.output_schemas.competitive import CompetitorProfile
from enterprise_skills_lib.llm.prompts.competitive_prompts import company_tracking_prompt
from enterprise_skills_lib.sensing.ingest import search_duckduckgo, extract_full_text
from enterprise_skills_lib.sensing.dedup import deduplicate_articles
from enterprise_skills_lib.sensing.sources.hackernews import fetch_hackernews


async def main():
    parser = argparse.ArgumentParser(description="Track a specific company")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--aspects", default="products,funding,hiring,partnerships",
                        help="Comma-separated aspects to track")
    parser.add_argument("--lookback-days", type=int, default=14)
    parser.add_argument("--user-id", default="default")
    args = parser.parse_args()

    aspects = [a.strip() for a in args.aspects.split(",")]
    print(f"Tracking {args.company}: {', '.join(aspects)}")

    queries = [f"{args.company} {aspect}" for aspect in aspects]
    ddg = await search_duckduckgo(queries, args.company, lookback_days=args.lookback_days)
    hn = await fetch_hackernews(args.company, lookback_days=args.lookback_days)

    all_articles = ddg + hn
    unique = deduplicate_articles(all_articles)

    import asyncio as aio
    sem = aio.Semaphore(5)
    async def _extract(a):
        async with sem:
            return await extract_full_text(a)

    enriched = await aio.gather(*[_extract(a) for a in unique[:30]])

    articles_text = ""
    for a in enriched:
        articles_text += f"TITLE: {a.title}\nURL: {a.url}\nCONTENT: {(a.content or a.snippet)[:500]}\n\n"

    messages = company_tracking_prompt(
        articles_text=articles_text,
        company=args.company,
        aspects=aspects,
    )

    profile = await invoke_llm(
        gpu_model=GPU_SENSING_REPORT_LLM.model,
        response_schema=CompetitorProfile,
        contents=messages,
        port=PORT1,
    )

    output_dir = os.path.join("data", args.user_id, "competitive")
    os.makedirs(output_dir, exist_ok=True)
    safe_name = args.company.lower().replace(" ", "_")[:20]
    output_path = os.path.join(output_dir, f"company_{safe_name}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profile.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    print(f"Profile saved to: {output_path}")
    print(json.dumps({"status": "success", "company": args.company, "output_path": output_path}))


if __name__ == "__main__":
    asyncio.run(main())
