"""Integration tests for data ingestion (requires network access)."""

import pytest

from enterprise_skills_lib.sensing.ingest import RawArticle, fetch_rss_feeds, search_duckduckgo
from enterprise_skills_lib.sensing.sources.arxiv_search import fetch_arxiv_papers
from enterprise_skills_lib.sensing.sources.github_trending import fetch_github_trending
from enterprise_skills_lib.sensing.sources.hackernews import fetch_hackernews


@pytest.mark.asyncio
@pytest.mark.integration
async def test_fetch_hackernews():
    """HN API should return articles."""
    articles = await fetch_hackernews("artificial intelligence", lookback_days=7, max_results=5)
    assert isinstance(articles, list)
    # May be empty if API is down, but should not raise
    for a in articles:
        assert isinstance(a, RawArticle)
        assert a.source == "Hacker News"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_fetch_github_trending():
    """GitHub API should return repos."""
    articles = await fetch_github_trending("machine learning", lookback_days=30, max_results=5)
    assert isinstance(articles, list)
    for a in articles:
        assert isinstance(a, RawArticle)
        assert a.source == "GitHub"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_fetch_arxiv_papers():
    """arXiv API should return papers."""
    articles = await fetch_arxiv_papers("large language models", lookback_days=30, max_results=5)
    assert isinstance(articles, list)
    for a in articles:
        assert isinstance(a, RawArticle)
        assert a.source == "arXiv"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_search_duckduckgo():
    """DDG search should return results."""
    articles = await search_duckduckgo(
        ["artificial intelligence news"], "AI", lookback_days=7
    )
    assert isinstance(articles, list)
    for a in articles:
        assert isinstance(a, RawArticle)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_fetch_rss_feeds():
    """RSS fetch should return articles."""
    feeds = ["https://feeds.arstechnica.com/arstechnica/technology-lab"]
    articles = await fetch_rss_feeds(feeds, lookback_days=30)
    assert isinstance(articles, list)
    for a in articles:
        assert isinstance(a, RawArticle)
