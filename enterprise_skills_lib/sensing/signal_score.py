"""
Signal Strength Scoring — computes composite confidence for each radar item.
"""

import logging
from typing import List

from enterprise_skills_lib.llm.output_schemas.sensing import (
    ClassifiedArticle,
    TechSensingReport,
)

logger = logging.getLogger("sensing.signal_score")

SOURCE_AUTHORITY: dict[str, float] = {
    "arXiv": 0.9,
    "GitHub": 0.85,
    "Hacker News": 0.7,
    "MIT Technology Review": 0.9,
    "TechCrunch": 0.8,
    "VentureBeat": 0.75,
    "The Verge": 0.7,
    "Ars Technica": 0.75,
    "IEEE Spectrum": 0.85,
    "Nature": 0.95,
    "Science": 0.95,
}
DEFAULT_AUTHORITY = 0.5


def compute_signal_strengths(
    report: TechSensingReport,
    classified_articles: List[ClassifiedArticle],
) -> TechSensingReport:
    """Compute signal_strength for each radar item based on supporting articles."""
    article_map: dict[str, list[ClassifiedArticle]] = {}
    for article in classified_articles:
        key = article.technology_name.lower().strip()
        article_map.setdefault(key, []).append(article)

    scored = 0
    for item in report.radar_items:
        key = item.name.lower().strip()
        supporting = article_map.get(key, [])

        if not supporting:
            item.signal_strength = 0.2
            item.source_count = 0
            continue

        sources = set(a.source for a in supporting)
        source_count = len(sources)

        authority_scores = [SOURCE_AUTHORITY.get(a.source, DEFAULT_AUTHORITY) for a in supporting]
        avg_authority = sum(authority_scores) / len(authority_scores)
        avg_relevance = sum(a.relevance_score for a in supporting) / len(supporting)

        diversity_score = min(source_count / 4.0, 1.0)
        strength = 0.4 * avg_authority + 0.3 * diversity_score + 0.3 * avg_relevance
        strength = max(0.0, min(1.0, strength))

        item.signal_strength = round(strength, 2)
        item.source_count = source_count
        scored += 1

    logger.info(f"Signal scoring: {scored}/{len(report.radar_items)} items scored")
    return report
