#!/usr/bin/env python3
"""Scan for recent patents in a technology domain."""

import argparse
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import httpx

from enterprise_skills_lib.constants import GPU_SENSING_REPORT_LLM, PORT1
from enterprise_skills_lib.llm.client import invoke_llm
from enterprise_skills_lib.llm.output_schemas.patents import PatentReport
from enterprise_skills_lib.llm.prompts.patent_prompts import patent_analysis_prompt
from enterprise_skills_lib.sensing.ingest import search_duckduckgo
from enterprise_skills_lib.sensing.dedup import deduplicate_articles


async def _fetch_patents_view(domain: str, assignees: list[str] | None, lookback_days: int) -> list[dict]:
    """Fetch patents from USPTO PatentsView API."""
    patents = []
    try:
        query_criteria = [{"_text_any": {"patent_abstract": domain}}]
        if assignees:
            assignee_filters = [{"_text_phrase": {"assignee_organization": a}} for a in assignees]
            query_criteria.append({"_or": assignee_filters})

        query = {"_and": query_criteria} if len(query_criteria) > 1 else query_criteria[0]

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.patentsview.org/patents/query",
                json={
                    "q": query,
                    "f": ["patent_id", "patent_title", "patent_abstract", "patent_date",
                          "assignee_organization", "inventor_first_name", "inventor_last_name"],
                    "o": {"per_page": 25},
                    "s": [{"patent_date": "desc"}],
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                for p in data.get("patents", []):
                    patents.append({
                        "patent_id": p.get("patent_id", ""),
                        "title": p.get("patent_title", ""),
                        "abstract": p.get("patent_abstract", "")[:500],
                        "date": p.get("patent_date", ""),
                        "assignee": (p.get("assignees", [{}])[0].get("assignee_organization", "")
                                     if p.get("assignees") else ""),
                    })
    except Exception as e:
        print(f"PatentsView API error: {e}", file=sys.stderr)

    return patents


async def main():
    parser = argparse.ArgumentParser(description="Scan for patents")
    parser.add_argument("--domain", default="large language models", help="Technology domain")
    parser.add_argument("--assignees", default="", help="Comma-separated assignee companies")
    parser.add_argument("--lookback-days", type=int, default=90)
    parser.add_argument("--user-id", default="default")
    args = parser.parse_args()

    assignees = [a.strip() for a in args.assignees.split(",") if a.strip()] or None
    print(f"Scanning patents for: {args.domain}")

    # Fetch from PatentsView
    patents = await _fetch_patents_view(args.domain, assignees, args.lookback_days)
    print(f"Found {len(patents)} patents from PatentsView")

    # Supplement with news articles about patents
    queries = [f"{args.domain} patent filing", f"{args.domain} intellectual property"]
    if assignees:
        queries.extend(f"{a} patent" for a in assignees[:3])
    ddg = await search_duckduckgo(queries, args.domain, lookback_days=args.lookback_days)

    # Build text for LLM
    patents_text = ""
    for p in patents:
        patents_text += (
            f"PATENT: {p['patent_id']}\nTITLE: {p['title']}\n"
            f"ASSIGNEE: {p['assignee']}\nDATE: {p['date']}\n"
            f"ABSTRACT: {p['abstract']}\n\n"
        )
    for a in ddg[:10]:
        patents_text += f"NEWS: {a.title}\nURL: {a.url}\nSNIPPET: {a.snippet}\n\n"

    messages = patent_analysis_prompt(
        patents_text=patents_text,
        domain=args.domain,
        assignees=assignees,
    )

    report = await invoke_llm(
        gpu_model=GPU_SENSING_REPORT_LLM.model,
        response_schema=PatentReport,
        contents=messages,
        port=PORT1,
    )

    tracking_id = uuid.uuid4().hex[:12]
    output_dir = os.path.join("data", args.user_id, "patents")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"report_{tracking_id}.json")

    report_data = report.model_dump(mode="json")
    report_data["_meta"] = {
        "tracking_id": tracking_id,
        "domain": args.domain,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "patents_from_api": len(patents),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"Report saved to: {output_path}")
    print(json.dumps({
        "status": "success", "tracking_id": tracking_id,
        "output_path": output_path, "patents_analyzed": len(patents),
    }))


if __name__ == "__main__":
    asyncio.run(main())
