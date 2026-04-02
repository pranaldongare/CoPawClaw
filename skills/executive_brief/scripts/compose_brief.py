#!/usr/bin/env python3
"""Compose an executive brief from specified skill outputs."""

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
from enterprise_skills_lib.llm.output_schemas.executive import ExecutiveBrief
from enterprise_skills_lib.llm.prompts.executive_prompts import executive_brief_prompt


def _load_report(user_id: str, skill_and_id: str) -> dict | None:
    """Load a report given 'skill_name:tracking_id' format."""
    parts = skill_and_id.split(":")
    if len(parts) != 2:
        return None

    skill_name_map = {
        "sensing": "sensing",
        "competitive": "competitive",
        "patent": "patents",
        "regulation": "regulations",
        "talent": "talent",
    }
    skill_dir = skill_name_map.get(parts[0], parts[0])
    path = os.path.join("data", user_id, skill_dir, f"report_{parts[1]}.json")
    if not os.path.exists(path):
        print(f"Warning: report not found: {path}", file=sys.stderr)
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def main():
    parser = argparse.ArgumentParser(description="Compose executive brief")
    parser.add_argument("--user-id", default="default")
    parser.add_argument("--domain", default="Generative AI")
    parser.add_argument("--inputs", required=True,
                        help="Comma-separated 'skill:tracking_id' pairs")
    args = parser.parse_args()

    input_specs = [s.strip() for s in args.inputs.split(",")]

    # Load all referenced reports
    skill_summaries = ""
    supporting_reports = []
    for spec in input_specs:
        data = _load_report(args.user_id, spec)
        if data:
            skill_name = spec.split(":")[0]
            # Extract key fields for summary
            summary_text = json.dumps({
                k: v for k, v in data.items()
                if k != "_meta" and isinstance(v, (str, list)) and v
            }, indent=1, ensure_ascii=False)[:3000]

            skill_summaries += f"\n--- {skill_name.upper()} REPORT ---\n{summary_text}\n"
            supporting_reports.append({
                "skill": skill_name,
                "report_id": spec.split(":")[1],
                "title": data.get("report_title", data.get("brief_title", "")),
            })

    if not skill_summaries:
        print(json.dumps({"status": "error", "message": "No valid input reports found"}))
        return

    messages = executive_brief_prompt(
        skill_summaries=skill_summaries,
        domain=args.domain,
    )

    brief = await invoke_llm(
        gpu_model=GPU_SENSING_REPORT_LLM.model,
        response_schema=ExecutiveBrief,
        contents=messages,
        port=PORT1,
    )

    tracking_id = uuid.uuid4().hex[:12]
    output_dir = os.path.join("data", args.user_id, "briefs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"brief_{tracking_id}.json")

    brief_data = brief.model_dump(mode="json")
    brief_data["supporting_reports"] = supporting_reports
    brief_data["_meta"] = {
        "tracking_id": tracking_id,
        "domain": args.domain,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_reports": input_specs,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(brief_data, f, indent=2, ensure_ascii=False)

    print(f"Brief saved to: {output_path}")
    print(json.dumps({
        "status": "success", "tracking_id": tracking_id,
        "output_path": output_path,
    }))


if __name__ == "__main__":
    asyncio.run(main())
