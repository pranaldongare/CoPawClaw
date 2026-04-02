"""
Prompt templates for Tech Sensing — classification, report skeleton, and radar details.
Adapted from source repo core/llm/prompts/sensing_prompts.py.
"""


def sensing_classify_prompt(
    articles_text: str,
    domain: str = "Generative AI",
    custom_requirements: str = "",
    key_people: list[str] | None = None,
) -> list[dict]:
    """Build a chat prompt to classify and summarize a batch of articles."""
    people_block = ""
    if key_people:
        names = ", ".join(key_people)
        people_block = (
            f"\nKEY PEOPLE WATCHLIST:\n"
            f"Pay special attention to articles mentioning these leaders: {names}.\n"
            "Boost relevance_score by ~0.1 for articles featuring their actions or statements.\n"
        )

    contents = [
        {
            "role": "system",
            "parts": (
                f"You are a senior technology analyst specializing in {domain}.\n\n"
                "Your task is to classify and summarize each article below.\n"
                "For each article, determine:\n"
                "1. A concise summary (2-3 sentences)\n"
                "2. Relevance score (0.0-1.0) to the domain\n"
                "3. Technology Radar quadrant placement\n"
                "4. Technology Radar ring placement\n"
                "5. A short technology name for the radar blip\n"
                "6. Topic category\n"
                "7. Industry segment\n\n"
                "QUADRANT DEFINITIONS:\n"
                "- Techniques: Processes, methodologies, architectural patterns\n"
                "- Platforms: Infrastructure, cloud services, compute platforms\n"
                "- Tools: Software tools, libraries, frameworks\n"
                "- Languages & Frameworks: Programming languages, major ML frameworks\n\n"
                "RING DEFINITIONS:\n"
                "- Adopt: Proven technology, recommend for wide use\n"
                "- Trial: Worth pursuing in projects that can handle some risk\n"
                "- Assess: Worth exploring to understand its impact\n"
                "- Hold: Proceed with caution\n\n"
                "TOPIC CATEGORIES:\n"
                "- Foundation Models & Agents | Safety & Governance | Infrastructure & Compute\n"
                "- Open Source & Research | Partnerships & Strategy\n\n"
                "INDUSTRY SEGMENTS:\n"
                "- Frontier Labs | Big Tech Platforms | Infra & Chips | Ethics & Policy | Ecosystem & Investors\n\n"
                + people_block
                + "OUTPUT RULES:\n"
                "- Return ONLY a valid JSON object with an \"articles\" array.\n"
                "- Do NOT include schema definitions or type metadata.\n"
                "- Filter out articles with relevance_score < 0.3.\n"
                "- The articles array MUST contain actual classified data.\n"
                + (f"\nADDITIONAL REQUIREMENTS:\n{custom_requirements}\n" if custom_requirements else "")
            ),
        },
        {
            "role": "user",
            "parts": (
                f"ARTICLES TO CLASSIFY:\n\n{articles_text}\n\n"
                "Classify each relevant article. Return ONLY valid JSON."
            ),
        },
    ]
    return contents


def sensing_report_prompt(
    classified_articles_json: str,
    domain: str = "Generative AI",
    date_range: str = "",
    custom_requirements: str = "",
    org_context: str = "",
    key_people: list[str] | None = None,
) -> list[dict]:
    """Build a chat prompt to generate the final tech sensing report."""
    people_block = ""
    if key_people:
        names = ", ".join(key_people)
        people_block = (
            f"\nKEY PEOPLE WATCHLIST:\n"
            f"Track actions and statements by these leaders: {names}.\n"
            "Include their moves in headline_moves and market_signals.\n"
        )

    contents = [
        {
            "role": "system",
            "parts": (
                f"You are a senior technology strategist creating a weekly "
                f"Tech Sensing Report for the {domain} domain.\n\n"
                "Generate a comprehensive report that:\n"
                "1. Ranks the top 10 headline moves\n"
                "2. Identifies key trends and patterns\n"
                "3. Places technologies on a Technology Radar\n"
                "4. Analyzes market signals\n"
                "5. Offers actionable recommendations\n"
                "6. Highlights notable developments\n\n"
                + people_block
                + "REPORT QUALITY GUIDELINES:\n"
                "- Executive summary: 200-350 words with markdown formatting\n"
                "- Key trends: 5-10 with supporting evidence\n"
                "- Radar items: 15-30 distinct technologies\n"
                "- Market signals: 5-10 from companies and leaders\n"
                "- Report sections: 3-6 deep-dive sections\n"
                "- Recommendations: actionable, prioritized\n\n"
                "GROUNDING RULES:\n"
                "- Every claim MUST be grounded in the provided articles.\n"
                "- Use article URLs to populate source_urls arrays.\n"
                "- Do NOT fabricate information.\n\n"
                "OUTPUT RULES:\n"
                "- Return ONLY a valid JSON object.\n"
                "- Do NOT include radar_item_details.\n"
                "- Do NOT include schema definitions.\n"
                "- Escape newlines as \\n in string values.\n"
                + (f"\nADDITIONAL REQUIREMENTS:\n{custom_requirements}\n" if custom_requirements else "")
                + (f"\n{org_context}\n" if org_context else "")
            ),
        },
        {
            "role": "user",
            "parts": (
                f"DATE RANGE: {date_range}\nDOMAIN: {domain}\n\n"
                f"CLASSIFIED ARTICLES:\n\n{classified_articles_json}\n\n"
                "Generate the complete Tech Sensing Report. Return ONLY valid JSON."
            ),
        },
    ]
    return contents


def sensing_details_prompt(
    radar_items_json: str,
    classified_articles_json: str,
    domain: str = "Generative AI",
) -> list[dict]:
    """Build a chat prompt to generate detailed write-ups for each radar item."""
    contents = [
        {
            "role": "system",
            "parts": (
                f"You are a senior technology strategist writing detailed technology "
                f"radar entries for the {domain} domain.\n\n"
                "For EVERY radar item, generate a detailed write-up covering:\n"
                "  * what_it_is, why_it_matters, current_state\n"
                "  * key_players, practical_applications, source_urls\n\n"
                "ATTRIBUTION RULES:\n"
                "- List ONLY entities that actively develop or release the technology.\n"
                "- Distinguish research authors from implementation authors.\n\n"
                "OUTPUT RULES:\n"
                "- Return ONLY a valid JSON object with one key: radar_item_details.\n"
                "- technology_name MUST exactly match the radar item name.\n"
                "- Escape newlines as \\n in string values.\n"
            ),
        },
        {
            "role": "user",
            "parts": (
                f"DOMAIN: {domain}\n\n"
                f"RADAR ITEMS:\n{radar_items_json}\n\n"
                f"CLASSIFIED ARTICLES:\n{classified_articles_json}\n\n"
                "Generate detailed write-ups for EVERY radar item. Return ONLY valid JSON."
            ),
        },
    ]
    return contents
