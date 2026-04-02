"""
Report verifier — filters off-topic content from the generated report.
Uses a lightweight LLM call to check each item against the user's domain.
"""

import json
import logging
import time
from typing import List

from pydantic import Field

from enterprise_skills_lib.constants import GPU_SENSING_CLASSIFY_LLM
from enterprise_skills_lib.llm.client import invoke_llm
from enterprise_skills_lib.llm.output_schemas.base import LLMOutputBase
from enterprise_skills_lib.llm.output_schemas.sensing import TechSensingReport

logger = logging.getLogger("sensing.verifier")


class VerifiedItems(LLMOutputBase):
    """LLM output: lists of item names/titles that are on-topic + attribution warnings."""
    relevant_radar_items: List[str] = Field(description="Names of radar items that are directly relevant.")
    relevant_market_signals: List[str] = Field(description="Company names of relevant market signals.")
    relevant_trends: List[str] = Field(description="Names of relevant trends.")
    attribution_warnings: List[str] = Field(
        default_factory=list,
        description="Warnings about potential misattributions. Format: 'technology_name: entity_to_remove | reason'.",
    )


async def verify_report(
    report: TechSensingReport,
    domain: str,
    must_include: list[str] | None = None,
    dont_include: list[str] | None = None,
) -> TechSensingReport:
    """Verify report content against the user's domain and filter off-topic items."""
    verify_start = time.time()

    radar_names = [item.name for item in report.radar_items]
    signal_companies = [s.company_or_player for s in report.market_signals]
    trend_names = [t.trend_name for t in report.key_trends]

    detail_key_players = {d.technology_name: d.key_players for d in report.radar_item_details}

    items_summary = {
        "radar_items": [
            {"name": item.name, "description": item.description, "key_players": detail_key_players.get(item.name, [])}
            for item in report.radar_items
        ],
        "market_signals": [
            {"company": s.company_or_player, "signal": s.signal} for s in report.market_signals
        ],
        "trends": [
            {"name": t.trend_name, "description": t.description} for t in report.key_trends
        ],
    }

    must_str = f"\nMust-include keywords: {', '.join(must_include)}" if must_include else ""
    dont_str = f"\nDon't-include keywords: {', '.join(dont_include)}" if dont_include else ""

    prompt = [
        {
            "role": "system",
            "parts": (
                f"You are a relevance checker for a tech sensing report about '{domain}'.\n\n"
                "Review each item and determine if it is DIRECTLY relevant "
                f"to '{domain}'.\n\n"
                "STRICT RELEVANCE CRITERIA:\n"
                f"- Items must be specifically about or closely related to '{domain}'\n"
                "- General industry news that only tangentially mentions the domain should be EXCLUDED\n"
                + must_str + dont_str + "\n\n"
                "ATTRIBUTION CHECK:\n"
                "- Flag cases where a company is listed as key_player but only published research.\n"
                "- Format: 'technology_name: entity_to_remove | reason'\n\n"
                "OUTPUT RULES:\n"
                "- Return ONLY a valid JSON object with keys: relevant_radar_items, "
                "relevant_market_signals, relevant_trends, attribution_warnings.\n"
                "- List ONLY the names/companies of items that pass the relevance check.\n"
            ),
        },
        {
            "role": "user",
            "parts": (
                f"DOMAIN: {domain}\n\n"
                f"ITEMS TO VERIFY:\n{json.dumps(items_summary, indent=2, ensure_ascii=False)}\n\n"
                "Return ONLY the names of items that are directly relevant. Be strict."
            ),
        },
    ]

    try:
        result = await invoke_llm(
            gpu_model=GPU_SENSING_CLASSIFY_LLM.model,
            response_schema=VerifiedItems,
            contents=prompt,
            port=GPU_SENSING_CLASSIFY_LLM.port,
        )

        verified = VerifiedItems.model_validate(result)

        relevant_radar = set(verified.relevant_radar_items)
        relevant_signals = set(verified.relevant_market_signals)
        relevant_trends = set(verified.relevant_trends)

        report.radar_items = [item for item in report.radar_items if item.name in relevant_radar]
        report.radar_item_details = [item for item in report.radar_item_details if item.technology_name in relevant_radar]
        report.market_signals = [s for s in report.market_signals if s.company_or_player in relevant_signals]
        report.key_trends = [t for t in report.key_trends if t.trend_name in relevant_trends]

        if report.notable_articles:
            report.notable_articles = [a for a in report.notable_articles if a.technology_name in relevant_radar]

        # Apply attribution warnings
        if verified.attribution_warnings:
            for warning in verified.attribution_warnings:
                if ":" in warning and "|" in warning:
                    tech_part, rest = warning.split(":", 1)
                    entity_part = rest.split("|", 1)[0].strip()
                    tech_name = tech_part.strip()
                    for detail in report.radar_item_details:
                        if detail.technology_name == tech_name:
                            detail.key_players = [
                                p for p in detail.key_players if p.lower() != entity_part.lower()
                            ]

        elapsed = time.time() - verify_start
        logger.info(f"Verification complete in {elapsed:.1f}s")

    except Exception as e:
        logger.warning(f"Verification failed (keeping original report): {e}")

    return report
