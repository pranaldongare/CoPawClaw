"""Prompt templates for Competitive Intelligence skill."""


def competitive_analysis_prompt(
    articles_text: str,
    companies: list[str],
    domain: str = "Generative AI",
    custom_requirements: str = "",
) -> list[dict]:
    """Build a prompt to analyze competitive landscape from articles."""
    companies_str = ", ".join(companies)
    return [
        {
            "role": "system",
            "parts": (
                f"You are a senior competitive intelligence analyst specializing in {domain}.\n\n"
                f"Analyze the following articles to build a competitive landscape for these companies: {companies_str}.\n\n"
                "For each company, determine:\n"
                "1. Recent events (product launches, funding, partnerships, acquisitions, key hires)\n"
                "2. Market position (Leader/Challenger/Niche/Emerging)\n"
                "3. Key strengths and weaknesses\n"
                "4. Threat level with reasoning\n\n"
                "Also produce:\n"
                "- A competitive matrix comparing companies across key dimensions\n"
                "- Strategic moves analysis with assessed intent\n"
                "- Opportunity gaps in the market\n"
                "- SWOT synthesis narrative\n"
                "- Actionable recommendations\n\n"
                "GROUNDING RULES:\n"
                "- Every claim MUST be grounded in the provided articles.\n"
                "- Use article URLs for source_urls.\n"
                "- Do NOT fabricate information.\n\n"
                "OUTPUT: Return ONLY a valid JSON object matching the CompetitiveReport schema.\n"
                + (f"\nADDITIONAL REQUIREMENTS:\n{custom_requirements}\n" if custom_requirements else "")
            ),
        },
        {
            "role": "user",
            "parts": (
                f"DOMAIN: {domain}\nCOMPANIES: {companies_str}\n\n"
                f"ARTICLES:\n\n{articles_text}\n\n"
                "Generate the competitive analysis. Return ONLY valid JSON."
            ),
        },
    ]


def company_tracking_prompt(
    articles_text: str,
    company: str,
    aspects: list[str],
    domain: str = "Generative AI",
) -> list[dict]:
    """Build a prompt for focused single-company tracking."""
    aspects_str = ", ".join(aspects)
    return [
        {
            "role": "system",
            "parts": (
                f"You are a competitive intelligence analyst tracking {company} in the {domain} space.\n\n"
                f"Focus on these aspects: {aspects_str}.\n\n"
                "Provide a detailed CompetitorProfile with all recent events, products, strengths, weaknesses.\n"
                "Return ONLY a valid JSON object.\n"
            ),
        },
        {
            "role": "user",
            "parts": (
                f"ARTICLES ABOUT {company.upper()}:\n\n{articles_text}\n\n"
                "Generate the company profile. Return ONLY valid JSON."
            ),
        },
    ]
