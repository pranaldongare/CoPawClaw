#!/usr/bin/env python3
"""Generate a PPTX deck from any JSON input with schema hint."""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from pptx_engine import (
    add_content_slide,
    add_table_slide,
    add_title_slide,
    create_presentation,
    save_presentation,
)


def main():
    parser = argparse.ArgumentParser(description="Generate PPTX from JSON")
    parser.add_argument("--input", required=True, help="Input JSON file path")
    parser.add_argument("--schema", default="auto",
                        help="Schema hint: tech_sensing|competitive|patent|regulation|talent|brief|auto")
    parser.add_argument("--output", required=True, help="Output PPTX path")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Auto-detect schema from data keys
    schema = args.schema
    if schema == "auto":
        if "radar_items" in data:
            schema = "tech_sensing"
        elif "competitor_profiles" in data:
            schema = "competitive"
        elif "key_filings" in data:
            schema = "patent"
        elif "regulatory_updates" in data:
            schema = "regulation"
        elif "key_moves" in data:
            schema = "talent"
        elif "risk_opportunity_matrix" in data:
            schema = "brief"

    if schema == "tech_sensing":
        from sensing_adapter import build_sensing_deck
        output = build_sensing_deck(data, args.output)
    else:
        # Generic rendering
        prs = create_presentation()
        title = data.get("report_title", data.get("brief_title", "Report"))
        add_title_slide(prs, title, data.get("domain", ""))

        # Render list fields as slides
        for key, value in data.items():
            if isinstance(value, list) and value and len(value) <= 20:
                bullets = []
                for item in value[:8]:
                    if isinstance(item, dict):
                        # Take the first string value as the bullet
                        text_vals = [v for v in item.values() if isinstance(v, str) and len(v) > 3]
                        bullets.append(text_vals[0][:100] if text_vals else str(item)[:100])
                    elif isinstance(item, str):
                        bullets.append(item[:100])
                if bullets:
                    add_content_slide(prs, key.replace("_", " ").title(), bullets)

            elif isinstance(value, str) and len(value) > 50:
                sentences = [s.strip() for s in value.split(". ") if s.strip()][:6]
                if sentences:
                    add_content_slide(prs, key.replace("_", " ").title(), sentences)

        output = save_presentation(prs, args.output)

    print(f"Deck saved to: {output}")
    print(json.dumps({"status": "success", "output": output, "schema": schema}))


if __name__ == "__main__":
    main()
