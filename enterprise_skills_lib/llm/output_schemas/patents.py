"""Pydantic schemas for Patent Monitor skill."""

from typing import List

from pydantic import BaseModel, Field

from enterprise_skills_lib.llm.output_schemas.base import LLMOutputBase


class PatentFiling(BaseModel):
    patent_id: str
    title: str
    abstract: str = ""
    assignee: str = ""
    inventors: List[str] = Field(default_factory=list)
    filing_date: str = ""
    publication_date: str = ""
    classification_codes: List[str] = Field(default_factory=list)
    technology_cluster: str = ""
    significance_score: float = 0.5


class AssigneeActivity(BaseModel):
    company_name: str
    filing_count: int = 0
    trend_direction: str = "Stable"  # "Increasing"|"Stable"|"Decreasing"
    top_technology_areas: List[str] = Field(default_factory=list)
    notable_patents: List[str] = Field(default_factory=list)


class PatentReport(LLMOutputBase):
    report_title: str
    domain: str
    date_range: str
    total_patents_analyzed: int = 0
    key_filings: List[PatentFiling]
    assignee_activity: List[AssigneeActivity] = Field(default_factory=list)
    technology_clusters: List[dict] = Field(default_factory=list)
    ip_landscape_summary: str = ""
    white_space_opportunities: List[str] = Field(default_factory=list)
    trend_analysis: str = ""
