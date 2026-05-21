"""LangGraph state model for the AI Governance Framework Helper."""

from typing import Annotated, Optional, TypedDict

from langgraph.graph.message import add_messages

from src.models.advice import ComplianceAdvice
from src.models.compliance import (
    ComplianceObligation,
    FrameworkComparison,
    RiskClassification,
)
from src.models.enums import DetailLevel, GovernanceFrameworkId
from src.models.project import ProjectProfileInput
from src.models.technology import TechnologyRecommendation


class GraphState(TypedDict):
    """Shared state across all agents in the LangGraph state graph."""

    # Input state
    project_profile: Optional[ProjectProfileInput]
    selected_frameworks: list[GovernanceFrameworkId]
    detail_level: DetailLevel

    # Agent routing state
    next_agent: str
    agents_completed: list[str]
    requires_clarification: bool
    clarification_questions: list[str]

    # User Persona Agent output
    enriched_profile: Optional[dict]
    profile_valid: bool
    validation_errors: list[str]

    # Country Policy Agent output
    risk_classifications: list[RiskClassification]
    compliance_obligations: list[ComplianceObligation]
    framework_comparison: Optional[FrameworkComparison]
    framework_metadata: list[dict]

    # Industry Agent output
    industry_guidance: str
    industry_best_practices: list[str]
    additional_obligations: list[ComplianceObligation]

    # Technology Recommender Agent output
    technology_recommendations: list[TechnologyRecommendation]
    governance_constraints: dict

    # Final output
    final_advice: Optional[ComplianceAdvice]

    # Messages for agent reasoning
    messages: Annotated[list, add_messages]
