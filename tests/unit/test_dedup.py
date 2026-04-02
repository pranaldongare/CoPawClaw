"""Tests for article deduplication."""

import pytest

from enterprise_skills_lib.sensing.dedup import (
    _is_title_duplicate,
    _normalize_url,
    deduplicate_articles,
)
from enterprise_skills_lib.sensing.ingest import RawArticle


class TestNormalizeUrl:
    def test_strips_utm_params(self):
        url = "https://example.com/article?utm_source=twitter&utm_medium=social&id=123"
        result = _normalize_url(url)
        assert "utm_source" not in result
        assert "id=123" in result

    def test_strips_trailing_slash(self):
        assert _normalize_url("https://example.com/path/") == _normalize_url("https://example.com/path")

    def test_strips_fragment(self):
        url = "https://example.com/article#section"
        result = _normalize_url(url)
        assert "#" not in result

    def test_lowercases(self):
        url = "https://EXAMPLE.COM/Article"
        result = _normalize_url(url)
        assert "example.com" in result


class TestIsTitleDuplicate:
    def test_exact_match(self):
        assert _is_title_duplicate("OpenAI launches GPT-5", ["OpenAI launches GPT-5"])

    def test_similar_titles(self):
        existing = ["OpenAI launches GPT-5 with major improvements"]
        assert _is_title_duplicate("OpenAI launches GPT-5 with significant improvements", existing)

    def test_different_titles(self):
        existing = ["Google announces Gemini 2.0"]
        assert not _is_title_duplicate("OpenAI launches GPT-5", existing)


class TestDeduplicateArticles:
    def test_removes_url_duplicates(self):
        articles = [
            RawArticle(title="Article 1", url="https://example.com/a?utm_source=x", source="A"),
            RawArticle(title="Article 2", url="https://example.com/a", source="B"),
        ]
        result = deduplicate_articles(articles)
        assert len(result) == 1

    def test_removes_title_duplicates(self):
        articles = [
            RawArticle(title="OpenAI launches GPT-5", url="https://a.com/1", source="A"),
            RawArticle(title="OpenAI launches GPT-5 model", url="https://b.com/2", source="B"),
        ]
        result = deduplicate_articles(articles)
        assert len(result) == 1

    def test_keeps_different_articles(self):
        articles = [
            RawArticle(title="Article about AI", url="https://a.com/1", source="A"),
            RawArticle(title="Article about quantum computing", url="https://b.com/2", source="B"),
        ]
        result = deduplicate_articles(articles)
        assert len(result) == 2

    def test_empty_input(self):
        assert deduplicate_articles([]) == []
