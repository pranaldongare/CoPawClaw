#!/usr/bin/env python3
"""Run a focused regulatory impact assessment."""

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from enterprise_skills_lib.constants import GPU_SENSING_REPORT_LLM, PORT1
from enterprise_skills_lib.llm.client import invoke_llm
from enterprise_skills_lib.llm.output_schemas.regulations import ImpactAssessment
from enterprise_skills_lib.llm.prompts.regulation_prompts import impact_assessment_prompt
from enterprise_skills_lib.sensing.ingest import search_duckduckgo, extract_full_text
from enterprise_skills_lib.sensing.dedup import deduplicate_articles


async def main():
    parser = argparse.ArgumentParser(description="Regulatory impact assessment")
    parser.add_argument("--regulation", required=True, help="Regulation name (e.g., 'EU AI Act')")
    parser.add_argument("--company-context", required=True,
                        help="Description of your business context")
    parser.add_argument("--user-id", default="default")
    args = parser.parse_args()

    print(f"Assessing impact of: {args.regulation}")

    # Fetch articles about the regulation
    queries = [
        f"{args.regulation} requirements",
        f"{args.regulation} compliance obligations",
        f"{args.regulation} enforcement",
    ]
    ddg = await search_duckduckgo(queries, args.regulation, lookback_days=180)
    unique = deduplicate_articles(ddg)

    import asyncio as aio
    sem = aio.Semaphore(5)
    async def _extract(a):
        async with sem:
            return await extract_full_text(a)

    enriched = await aio.gather(*[_extract(a) for a in unique[:15]])

    regulation_text = ""
    for a in enriched:
        regulation_text += f"SOURCE: {a.title}\nURL: {a.url}\n{(a.content or a.snippet)[:600]}\n\n"

    messages = impact_assessment_prompt(
        regulation_text=regulation_text,
        regulation_name=args.regulation,
        company_context=args.company_context,
    )

    assessment = await invoke_llm(
        gpu_model=GPU_SENSING_REPORT_LLM.model,
        response_schema=ImpactAssessment,
        contents=messages,
        port=PORT1,
    )

    output_dir = os.path.join("data", args.user_id, "regulations")
    os.makedirs(output_dir, exist_ok=True)
    safe_name = args.regulation.lower().replace(" ", "_")[:30]
    output_path = os.path.join(output_dir, f"impact_{safe_name}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(assessment.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    print(f"Assessment saved to: {output_path}")
    print(json.dumps({
        "status": "success",
        "regulation": args.regulation,
        "impact_level": assessment.impact_level,
        "output_path": output_path,
    }))


if __name__ == "__main__":
    asyncio.run(main())
