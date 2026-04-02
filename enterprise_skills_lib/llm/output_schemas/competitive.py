"""Pydantic schemas for Competitive Intelligence skill."""

from typing import List

from pydantic import BaseModel, Field

from enterprise_skills_lib.llm.output_schemas.base import LLMOutputBase


class CompanyEvent(BaseModel):
    company: str
    event_type: str  # "product_launch"|"funding"|"partnership"|"acquisition"|"hire"|"regulatory"
    headline: str
    description: str
    date: str = ""
    strategic_intent: str = ""
    source_urls: List[str] = Field(default_factory=list)


class CompetitorProfile(BaseModel):
    company_name: str
    segment: str = ""
    recent_events: List[CompanyEvent] = Field(default_factory=list)
    products: List[str] = Field(default_factory=list)
    estimated_market_position: str = "Emerging"  # "Leader"|"Challenger"|"Niche"|"Emerging"
    key_strengths: List[str] = Field(default_factory=list)
    key_weaknesses: List[str] = Field(default_factory=list)
    threat_level: str = "Medium"  # "Critical"|"High"|"Medium"|"Low"
    threat_reasoning: str = ""


class CompetitiveMatrix(BaseModel):
    dimensions: List[str] = Field(default_factory=list)
    rows: List[dict] = Field(default_factory=list)


class OpportunityGap(BaseModel):
    gap_name: str
    description: str
    related_competitors: List[str] = Field(default_factory=list)
    potential_value: str = "Medium"  # "High"|"Medium"|"Low"


class CompetitiveReport(LLMOutputBase):
    report_title: str
    domain: str
    date_range: str
    competitor_profiles: List[CompetitorProfile]
    competitive_matrix: CompetitiveMatrix = Field(default_factory=CompetitiveMatrix)
    strategic_moves: List[CompanyEvent] = Field(default_factory=list)
    opportunity_gaps: List[OpportunityGap] = Field(default_factory=list)
    swot_synthesis: str = ""
    recommendations: List[str] = Field(default_factory=list)
