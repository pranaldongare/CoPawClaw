"""Tests for report comparison/diffing."""

import pytest

from enterprise_skills_lib.llm.output_schemas.sensing import (
    RadarItem,
    TechSensingReport,
    TrendItem,
)
from enterprise_skills_lib.sensing.comparison import compare_reports


def _make_report(radar_items: list[RadarItem], trends: list[TrendItem] | None = None) -> TechSensingReport:
    return TechSensingReport(
        report_title="Test",
        date_range="test",
        executive_summary="test",
        headline_moves=[],
        key_trends=trends or [],
        radar_items=radar_items,
        market_signals=[],
        report_sections=[],
        recommendations=[],
    )


class TestCompareReports:
    def test_detects_added_items(self):
        report_a = _make_report([
            RadarItem(technology_name="Tech-A", quadrant="Tools", ring="Assess", description=""),
        ])
        report_b = _make_report([
            RadarItem(technology_name="Tech-A", quadrant="Tools", ring="Assess", description=""),
            RadarItem(technology_name="Tech-B", quadrant="Tools", ring="Trial", description=""),
        ])
        result = compare_reports(report_a, report_b)
        assert len(result.radar_diff.added) == 1
        assert result.radar_diff.added[0].technology_name == "Tech-B"

    def test_detects_removed_items(self):
        report_a = _make_report([
            RadarItem(technology_name="Tech-A", quadrant="Tools", ring="Assess", description=""),
            RadarItem(technology_name="Tech-B", quadrant="Tools", ring="Trial", description=""),
        ])
        report_b = _make_report([
            RadarItem(technology_name="Tech-A", quadrant="Tools", ring="Assess", description=""),
        ])
        result = compare_reports(report_a, report_b)
        assert len(result.radar_diff.removed) == 1

    def test_detects_moved_items(self):
        report_a = _make_report([
            RadarItem(technology_name="Tech-A", quadrant="Tools", ring="Assess", description=""),
        ])
        report_b = _make_report([
            RadarItem(technology_name="Tech-A", quadrant="Tools", ring="Trial", description=""),
        ])
        result = compare_reports(report_a, report_b)
        assert len(result.radar_diff.moved) == 1

    def test_detects_unchanged_items(self):
        items = [RadarItem(technology_name="Tech-A", quadrant="Tools", ring="Assess", description="")]
        report_a = _make_report(items)
        report_b = _make_report(items)
        result = compare_reports(report_a, report_b)
        assert len(result.radar_diff.unchanged) == 1

    def test_empty_reports(self):
        report_a = _make_report([])
        report_b = _make_report([])
        result = compare_reports(report_a, report_b)
        assert len(result.radar_diff.added) == 0
        assert len(result.radar_diff.removed) == 0
