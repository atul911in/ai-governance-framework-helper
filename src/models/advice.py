"""Advice output and export models for the AI Governance Framework Helper."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.models.compliance import (
    ComplianceObligation,
    FrameworkComparison,
    RiskClassification,
)
from src.models.enums import DetailLevel, GovernanceFrameworkId
from src.models.project import ProjectProfile
from src.models.technology import TechnologyRecommendation


class ComplianceAdvice(BaseModel):
    """Complete compliance advice output from the multi-agent workflow."""

    id: str
    project_id: str
    frameworks: list[GovernanceFrameworkId]
    detail_level: DetailLevel
    risk_classifications: list[RiskClassification]
    obligations: list[ComplianceObligation]
    framework_comparison: Optional[FrameworkComparison] = None
    industry_guidance: str
    technology_recommendations: list[TechnologyRecommendation]
    generated_at: datetime
    disclaimer: str = "This advice is informational and does not constitute legal counsel."


class ExportDocument(BaseModel):
    """Exportable document containing compliance advice and project context."""

    advice_id: str
    format: str  # "pdf" or "markdown"
    project_summary: ProjectProfile
    content: ComplianceAdvice
    timestamp: datetime
    version: str
