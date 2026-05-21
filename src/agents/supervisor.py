"""Supervisor Agent for the AI Governance Framework Helper.

Orchestrates the overall workflow by determining which agents to invoke,
in what order, and whether to request clarification from the user.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def supervisor_router(state: dict[str, Any]) -> str:
    """Determine the next agent to invoke based on current state.

    Routing logic:
    1. If profile not valid -> user_persona (enrich/validate)
    2. If no risk classifications -> parallel_analysis (country_policy + industry)
    3. If no technology recommendations -> technology_recommender
    4. Otherwise -> aggregator

    Args:
        state: Current graph state.

    Returns:
        Name of the next node to route to.
    """
    # Check if profile needs enrichment
    if not state.get("profile_valid", False):
        return "user_persona"

    # Check if clarification is needed
    if state.get("requires_clarification", False):
        return "aggregator"  # Return what we have with clarification questions

    # Check if risk classification is done
    if not state.get("risk_classifications"):
        return "parallel_analysis"

    # Check if technology recommendations are done
    if not state.get("technology_recommendations"):
        return "technology_recommender"

    # All done
    return "aggregator"


def supervisor_node(state: dict[str, Any]) -> dict[str, Any]:
    """Supervisor node that updates routing state.

    This node is lightweight - it just determines the next step
    and updates the agents_completed list.

    Args:
        state: Current graph state.

    Returns:
        Partial state dict with next_agent updated.
    """
    next_agent = supervisor_router(state)
    agents_completed = state.get("agents_completed", [])

    logger.info(f"Supervisor routing to: {next_agent}")

    return {
        "next_agent": next_agent,
        "agents_completed": agents_completed,
    }