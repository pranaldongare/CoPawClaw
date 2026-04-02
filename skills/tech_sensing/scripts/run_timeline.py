#!/usr/bin/env python3
"""Build technology timelines from historical reports."""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from enterprise_skills_lib.llm.output_schemas.sensing import TechSensingReport
from enterprise_skills_lib.sensing.timeline import build_timeline


def main():
    parser = argparse.ArgumentParser(description="Build technology timeline")
    parser.add_argument("--user-id", default="default", help="User identifier")
    parser.add_argument("--domain", default="Generative AI", help="Filter by domain")
    args = parser.parse_args()

    # Load all reports for this user
    reports_dir = os.path.join("data", args.user_id, "sensing")
    if not os.path.isdir(reports_dir):
        print(json.dumps({"status": "error", "message": "No reports found"}))
        return

    reports = []
    for fname in sorted(os.listdir(reports_dir)):
        if not fname.startswith("report_") or not fname.endswith(".json"):
            continue
        fpath = os.path.join(reports_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            data.pop("_meta", None)
            reports.append(TechSensingReport.model_validate(data))
        except Exception as e:
            print(f"Warning: skipping {fname}: {e}", file=sys.stderr)

    if not reports:
        print(json.dumps({"status": "error", "message": "No valid reports found"}))
        return

    timelines = build_timeline(reports)

    output_path = os.path.join(reports_dir, "timeline.json")
    timeline_data = [t.model_dump(mode="json") for t in timelines]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(timeline_data, f, indent=2, ensure_ascii=False)

    print(f"Timeline saved to: {output_path}")
    print(json.dumps({
        "status": "success",
        "output_path": output_path,
        "technologies_tracked": len(timelines),
        "reports_analyzed": len(reports),
    }))


if __name__ == "__main__":
    main()
