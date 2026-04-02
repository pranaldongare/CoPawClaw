#!/usr/bin/env python3
"""Run a deep-dive analysis for a specific technology."""

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from enterprise_skills_lib.sensing.deep_dive import run_deep_dive


async def main():
    parser = argparse.ArgumentParser(description="Deep dive into a technology")
    parser.add_argument("--technology", required=True, help="Technology name to analyze")
    parser.add_argument("--domain", default="Generative AI", help="Technology domain")
    parser.add_argument("--user-id", default="default", help="User identifier")
    args = parser.parse_args()

    result = await run_deep_dive(
        technology_name=args.technology,
        domain=args.domain,
    )

    output_dir = os.path.join("data", args.user_id, "sensing")
    os.makedirs(output_dir, exist_ok=True)
    safe_name = args.technology.lower().replace(" ", "_")[:30]
    output_path = os.path.join(output_dir, f"deep_dive_{safe_name}.json")

    report_data = result.model_dump(mode="json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"Deep dive saved to: {output_path}")
    print(json.dumps({
        "status": "success",
        "technology": args.technology,
        "output_path": output_path,
    }))


if __name__ == "__main__":
    asyncio.run(main())
