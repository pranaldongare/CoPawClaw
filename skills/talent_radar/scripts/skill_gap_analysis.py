#!/usr/bin/env python3
"""Analyze skill gaps between current team and target capabilities."""

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from pydantic import BaseModel, Field
from typing import List

from enterprise_skills_lib.constants import GPU_SENSING_REPORT_LLM, PORT1
from enterprise_skills_lib.llm.client import invoke_llm
from enterprise_skills_lib.llm.output_schemas.talent import SkillGap
from enterprise_skills_lib.llm.prompts.talent_prompts import skill_gap_prompt


class SkillGapResult(BaseModel):
    skill_gaps: List[SkillGap]


async def main():
    parser = argparse.ArgumentParser(description="Skill gap analysis")
    parser.add_argument("--current-team-skills", required=True,
                        help="Comma-separated current skills")
    parser.add_argument("--target-capabilities", required=True,
                        help="Comma-separated target capabilities")
    parser.add_argument("--user-id", default="default")
    args = parser.parse_args()

    current = [s.strip() for s in args.current_team_skills.split(",")]
    target = [t.strip() for t in args.target_capabilities.split(",")]

    print(f"Analyzing gaps: {len(current)} current skills -> {len(target)} target capabilities")

    messages = skill_gap_prompt(
        current_skills=current,
        target_capabilities=target,
    )

    result = await invoke_llm(
        gpu_model=GPU_SENSING_REPORT_LLM.model,
        response_schema=SkillGapResult,
        contents=messages,
        port=PORT1,
    )

    output_dir = os.path.join("data", args.user_id, "talent")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "skill_gap_analysis.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    print(f"Analysis saved to: {output_path}")
    print(json.dumps({
        "status": "success",
        "output_path": output_path,
        "gaps_identified": len(result.skill_gaps),
    }))


if __name__ == "__main__":
    asyncio.run(main())
