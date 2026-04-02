"""
Adapter: Tech Sensing report -> PPTX slides.
"""

from pptx_engine import (
    add_content_slide,
    add_table_slide,
    add_title_slide,
    add_two_column_slide,
    create_presentation,
    save_presentation,
)


def build_sensing_deck(data: dict, output_path: str, template: str = "executive") -> str:
    """Convert a tech sensing report JSON into a PPTX deck."""
    prs = create_presentation()

    # 1. Title slide
    title = data.get("report_title", "Tech Sensing Report")
    meta = data.get("_meta", {})
    subtitle = f"{meta.get('domain', '')} | {data.get('date_range', '')}"
    add_title_slide(prs, title, subtitle)

    # 2. Executive summary
    exec_summary = data.get("executive_summary", "")
    if exec_summary:
        # Split into bullet-sized chunks
        sentences = [s.strip() for s in exec_summary.split(". ") if s.strip()]
        add_content_slide(prs, "Executive Summary", sentences[:6])

    # 3. Headline moves
    moves = data.get("headline_moves", [])
    if moves:
        bullets = []
        for m in moves[:7]:
            if isinstance(m, dict):
                bullets.append(f"{m.get('actor', '')} — {m.get('move', m.get('headline', ''))}")
            else:
                bullets.append(str(m))
        add_content_slide(prs, "Headline Moves", bullets)

    # 4. Technology Radar summary
    radar_items = data.get("radar_items", [])
    if radar_items:
        quadrants = {}
        for item in radar_items:
            if isinstance(item, dict):
                q = item.get("quadrant", "Other")
                quadrants.setdefault(q, []).append(
                    f"{item.get('technology_name', '?')} ({item.get('ring', '?')})"
                )

        for quadrant, items in list(quadrants.items())[:4]:
            add_content_slide(prs, f"Radar: {quadrant}", items[:8])

    # 5. Key trends
    trends = data.get("key_trends", [])
    if trends:
        for trend in trends[:3]:
            if isinstance(trend, dict):
                name = trend.get("trend_name", trend.get("name", "Trend"))
                desc = trend.get("description", "")
                evidence = trend.get("evidence", [])
                bullets = [desc] if desc else []
                if isinstance(evidence, list):
                    bullets.extend(str(e) for e in evidence[:3])
                add_content_slide(prs, name, bullets, subtitle=trend.get("impact_level", ""))

    # 6. Market signals
    signals = data.get("market_signals", [])
    if signals:
        headers = ["Company", "Signal", "Impact"]
        rows = []
        for sig in signals[:8]:
            if isinstance(sig, dict):
                rows.append([
                    sig.get("company", sig.get("player", "")),
                    sig.get("signal", sig.get("move", ""))[:60],
                    sig.get("industry_impact", sig.get("impact", "")),
                ])
        if rows:
            add_table_slide(prs, "Market Signals", headers, rows)

    # 7. Recommendations
    recs = data.get("recommendations", [])
    if recs:
        bullets = []
        for r in recs[:6]:
            if isinstance(r, dict):
                bullets.append(f"[{r.get('priority', 'Medium')}] {r.get('recommendation', r.get('text', ''))}")
            else:
                bullets.append(str(r))
        add_content_slide(prs, "Recommendations", bullets)

    return save_presentation(prs, output_path)
