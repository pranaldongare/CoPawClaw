#!/usr/bin/env python3
"""Compare two sensing reports to identify changes."""

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from enterprise_skills_lib.llm.output_schemas.sensing import TechSensingReport
from enterprise_skills_lib.sensing.comparison import compare_reports


def _load_report(user_id: str, tracking_id: str) -> TechSensingReport:
    """Load a report by tracking ID."""
    path = os.path.join("data", user_id, "sensing", f"report_{tracking_id}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Report not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_meta", None)
    return TechSensingReport.model_validate(data)


def main():
    parser = argparse.ArgumentParser(description="Compare two sensing reports")
    parser.add_argument("--report-a", required=True, help="Tracking ID of first report")
    parser.add_argument("--report-b", required=True, help="Tracking ID of second report")
    parser.add_argument("--user-id", default="default", help="User identifier")
    args = parser.parse_args()

    report_a = _load_report(args.user_id, args.report_a)
    report_b = _load_report(args.user_id, args.report_b)

    comparison = compare_reports(report_a, report_b)

    output_dir = os.path.join("data", args.user_id, "sensing")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"comparison_{args.report_a}_vs_{args.report_b}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comparison.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    print(f"Comparison saved to: {output_path}")
    print(json.dumps({
        "status": "success",
        "output_path": output_path,
        "radar_changes": {
            "added": len(comparison.radar_diff.added),
            "removed": len(comparison.radar_diff.removed),
            "moved": len(comparison.radar_diff.moved),
            "unchanged": len(comparison.radar_diff.unchanged),
        },
    }))


if __name__ == "__main__":
    main()
