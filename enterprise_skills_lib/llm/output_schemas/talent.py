"""Pydantic schemas for Talent Radar skill."""

from typing import List

from pydantic import BaseModel, Field

from enterprise_skills_lib.llm.output_schemas.base import LLMOutputBase


class KeyMove(BaseModel):
    person_name: str
    previous_role: str = ""
    new_role: str = ""
    from_company: str = ""
    to_company: str = ""
    significance: str = ""
    source_urls: List[str] = Field(default_factory=list)


class HiringTrend(BaseModel):
    company: str
    role_category: str
    trend_direction: str = "Stable"  # "Rapidly Growing"|"Growing"|"Stable"|"Declining"
    estimated_openings: str = "Unknown"  # "50+"|"10-50"|"<10"|"Unknown"
    notable_requirements: List[str] = Field(default_factory=list)


class SkillDemand(BaseModel):
    skill_name: str
    demand_trend: str = "Stable"  # "Surging"|"Rising"|"Stable"|"Declining"
    top_requesting_companies: List[str] = Field(default_factory=list)
    salary_premium: str = "None"  # "High"|"Moderate"|"None"


class SkillGap(BaseModel):
    capability: str
    current_coverage: str = "None"  # "Strong"|"Partial"|"None"
    market_difficulty: str = "Moderate"  # "Hard to find"|"Moderate"|"Easy"
    recommended_action: str = "Hire"  # "Hire"|"Train"|"Contract"|"Partner"


class TalentReport(LLMOutputBase):
    report_title: str
    date_range: str
    key_moves: List[KeyMove]
    hiring_trends: List[HiringTrend] = Field(default_factory=list)
    skill_demands: List[SkillDemand] = Field(default_factory=list)
    skill_gaps: List[SkillGap] = Field(default_factory=list)
    talent_market_summary: str = ""
    recommendations: List[str] = Field(default_factory=list)
