"""Prompt templates for Talent Radar skill."""


def talent_scan_prompt(
    articles_text: str,
    roles: list[str],
    companies: list[str] | None = None,
) -> list[dict]:
    """Build a prompt to analyze the talent market."""
    roles_str = ", ".join(roles)
    companies_block = ""
    if companies:
        companies_block = f"\nFocus especially on talent movements at: {', '.join(companies)}.\n"

    return [
        {
            "role": "system",
            "parts": (
                "You are a senior talent intelligence analyst specializing in AI and technology.\n\n"
                f"Analyze the following articles for talent market insights related to: {roles_str}.\n\n"
                + companies_block
                + "Produce:\n"
                "1. Key executive/researcher moves (person, from/to, significance)\n"
                "2. Hiring trends by company and role category\n"
                "3. Skill demand shifts (emerging, declining)\n"
                "4. Talent market summary narrative\n"
                "5. Actionable recommendations\n\n"
                "GROUNDING RULES:\n"
                "- Ground claims in provided articles. Use source_urls.\n"
                "- Do NOT fabricate people or moves.\n\n"
                "OUTPUT: Return ONLY a valid JSON object matching the TalentReport schema.\n"
            ),
        },
        {
            "role": "user",
            "parts": (
                f"TARGET ROLES: {roles_str}\n\n"
                f"ARTICLES:\n\n{articles_text}\n\n"
                "Generate the talent market report. Return ONLY valid JSON."
            ),
        },
    ]


def skill_gap_prompt(
    current_skills: list[str],
    target_capabilities: list[str],
    market_context: str = "",
) -> list[dict]:
    """Build a prompt for skill gap analysis."""
    return [
        {
            "role": "system",
            "parts": (
                "You are a talent strategy advisor.\n\n"
                "Analyze the gap between a team's current skills and target capabilities.\n"
                "For each target capability, assess:\n"
                "1. Current coverage (Strong/Partial/None)\n"
                "2. Market difficulty to hire (Hard to find/Moderate/Easy)\n"
                "3. Recommended action (Hire/Train/Contract/Partner)\n\n"
                "OUTPUT: Return ONLY a valid JSON object with a 'skill_gaps' array.\n"
            ),
        },
        {
            "role": "user",
            "parts": (
                f"CURRENT TEAM SKILLS: {', '.join(current_skills)}\n"
                f"TARGET CAPABILITIES: {', '.join(target_capabilities)}\n"
                + (f"MARKET CONTEXT:\n{market_context}\n\n" if market_context else "\n")
                + "Generate the skill gap analysis. Return ONLY valid JSON."
            ),
        },
    ]
