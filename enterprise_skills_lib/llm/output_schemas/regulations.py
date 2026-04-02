"""Pydantic schemas for Regulation Tracker skill."""

from typing import List

from pydantic import BaseModel, Field

from enterprise_skills_lib.llm.output_schemas.base import LLMOutputBase


class RegulatoryUpdate(BaseModel):
    regulation_name: str
    jurisdiction: str
    update_type: str = "New"  # "New"|"Amendment"|"Enforcement"|"Guidance"|"Proposal"
    effective_date: str = ""
    summary: str
    key_obligations: List[str] = Field(default_factory=list)
    affected_sectors: List[str] = Field(default_factory=list)
    source_urls: List[str] = Field(default_factory=list)


class ComplianceDeadline(BaseModel):
    regulation: str
    deadline_date: str
    description: str
    jurisdiction: str = ""
    penalty_for_non_compliance: str = ""


class ImpactAssessment(BaseModel):
    regulation_name: str
    impact_level: str = "Medium"  # "Critical"|"High"|"Medium"|"Low"|"None"
    affected_operations: List[str] = Field(default_factory=list)
    required_changes: List[str] = Field(default_factory=list)
    estimated_effort: str = "Moderate"  # "Significant"|"Moderate"|"Minor"
    reasoning: str = ""


class RegulationReport(LLMOutputBase):
    report_title: str
    jurisdictions: List[str]
    date_range: str
    regulatory_updates: List[RegulatoryUpdate]
    compliance_deadlines: List[ComplianceDeadline] = Field(default_factory=list)
    impact_assessments: List[ImpactAssessment] = Field(default_factory=list)
    risk_matrix_summary: str = ""
    recommended_actions: List[str] = Field(default_factory=list)
