"""Prompt templates for Patent Monitor skill."""


def patent_analysis_prompt(
    patents_text: str,
    domain: str = "large language models",
    assignees: list[str] | None = None,
) -> list[dict]:
    """Build a prompt to analyze patent filings."""
    assignee_block = ""
    if assignees:
        assignee_block = f"\nFocus especially on patents from: {', '.join(assignees)}.\n"

    return [
        {
            "role": "system",
            "parts": (
                f"You are a senior patent analyst specializing in {domain}.\n\n"
                "Analyze the following patent filings and produce a comprehensive report:\n"
                "1. Identify the most significant patents (significance_score 0.0-1.0)\n"
                "2. Group patents into technology clusters\n"
                "3. Analyze filing activity by assignee (trend direction)\n"
                "4. Summarize the IP landscape\n"
                "5. Identify white space opportunities\n"
                "6. Provide trend analysis\n\n"
                + assignee_block
                + "OUTPUT: Return ONLY a valid JSON object matching the PatentReport schema.\n"
            ),
        },
        {
            "role": "user",
            "parts": (
                f"DOMAIN: {domain}\n\n"
                f"PATENT FILINGS:\n\n{patents_text}\n\n"
                "Generate the patent analysis report. Return ONLY valid JSON."
            ),
        },
    ]
