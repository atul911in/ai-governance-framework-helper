"""Graph state definition with proper reducers for LangGraph."""

from typing import Annotated, Any, Optional, TypedDict


def _replace(existing: Any, new: Any) -> Any:
    """Reducer that replaces the existing value with the new one."""
    return new


class GovernanceGraphState(TypedDict):
    """Shared state with reducer annotations for proper merging."""

    # Input state
    project_profile: Annotated[Optional[dict], _replace]
    selected_frameworks: Annotated[list, _replace]
    detail_level: Annotated[str, _replace]

    # Agent routing state
    next_agent: Annotated[str, _replace]
    agents_completed: Annotated[list, _replace]
    requires_clarification: Annotated[bool, _replace]
    clarification_questions: Annotated[list, _replace]

    # User Persona Agent output
    enriched_profile: Annotated[Optional[dict], _replace]
    profile_valid: Annotated[bool, _replace]
    validation_errors: Annotated[list, _replace]

    # Country Policy Agent output
    risk_classifications: Annotated[list, _replace]
    compliance_obligations: Annotated[list, _replace]
    framework_comparison: Annotated[Optional[dict], _replace]
    framework_metadata: Annotated[list, _replace]

    # Industry Agent output
    industry_guidance: Annotated[str, _replace]
    industry_best_practices: Annotated[list, _replace]
    additional_obligations: Annotated[list, _replace]

    # Technology Recommender Agent output
    technology_recommendations: Annotated[list, _replace]
    governance_constraints: Annotated[dict, _replace]

    # Final output
    final_advice: Annotated[Optional[dict], _replace]
