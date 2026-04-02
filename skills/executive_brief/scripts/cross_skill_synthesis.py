#!/usr/bin/env python3
"""Automatically gather latest outputs from all skills and compose a brief."""

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
from enterprise_skills_lib.skill_envelope import load_latest_skill_output


SYNTHESIS_SKILLS = ["sensing", "competitive", "patents", "regulations", "talent"]


async def main():
    parser = argparse.ArgumentParser(description="Cross-skill synthesis")
    parser.add_argument("--user-id", default="default")
    parser.add_argument("--domain", default="Generative AI")
    args = parser.parse_args()

    print(f"Gathering latest outputs for user: {args.user_id}")

    skill_summaries = ""
    supporting_reports = []

    for skill_name in SYNTHESIS_SKILLS:
        envelope = load_latest_skill_output(skill_name, args.user_id)
        if envelope:
            summary_text = json.dumps(envelope.report, indent=1, ensure_ascii=False)[:3000]
            skill_summaries += f"\n--- {skill_name.upper()} ---\n{summary_text}\n"
            supporting_reports.append({
                "skill": skill_name,
                "report_id": envelope.tracking_id,
                "date": envelope.generated_at,
            })
        else:
            # Try loading from legacy file format
            skill_dir = os.path.join("data", args.user_id, skill_name)
            if os.path.isdir(skill_dir):
                report_files = sorted(
                    [f for f in os.listdir(skill_dir) if f.startswith("report_") and f.endswith(".json")],
                    key=lambda f: os.path.getmtime(os.path.join(skill_dir, f)),
                    reverse=True,
                )
                if report_files:
                    path = os.path.join(skill_dir, report_files[0])
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    summary_text = json.dumps(
                        {k: v for k, v in data.items() if k != "_meta" and v},
                        indent=1, ensure_ascii=False,
                    )[:3000]
                    skill_summaries += f"\n--- {skill_name.upper()} ---\n{summary_text}\n"
                    meta = data.get("_meta", {})
                    supporting_reports.append({
                        "skill": skill_name,
                        "report_id": meta.get("tracking_id", report_files[0]),
                    })

    if not skill_summaries:
        print(json.dumps({
            "status": "error",
            "message": "No skill outputs found. Run individual skills first.",
        }))
        return

    print(f"Found {len(supporting_reports)} skill outputs to synthesize")

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
        "skills_synthesized": [r["skill"] for r in supporting_reports],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(brief_data, f, indent=2, ensure_ascii=False)

    print(f"Executive brief saved to: {output_path}")
    print(json.dumps({
        "status": "success", "tracking_id": tracking_id,
        "output_path": output_path,
        "skills_synthesized": len(supporting_reports),
    }))


if __name__ == "__main__":
    asyncio.run(main())
