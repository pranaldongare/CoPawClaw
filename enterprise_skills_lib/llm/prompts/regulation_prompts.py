"""Prompt templates for Regulation Tracker skill."""


def regulation_scan_prompt(
    articles_text: str,
    domains: list[str],
    jurisdictions: list[str],
) -> list[dict]:
    """Build a prompt to analyze regulatory developments."""
    domains_str = ", ".join(domains)
    jurisdictions_str = ", ".join(jurisdictions)

    return [
        {
            "role": "system",
            "parts": (
                f"You are a senior regulatory analyst monitoring {domains_str} regulations "
                f"across {jurisdictions_str}.\n\n"
                "Analyze the following articles and produce:\n"
                "1. Regulatory updates with jurisdiction, type, effective dates, key obligations\n"
                "2. Compliance deadlines with penalties\n"
                "3. Impact assessments per regulation\n"
                "4. Risk matrix summary (jurisdiction x regulation type)\n"
                "5. Recommended compliance actions\n\n"
                "GROUNDING RULES:\n"
                "- Ground every claim in the provided articles.\n"
                "- Include source_urls where available.\n\n"
                "OUTPUT: Return ONLY a valid JSON object matching the RegulationReport schema.\n"
            ),
        },
        {
            "role": "user",
            "parts": (
                f"REGULATORY DOMAINS: {domains_str}\nJURISDICTIONS: {jurisdictions_str}\n\n"
                f"ARTICLES:\n\n{articles_text}\n\n"
                "Generate the regulation report. Return ONLY valid JSON."
            ),
        },
    ]


def impact_assessment_prompt(
    regulation_text: str,
    regulation_name: str,
    company_context: str,
) -> list[dict]:
    """Build a prompt for a focused regulatory impact assessment."""
    return [
        {
            "role": "system",
            "parts": (
                "You are a regulatory compliance advisor.\n\n"
                f"Assess the impact of '{regulation_name}' on the following business context:\n"
                f"{company_context}\n\n"
                "Provide:\n"
                "1. Impact level (Critical/High/Medium/Low/None)\n"
                "2. Specific affected operations\n"
                "3. Required changes\n"
                "4. Estimated effort\n"
                "5. Detailed reasoning\n\n"
                "OUTPUT: Return ONLY a valid JSON object matching the ImpactAssessment schema.\n"
            ),
        },
        {
            "role": "user",
            "parts": (
                f"REGULATION: {regulation_name}\n\n"
                f"REGULATORY TEXT/ARTICLES:\n{regulation_text}\n\n"
                "Generate the impact assessment. Return ONLY valid JSON."
            ),
        },
    ]
