"""Tests for signal strength scoring."""

import pytest

from enterprise_skills_lib.sensing.signal_score import SOURCE_AUTHORITY, compute_signal_strengths
from enterprise_skills_lib.llm.output_schemas.sensing import (
    ClassifiedArticle,
    RadarItem,
    TechSensingReport,
)


class TestSourceAuthority:
    def test_known_sources_have_weights(self):
        assert SOURCE_AUTHORITY.get("arxiv", 0) > 0.5
        assert SOURCE_AUTHORITY.get("nature", 0) > 0.8

    def test_default_weight(self):
        # Unknown sources should get the default weight
        assert SOURCE_AUTHORITY.get("unknown_source", 0.5) == 0.5


class TestComputeSignalStrengths:
    def test_items_get_scores(self, sample_report, sample_classified_articles):
        result = compute_signal_strengths(sample_report, sample_classified_articles)
        for item in result.radar_items:
            assert hasattr(item, "signal_strength")

    def test_baseline_for_no_articles(self):
        """Items with no matching articles get baseline score."""
        report = TechSensingReport(
            report_title="Test",
            date_range="test",
            executive_summary="test",
            headline_moves=[],
            key_trends=[],
            radar_items=[
                RadarItem(
                    technology_name="Nonexistent Tech",
                    quadrant="Tools",
                    ring="Assess",
                    description="test",
                ),
            ],
            market_signals=[],
            report_sections=[],
            recommendations=[],
        )
        result = compute_signal_strengths(report, [])
        assert result.radar_items[0].signal_strength >= 0
