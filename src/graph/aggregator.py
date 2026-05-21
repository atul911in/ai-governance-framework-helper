"""Response Aggregator node for the AI Governance Framework Helper.

Combines outputs from all agents into a single ComplianceAdvice object.
Handles partial results gracefully when an agent has failed.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

DISCLAIMER = "This advice is informational and does not constitute legal counsel."


def aggregator_node(state: dict[str, Any]) -> dict[str, Any]:
    """Aggregate all agent outputs into a final ComplianceAdvice object.

    Extracts outputs from all agents, merges additional_obligations into
    compliance_obligations, and builds a ComplianceAdvice dict. Handles
    partial results gracefully - if an agent failed, the corresponding
    section is marked as unavailable or given a safe default.

    Args:
        state: Current graph state with outputs from all agents.

    Returns:
        Partial state dict with {"final_advice": advice_dict}.
    """
    # 1. Extract all agent outputs from state
    enriched_profile = state.get("enriched_profile") or {}
    selected_frameworks = state.get("selected_frameworks", [])
    detail_level = state.get("detail_level", "standard")
    risk_classifications = state.get("risk_classifications", [])
    compliance_obligations = state.get("compliance_obligations", [])
    additional_obligations = state.get("additional_obligations", [])
    framework_comparison = state.get("framework_comparison")
    industry_guidance = state.get("industry_guidance")
    industry_best_practices = state.get("industry_best_practices", [])
    technology_recommendations = state.get("technology_recommendations", [])

    # 2. Merge additional_obligations into compliance_obligations
    all_obligations = list(compliance_obligations) + list(additional_obligations)

    # 3. Derive project_id from enriched_profile
    project_id = "unknown"
    if enriched_profile:
        project_id = enriched_profile.get("id") or enriched_profile.get("name", "unknown")

    # Handle partial results gracefully - default unavailable sections
    if not industry_guidance:
        industry_guidance = "No industry guidance available"
        logger.warning("Industry guidance unavailable; using default placeholder.")

    if risk_classifications is None:
        risk_classifications = []
        logger.warning("Risk classifications unavailable; agent may have failed.")

    if technology_recommendations is None:
        technology_recommendations = []
        logger.warning("Technology recommendations unavailable; agent may have failed.")

    # Convert framework enums to their string values for serialization
    framework_ids = [
        fw.value if hasattr(fw, "value") else fw
        for fw in selected_frameworks
    ]

    # Convert detail_level enum to string value
    detail_level_str = detail_level.value if hasattr(detail_level, "value") else detail_level

    # 4. Build the ComplianceAdvice dict
    advice_dict = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "frameworks": framework_ids,
        "detail_level": detail_level_str,
        "risk_classifications": risk_classifications,
        "obligations": all_obligations,
        "framework_comparison": framework_comparison,
        "industry_guidance": industry_guidance,
        "technology_recommendations": technology_recommendations,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": DISCLAIMER,
    }

    logger.info(
        "Aggregated advice: %d risk classifications, %d obligations, %d tech recommendations.",
        len(risk_classifications),
        len(all_obligations),
        len(technology_recommendations),
    )

    return {"final_advice": advice_dict}
