#!/usr/bin/env python3
"""Convert any skill output JSON into a PPTX deck using the appropriate adapter."""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))


def main():
    parser = argparse.ArgumentParser(description="Convert skill output to PPTX")
    parser.add_argument("--skill", required=True,
                        choices=["tech_sensing", "competitive", "patent", "regulation", "talent", "brief"])
    parser.add_argument("--input", required=True, help="Path to skill output JSON")
    parser.add_argument("--output", required=True, help="Output PPTX path")
    parser.add_argument("--template", default="executive", choices=["executive", "detailed", "briefing"])
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    if args.skill == "tech_sensing":
        from sensing_adapter import build_sensing_deck
        output = build_sensing_deck(data, args.output, template=args.template)
    else:
        # Generic adapter for other skills
        from pptx_engine import (
            add_content_slide,
            add_title_slide,
            create_presentation,
            save_presentation,
        )
        prs = create_presentation()
        title = data.get("report_title", data.get("brief_title", f"{args.skill.title()} Report"))
        add_title_slide(prs, title, data.get("domain", ""))

        # Extract common fields as slides
        for key in ["key_findings", "recommendations", "recommended_actions"]:
            items = data.get(key, [])
            if items:
                bullets = []
                for item in items[:8]:
                    if isinstance(item, dict):
                        bullets.append(str(item.get("action", item.get("text", item.get("recommendation", str(item))))))
                    else:
                        bullets.append(str(item))
                add_content_slide(prs, key.replace("_", " ").title(), bullets)

        output = save_presentation(prs, args.output)

    slide_count = len(json.loads(json.dumps({"p": "count"})))  # placeholder
    print(f"Deck saved to: {output}")
    print(json.dumps({"status": "success", "output": output, "skill": args.skill}))


if __name__ == "__main__":
    main()
