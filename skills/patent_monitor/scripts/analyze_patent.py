#!/usr/bin/env python3
"""Analyze a specific patent by ID."""

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import httpx

from enterprise_skills_lib.constants import GPU_SENSING_REPORT_LLM, PORT1
from enterprise_skills_lib.llm.client import invoke_llm
from enterprise_skills_lib.llm.output_schemas.patents import PatentFiling
from enterprise_skills_lib.sensing.ingest import search_duckduckgo


async def main():
    parser = argparse.ArgumentParser(description="Analyze a specific patent")
    parser.add_argument("--patent-id", required=True, help="Patent ID (e.g., US20240001234A1)")
    parser.add_argument("--user-id", default="default")
    args = parser.parse_args()

    print(f"Analyzing patent: {args.patent_id}")

    # Fetch patent details
    patent_text = f"Patent ID: {args.patent_id}\n"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.patentsview.org/patents/query",
                json={
                    "q": {"patent_id": args.patent_id},
                    "f": ["patent_id", "patent_title", "patent_abstract", "patent_date",
                          "assignee_organization", "inventor_first_name", "inventor_last_name",
                          "patent_type"],
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                patents = data.get("patents", [])
                if patents:
                    p = patents[0]
                    patent_text += f"Title: {p.get('patent_title', '')}\n"
                    patent_text += f"Abstract: {p.get('patent_abstract', '')}\n"
                    patent_text += f"Date: {p.get('patent_date', '')}\n"
    except Exception as e:
        print(f"API error: {e}", file=sys.stderr)

    # Supplement with DDG
    ddg = await search_duckduckgo([args.patent_id], "patent", lookback_days=365)
    for a in ddg[:5]:
        patent_text += f"\nRelated: {a.title}\nURL: {a.url}\n"

    messages = [
        {
            "role": "system",
            "parts": (
                "You are a patent analyst. Analyze the following patent and provide:\n"
                "- Technology cluster classification\n"
                "- Significance score (0.0-1.0)\n"
                "- Detailed analysis of claims and implications\n"
                "Return ONLY valid JSON matching the PatentFiling schema."
            ),
        },
        {"role": "user", "parts": patent_text},
    ]

    result = await invoke_llm(
        gpu_model=GPU_SENSING_REPORT_LLM.model,
        response_schema=PatentFiling,
        contents=messages,
        port=PORT1,
    )

    output_dir = os.path.join("data", args.user_id, "patents")
    os.makedirs(output_dir, exist_ok=True)
    safe_id = args.patent_id.replace("/", "_")
    output_path = os.path.join(output_dir, f"patent_{safe_id}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    print(f"Analysis saved to: {output_path}")
    print(json.dumps({"status": "success", "patent_id": args.patent_id, "output_path": output_path}))


if __name__ == "__main__":
    asyncio.run(main())
