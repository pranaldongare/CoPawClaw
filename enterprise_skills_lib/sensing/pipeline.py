"""
Tech Sensing Pipeline — orchestrates Ingest -> Dedup -> Extract -> Classify -> Report -> Verify -> Movement.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, List, Optional

from enterprise_skills_lib.llm.output_schemas.sensing import TechSensingReport
from enterprise_skills_lib.sensing.classify import classify_articles
from enterprise_skills_lib.sensing.config import DEFAULT_DOMAIN, LOOKBACK_DAYS
from enterprise_skills_lib.sensing.dedup import deduplicate_articles
from enterprise_skills_lib.sensing.ingest import (
    RawArticle,
    extract_full_text,
    fetch_rss_feeds,
    search_duckduckgo,
)
from enterprise_skills_lib.sensing.movement import detect_radar_movements
from enterprise_skills_lib.sensing.report_generator import generate_report
from enterprise_skills_lib.sensing.signal_score import compute_signal_strengths
from enterprise_skills_lib.sensing.sources.arxiv_search import fetch_arxiv_papers
from enterprise_skills_lib.sensing.sources.github_trending import fetch_github_trending
from enterprise_skills_lib.sensing.sources.hackernews import fetch_hackernews
from enterprise_skills_lib.sensing.verifier import verify_report

logger = logging.getLogger("sensing.pipeline")


@dataclass
class SensingPipelineResult:
    """Result of a complete tech sensing run."""
    report: TechSensingReport
    raw_article_count: int
    deduped_article_count: int
    classified_article_count: int
    execution_time_seconds: float


async def run_sensing_pipeline(
    domain: str = DEFAULT_DOMAIN,
    custom_requirements: str = "",
    feed_urls: Optional[List[str]] = None,
    search_queries: Optional[List[str]] = None,
    must_include: Optional[List[str]] = None,
    dont_include: Optional[List[str]] = None,
    lookback_days: int = LOOKBACK_DAYS,
    progress_callback: Optional[Callable] = None,
    user_id: Optional[str] = None,
    key_people: Optional[List[str]] = None,
) -> SensingPipelineResult:
    """Full tech sensing pipeline execution."""
    start = time.time()

    async def _emit(stage: str, pct: int, msg: str = ""):
        if progress_callback:
            await progress_callback(stage, pct, msg)

    keyword_instructions = _build_keyword_instructions(domain, must_include, dont_include)
    full_requirements = custom_requirements
    if keyword_instructions:
        full_requirements = f"{custom_requirements}\n\n{keyword_instructions}" if custom_requirements else keyword_instructions

    # Stage 1: Ingest (5 sources)
    await _emit("ingest", 10, "Fetching RSS feeds...")
    rss_articles = await fetch_rss_feeds(feed_urls, lookback_days=lookback_days, domain=domain)

    await _emit("ingest", 18, "Searching DuckDuckGo...")
    ddg_articles = await search_duckduckgo(search_queries, domain, lookback_days=lookback_days, must_include=must_include)

    await _emit("ingest", 19, "Searching GitHub trending...")
    github_articles = await fetch_github_trending(domain, lookback_days=lookback_days)

    await _emit("ingest", 20, "Searching arXiv...")
    arxiv_articles = await fetch_arxiv_papers(domain, lookback_days=lookback_days, must_include=must_include)

    await _emit("ingest", 21, "Searching Hacker News...")
    hn_articles = await fetch_hackernews(domain, lookback_days=lookback_days)

    all_raw = rss_articles + ddg_articles + github_articles + arxiv_articles + hn_articles
    await _emit("ingest", 22, f"Found {len(all_raw)} raw articles from 5 sources")
    logger.info(f"[Stage 1/7] INGEST COMPLETE: {len(all_raw)} total raw articles")

    # Stage 2: Dedup
    await _emit("dedup", 25, "Deduplicating...")
    unique_articles = deduplicate_articles(all_raw)

    if dont_include:
        dont_lower = [kw.lower() for kw in dont_include]
        unique_articles = [a for a in unique_articles if not _matches_exclusion(a, dont_lower)]

    await _emit("dedup", 30, f"{len(unique_articles)} unique articles")

    # Stage 3: Extract full text
    await _emit("extract", 35, "Extracting article text...")
    sem = asyncio.Semaphore(5)

    async def _extract_with_sem(article: RawArticle) -> RawArticle:
        async with sem:
            return await extract_full_text(article)

    enriched = await asyncio.gather(*[_extract_with_sem(a) for a in unique_articles])
    await _emit("extract", 45, "Text extraction complete")

    # Stage 4: Classify
    await _emit("classify", 50, "Classifying articles with LLM...")
    classified = await classify_articles(
        list(enriched), domain=domain, custom_requirements=full_requirements, key_people=key_people,
    )
    await _emit("classify", 65, f"{len(classified)} articles classified")

    url_content_map = {
        a.url: (a.content or "")[:800]
        for a in enriched if a.url and a.content and len(a.content) > 50
    }

    # Stage 5: Generate report
    await _emit("report", 70, "Generating report with LLM...")
    now = datetime.now(timezone.utc)
    if lookback_days > 0:
        lookback_start = now - timedelta(days=lookback_days)
        date_range = f"{lookback_start.strftime('%b %d')} - {now.strftime('%b %d, %Y')}"
    else:
        date_range = f"All time (as of {now.strftime('%b %d, %Y')})"

    org_context_str = ""
    if user_id:
        try:
            from enterprise_skills_lib.sensing.org_context import build_org_context_prompt, load_org_context
            org_ctx = await load_org_context(user_id)
            if org_ctx:
                org_context_str = build_org_context_prompt(org_ctx)
        except Exception:
            pass

    report = await generate_report(
        classified_articles=classified, domain=domain, date_range=date_range,
        custom_requirements=full_requirements, org_context=org_context_str,
        article_content_map=url_content_map, key_people=key_people,
    )
    await _emit("report", 85, "Report generated, verifying relevance...")

    # Stage 6: Verify relevance
    await _emit("verify", 88, "Verifying report relevance...")
    report = await verify_report(report=report, domain=domain, must_include=must_include, dont_include=dont_include)
    await _emit("verify", 92, "Verification complete")

    # Stage 7: Movement detection
    if user_id:
        await _emit("movement", 95, "Detecting technology movements...")
        report = await detect_radar_movements(new_report=report, user_id=user_id, domain=domain)

    # Signal strength scoring
    await _emit("scoring", 98, "Computing signal strengths...")
    report = compute_signal_strengths(report, classified)

    await _emit("complete", 100, "Report ready")

    elapsed = time.time() - start
    logger.info(f"========== SENSING PIPELINE COMPLETE in {elapsed:.1f}s ==========")

    return SensingPipelineResult(
        report=report,
        raw_article_count=len(all_raw),
        deduped_article_count=len(unique_articles),
        classified_article_count=len(classified),
        execution_time_seconds=round(elapsed, 2),
    )


def _matches_exclusion(article: RawArticle, dont_lower: list[str]) -> bool:
    text = f"{article.title} {article.snippet} {article.content}".lower()
    return any(kw in text for kw in dont_lower)


def _build_keyword_instructions(domain: str, must_include: list[str] | None, dont_include: list[str] | None) -> str:
    parts = []
    if must_include:
        parts.append(f"MUST INCLUDE: Prioritize articles related to: {', '.join(must_include)}.")
    if dont_include:
        parts.append(f"DON'T INCLUDE: Exclude articles related to: {', '.join(dont_include)}.")
    return "\n".join(parts)
