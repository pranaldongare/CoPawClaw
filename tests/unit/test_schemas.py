"""Tests for Pydantic schema validation."""

import pytest

from enterprise_skills_lib.llm.output_schemas.base import LLMOutputBase, SimpleTextOutput
from enterprise_skills_lib.llm.output_schemas.competitive import CompetitiveReport, CompetitorProfile
from enterprise_skills_lib.llm.output_schemas.executive import ExecutiveBrief, ActionItem
from enterprise_skills_lib.llm.output_schemas.patents import PatentReport, PatentFiling
from enterprise_skills_lib.llm.output_schemas.regulations import RegulationReport, RegulatoryUpdate
from enterprise_skills_lib.llm.output_schemas.sensing import (
    ClassifiedArticle,
    TechSensingReport,
    RadarItem,
)
from enterprise_skills_lib.llm.output_schemas.talent import TalentReport, KeyMove


class TestSimpleTextOutput:
    def test_basic(self):
        result = SimpleTextOutput(text="hello")
        assert result.text == "hello"


class TestClassifiedArticle:
    def test_valid(self):
        article = ClassifiedArticle(
            title="Test",
            source="arXiv",
            url="https://arxiv.org/123",
            published_date="2026-04-01",
            summary="A test article",
            relevance_score=0.8,
            quadrant="Tools",
            ring="Trial",
            technology_name="MCP",
            reasoning="Relevant to AI agents",
        )
        assert article.relevance_score == 0.8


class TestRadarItem:
    def test_valid(self):
        item = RadarItem(
            technology_name="GPT-5",
            quadrant="Platforms",
            ring="Adopt",
            description="Latest foundation model",
        )
        assert item.technology_name == "GPT-5"


class TestCompetitiveReport:
    def test_minimal(self):
        report = CompetitiveReport(
            report_title="Test",
            domain="AI",
            date_range="2026",
            competitor_profiles=[
                CompetitorProfile(company_name="OpenAI"),
            ],
        )
        assert len(report.competitor_profiles) == 1


class TestPatentReport:
    def test_minimal(self):
        report = PatentReport(
            report_title="Test",
            domain="LLMs",
            date_range="2026",
            key_filings=[
                PatentFiling(patent_id="US123", title="Test Patent"),
            ],
        )
        assert report.total_patents_analyzed == 0


class TestRegulationReport:
    def test_minimal(self):
        report = RegulationReport(
            report_title="Test",
            jurisdictions=["EU"],
            date_range="2026",
            regulatory_updates=[
                RegulatoryUpdate(
                    regulation_name="EU AI Act",
                    jurisdiction="EU",
                    summary="New AI regulation",
                ),
            ],
        )
        assert len(report.regulatory_updates) == 1


class TestTalentReport:
    def test_minimal(self):
        report = TalentReport(
            report_title="Test",
            date_range="2026",
            key_moves=[
                KeyMove(person_name="Jane Doe"),
            ],
        )
        assert len(report.key_moves) == 1


class TestExecutiveBrief:
    def test_minimal(self):
        brief = ExecutiveBrief(
            brief_title="Test Brief",
            domain="AI",
            date="2026-04-01",
            situation_summary="Current state.",
            key_findings=["Finding 1"],
            recommended_actions=[
                ActionItem(action="Do something"),
            ],
        )
        assert brief.domain == "AI"
