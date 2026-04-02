"""Pydantic schemas for Executive Brief Composer skill."""

from typing import List

from pydantic import BaseModel, Field

from enterprise_skills_lib.llm.output_schemas.base import LLMOutputBase


class RiskOpportunity(BaseModel):
    item: str
    type: str = "Risk"  # "Risk"|"Opportunity"
    probability: str = "Medium"  # "High"|"Medium"|"Low"
    impact: str = "Medium"  # "High"|"Medium"|"Low"
    source_skill: str = ""


class ActionItem(BaseModel):
    action: str
    priority: str = "Short-term"  # "Immediate"|"Short-term"|"Medium-term"
    owner_suggestion: str = ""  # "CTO"|"VP Engineering"|"Legal"|"HR"|"CEO"
    related_findings: List[str] = Field(default_factory=list)


class ExecutiveBrief(LLMOutputBase):
    brief_title: str
    domain: str
    date: str
    situation_summary: str  # 2-3 sentences
    key_findings: List[str]  # 5-7 bullets
    risk_opportunity_matrix: List[RiskOpportunity] = Field(default_factory=list)
    competitive_position: List[dict] = Field(default_factory=list)
    regulatory_exposure: List[str] = Field(default_factory=list)
    talent_implications: List[str] = Field(default_factory=list)
    recommended_actions: List[ActionItem]
    supporting_reports: List[dict] = Field(default_factory=list)
