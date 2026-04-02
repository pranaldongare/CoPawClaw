#!/usr/bin/env python3
"""Run competitive intelligence analysis for specified companies."""

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
from enterprise_skills_lib.llm.output_schemas.competitive import CompetitiveReport
from enterprise_skills_lib.llm.prompts.competitive_prompts import competitive_analysis_prompt
from enterprise_skills_lib.sensing.ingest import search_duckduckgo, extract_full_text, RawArticle
from enterprise_skills_lib.sensing.dedup import deduplicate_articles
from enterprise_skills_lib.sensing.sources.hackernews import fetch_hackernews


async def main():
    parser = argparse.ArgumentParser(description="Run competitive analysis")
    parser.add_argument("--companies", required=True, help="Comma-separated company names")
    parser.add_argument("--domain", default="Generative AI", help="Market domain")
    parser.add_argument("--lookback-days", type=int, default=30)
    parser.add_argument("--user-id", default="default")
    parser.add_argument("--custom-requirements", default="")
    args = parser.parse_args()

    companies = [c.strip() for c in args.companies.split(",") if c.strip()]

    print(f"Analyzing {len(companies)} companies in {args.domain}...")

    # Ingest articles about each company
    all_articles: list[RawArticle] = []
    for company in companies:
        queries = [
            f"{company} announcement",
            f"{company} product launch",
            f"{company} funding",
            f"{company} partnership",
        ]
        ddg = await search_duckduckgo(queries, args.domain, lookback_days=args.lookback_days)
        all_articles.extend(ddg)

    # Also fetch from HN
    for company in companies[:3]:
        hn = await fetch_hackernews(company, lookback_days=args.lookback_days)
        all_articles.extend(hn)

    unique = deduplicate_articles(all_articles)
    print(f"Found {len(all_articles)} articles, {len(unique)} unique")

    # Extract text for top articles
    import asyncio as aio
    sem = aio.Semaphore(5)
    async def _extract(a):
        async with sem:
            return await extract_full_text(a)

    enriched = await aio.gather(*[_extract(a) for a in unique[:40]])

    # Build articles text for LLM
    articles_text = ""
    for a in enriched:
        articles_text += f"TITLE: {a.title}\nURL: {a.url}\nSOURCE: {a.source}\nCONTENT: {(a.content or a.snippet)[:500]}\n\n"

    # Classify via LLM
    messages = competitive_analysis_prompt(
        articles_text=articles_text,
        companies=companies,
        domain=args.domain,
        custom_requirements=args.custom_requirements,
    )

    report = await invoke_llm(
        gpu_model=GPU_SENSING_REPORT_LLM.model,
        response_schema=CompetitiveReport,
        contents=messages,
        port=PORT1,
    )

    # Save
    tracking_id = uuid.uuid4().hex[:12]
    output_dir = os.path.join("data", args.user_id, "competitive")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"report_{tracking_id}.json")

    report_data = report.model_dump(mode="json")
    report_data["_meta"] = {
        "tracking_id": tracking_id,
        "companies": companies,
        "domain": args.domain,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "articles_analyzed": len(unique),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"Report saved to: {output_path}")
    print(json.dumps({
        "status": "success",
        "tracking_id": tracking_id,
        "output_path": output_path,
        "companies": companies,
        "articles_analyzed": len(unique),
    }))


if __name__ == "__main__":
    asyncio.run(main())
