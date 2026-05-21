"""Risk and compliance models for the AI Governance Framework Helper."""

from typing import Optional

from pydantic import BaseModel, Field

from src.models.enums import AdviceCategory, GovernanceFrameworkId, RiskLevel


class RiskClassification(BaseModel):
    """Risk classification result for a specific governance framework."""

    framework: GovernanceFrameworkId
    risk_level: RiskLevel
    explanation: str
    key_factors: list[str]
    regulatory_obligations: list[str]
    is_flagged: bool = Field(description="True if risk is high or unacceptable")


class ComplianceObligation(BaseModel):
    """A specific compliance obligation with actionable guidance."""

    category: AdviceCategory
    obligation: str
    recommended_actions: list[str]
    documentation_requirements: list[str]
    timeline: Optional[str] = None
    framework_reference: str  # e.g., "EU AI Act, Article 9"
    priority: str  # "high", "medium", "low"


class FrameworkComparison(BaseModel):
    """Comparison analysis across multiple governance frameworks."""

    frameworks: list[GovernanceFrameworkId]
    overlapping_requirements: list[str]
    conflicting_requirements: list[dict]
    harmonized_approach: str
