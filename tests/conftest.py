"""Shared test fixtures for the CoPaw Enterprise Skills Platform."""

import os
import sys

import pytest

# Ensure enterprise_skills_lib is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def sample_raw_articles():
    """10 diverse RawArticle instances for testing."""
    from enterprise_skills_lib.sensing.ingest import RawArticle

    return [
        RawArticle(
            title=f"Test Article {i}: {'AI' if i % 2 == 0 else 'ML'} Breakthrough",
            url=f"https://example.com/article-{i}",
            source=["TechCrunch", "arXiv", "Hacker News", "GitHub", "VentureBeat"][i % 5],
            published_date="2026-04-01",
            snippet=f"This is a test snippet for article {i} about technology.",
            content=f"Full content for article {i}. " * 20,
        )
        for i in range(10)
    ]


@pytest.fixture
def sample_classified_articles():
    """10 ClassifiedArticle instances with varied quadrants/rings."""
    from enterprise_skills_lib.llm.output_schemas.sensing import ClassifiedArticle

    quadrants = ["Techniques", "Platforms", "Tools", "Languages & Frameworks"]
    rings = ["Adopt", "Trial", "Assess", "Hold"]

    return [
        ClassifiedArticle(
            title=f"Classified Article {i}",
            source="Test",
            url=f"https://example.com/{i}",
            published_date="2026-04-01",
            summary=f"Summary of article {i}.",
            relevance_score=0.5 + (i * 0.05),
            quadrant=quadrants[i % 4],
            ring=rings[i % 4],
            technology_name=f"Tech-{i}",
            reasoning=f"Reasoning for article {i}.",
        )
        for i in range(10)
    ]


@pytest.fixture
def sample_report(sample_classified_articles):
    """Complete TechSensingReport for testing comparison, movement, timeline."""
    from enterprise_skills_lib.llm.output_schemas.sensing import (
        HeadlineMove,
        MarketSignal,
        RadarItem,
        Recommendation,
        ReportSection,
        TechSensingReport,
        TrendItem,
    )

    return TechSensingReport(
        report_title="Test Sensing Report",
        date_range="Apr 01 - Apr 07, 2026",
        executive_summary="This is a test executive summary for the report.",
        headline_moves=[
            HeadlineMove(
                actor="OpenAI",
                move="Released GPT-5",
                headline="OpenAI launches GPT-5",
                segment="Frontier Labs",
                source_urls=["https://example.com/1"],
            ),
        ],
        key_trends=[
            TrendItem(
                trend_name="Agent Frameworks",
                description="Rise of multi-agent systems",
                evidence=["MCP adoption growing", "CoPaw reaches 14K stars"],
                impact_level="High",
            ),
        ],
        radar_items=[
            RadarItem(
                technology_name=f"Tech-{i}",
                quadrant=["Techniques", "Platforms", "Tools", "Languages & Frameworks"][i % 4],
                ring=["Adopt", "Trial", "Assess", "Hold"][i % 4],
                description=f"Description of Tech-{i}",
            )
            for i in range(5)
        ],
        market_signals=[
            MarketSignal(
                player="Google",
                signal="Investing heavily in AI infrastructure",
                industry_impact="High",
            ),
        ],
        report_sections=[
            ReportSection(
                section_title="AI Agents",
                content="Analysis of the agent ecosystem.",
            ),
        ],
        recommendations=[
            Recommendation(
                recommendation="Evaluate MCP for tool integration",
                priority="High",
            ),
        ],
    )


@pytest.fixture
def tmp_data_dir(tmp_path):
    """Create a temporary data directory structure."""
    data_dir = tmp_path / "data" / "testuser" / "sensing"
    data_dir.mkdir(parents=True)
    return tmp_path
