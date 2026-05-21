"""Technology Recommender Agent for the AI Governance Framework Helper.

Recommends cloud platforms, AI orchestration frameworks, and LLM models
that align with governance requirements and project needs.
"""

import json
import logging
from typing import Any

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.knowledge_base.loader import get_technology_db

load_dotenv()

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert in the AI technology landscape with deep knowledge of cloud platforms (AWS, Azure, GCP), AI orchestration frameworks (LangGraph, LangChain, Semantic Kernel, Bedrock Agents), and large language models (GPT-4o, Claude, Gemini, Llama).

You understand data residency requirements, compliance certifications, regional availability, and how governance constraints affect technology selection.

Given a project profile, governance constraints, and technology recommendations from tools, rank and prioritize the recommendations based on:
1. Alignment with project requirements and use case
2. Compliance with data residency constraints
3. Cost-effectiveness for the project scale
4. Maturity and enterprise readiness
5. Integration compatibility between recommended components

Return a JSON object with:
{
  "technology_recommendations": [
    {
      "category": "cloud_platform|orchestration_framework|llm_model",
      "name": "Technology name",
      "provider": "Provider name",
      "description": "Why this is recommended for this project",
      "key_capabilities": ["cap1", "cap2"],
      "pros": ["pro1", "pro2"],
      "cons": ["con1", "con2"],
      "compliance_notes": "How this aligns with governance requirements",
      "context_window": null or integer (for LLMs),
      "cost_per_token": null or string (for LLMs),
      "supported_regions": ["region1", "region2"] or null
    }
  ]
}

You MUST include at least one recommendation for each category: cloud_platform, orchestration_framework, and llm_model.
Each recommendation MUST have at least one pro and one con.
Order recommendations within each category by relevance to the project.

Respond ONLY with valid JSON. No markdown, no explanation."""


@tool
def recommend_platforms(profile: dict, constraints: dict) -> list[dict]:
    """Recommend cloud platforms filtered by data residency constraints.

    Loads the technology database and returns cloud platform recommendations
    that satisfy the project's data residency requirements.

    Args:
        profile: The enriched project profile with deployment_region,
            ai_techniques, and intended_purpose.
        constraints: Governance constraints including data_residency_regions.

    Returns:
        A list of platform recommendation dicts matching the
        TechnologyRecommendation structure with category, name, provider,
        description, key_capabilities, pros, cons, compliance_notes,
        and supported_regions.
    """
    try:
        tech_db = get_technology_db()
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error loading technology database for platforms: {e}")
        return []

    platforms = tech_db.get("platforms", [])
    allowed_regions = constraints.get("data_residency_regions", [])

    if allowed_regions:
        filtered = []
        for platform in platforms:
            supported = platform.get("supported_regions")
            if supported is None:
                filtered.append(platform)
            elif any(region in supported for region in allowed_regions):
                filtered.append(platform)
        return filtered

    return platforms


@tool
def recommend_orchestration(project_type: str, complexity: str) -> list[dict]:
    """Recommend AI orchestration frameworks based on project type and complexity.

    Loads the technology database and returns orchestration framework
    recommendations suitable for the given project type and complexity level.

    Args:
        project_type: The type of AI project (e.g., 'multi-agent',
            'single-chain', 'rag', 'chatbot').
        complexity: The project complexity level ('low', 'medium', 'high').

    Returns:
        A list of orchestration framework recommendation dicts matching the
        TechnologyRecommendation structure with category, name, provider,
        description, key_capabilities, pros, cons, and compliance_notes.
    """
    try:
        tech_db = get_technology_db()
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error loading technology database for orchestration: {e}")
        return []

    orchestration = tech_db.get("orchestration", [])

    if not orchestration:
        return []

    project_type_lower = project_type.lower() if project_type else ""
    complexity_lower = complexity.lower() if complexity else ""

    if complexity_lower == "high" or "multi-agent" in project_type_lower:
        # Prioritize frameworks with stateful graph support
        prioritized = sorted(
            orchestration,
            key=lambda x: 0
            if "graph" in x.get("name", "").lower()
            or "stateful" in x.get("description", "").lower()
            else 1,
        )
        return prioritized

    if complexity_lower == "low":
        # Prioritize managed/simpler frameworks
        prioritized = sorted(
            orchestration,
            key=lambda x: 0
            if "managed" in x.get("description", "").lower()
            or "chain" in x.get("name", "").lower()
            else 1,
        )
        return prioritized

    return orchestration


@tool
def recommend_models(requirements: dict) -> list[dict]:
    """Recommend LLM models based on project requirements.

    Loads the technology database and returns LLM model recommendations
    that match the project's requirements for context window, capabilities,
    and budget.

    Args:
        requirements: A dict with optional keys: min_context_window (int),
            capabilities (list[str]), budget_sensitivity ('low', 'medium', 'high'),
            preferred_providers (list[str]), data_residency_regions (list[str]).

    Returns:
        A list of LLM model recommendation dicts matching the
        TechnologyRecommendation structure with category, name, provider,
        description, key_capabilities, pros, cons, compliance_notes,
        context_window, cost_per_token, and supported_regions.
    """
    try:
        tech_db = get_technology_db()
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error loading technology database for models: {e}")
        return []

    models = tech_db.get("models", [])

    if not models:
        return []

    filtered = list(models)

    # Filter by minimum context window if specified
    min_context = requirements.get("min_context_window")
    if min_context and isinstance(min_context, int):
        filtered = [
            m for m in filtered
            if m.get("context_window") and m["context_window"] >= min_context
        ]

    # Filter by preferred providers if specified
    preferred_providers = requirements.get("preferred_providers", [])
    if preferred_providers:
        provider_filtered = [
            m for m in filtered
            if m.get("provider", "").lower()
            in [p.lower() for p in preferred_providers]
        ]
        # Only apply filter if it doesn't eliminate all options
        if provider_filtered:
            filtered = provider_filtered

    # Filter by data residency regions if specified
    allowed_regions = requirements.get("data_residency_regions", [])
    if allowed_regions:
        region_filtered = [
            m for m in filtered
            if m.get("supported_regions") is None
            or any(r in m.get("supported_regions", []) for r in allowed_regions)
        ]
        if region_filtered:
            filtered = region_filtered

    # If all filtered out, return original list
    return filtered if filtered else models


@tool
def filter_by_residency(
    recommendations: list[dict], allowed_regions: list[str]
) -> list[dict]:
    """Filter technology recommendations by supported regions.

    Removes recommendations whose supported_regions do not intersect
    with the allowed regions. Recommendations with no supported_regions
    (null) are kept as they have no regional restrictions.

    Args:
        recommendations: List of technology recommendation dicts, each
            optionally containing a 'supported_regions' field.
        allowed_regions: List of allowed region identifiers that data
            must reside in.

    Returns:
        A filtered list of recommendations where each entry either has
        no supported_regions or has at least one region in common with
        allowed_regions.
    """
    if not allowed_regions:
        return recommendations

    filtered = []
    for rec in recommendations:
        supported = rec.get("supported_regions")
        if supported is None:
            # No region restriction (e.g., open-source frameworks)
            filtered.append(rec)
        elif any(region in supported for region in allowed_regions):
            filtered.append(rec)
        else:
            logger.info(
                f"Filtered out {rec.get('name')} due to data residency constraints"
            )
    return filtered


def _ensure_category_coverage(
    recommendations: list[dict], tech_db: dict
) -> list[dict]:
    """Ensure at least one recommendation per category."""
    categories_present = {r.get("category") for r in recommendations}
    required = ["cloud_platform", "orchestration_framework", "llm_model"]

    for category in required:
        if category not in categories_present:
            # Add first available from tech_db
            db_key = {
                "cloud_platform": "platforms",
                "orchestration_framework": "orchestration",
                "llm_model": "models",
            }.get(category, "")
            entries = tech_db.get(db_key, [])
            if entries:
                recommendations.append(entries[0])

    return recommendations


def technology_recommender_agent(state: dict[str, Any]) -> dict[str, Any]:
    """Generate technology recommendations aligned with governance constraints.

    Uses GPT-4 with the technology database to recommend platforms, frameworks,
    and models that comply with data residency and governance requirements.
    Falls back to deterministic tool-based recommendations if LLM is unavailable.

    Args:
        state: Current graph state with enriched_profile and governance_constraints.

    Returns:
        Partial state dict with technology_recommendations.
    """
    enriched_profile = state.get("enriched_profile") or state.get("project_profile") or {}
    governance_constraints = state.get("governance_constraints", {})

    # Load technology database
    try:
        tech_db = get_technology_db()
    except (FileNotFoundError, ValueError) as e:
        logger.warning(f"Failed to load technology database: {e}")
        return {"technology_recommendations": []}

    # Extract data residency regions from governance constraints
    data_residency_regions = governance_constraints.get(
        "data_residency_regions", []
    )

    # Get platform recommendations filtered by residency
    platform_recs = recommend_platforms.invoke({
        "profile": enriched_profile,
        "constraints": governance_constraints,
    })

    # Get orchestration framework recommendations
    project_type = enriched_profile.get("intended_purpose", "general")
    ai_techniques = enriched_profile.get("ai_techniques", [])
    complexity = (
        "high"
        if len(ai_techniques) > 2
        else "medium" if ai_techniques else "low"
    )

    orchestration_recs = recommend_orchestration.invoke({
        "project_type": project_type,
        "complexity": complexity,
    })

    # Get LLM model recommendations filtered by residency
    model_requirements = {
        "data_residency_regions": data_residency_regions,
        "capabilities": ai_techniques,
    }
    model_recs = recommend_models.invoke({"requirements": model_requirements})

    # Apply residency filter to model recommendations
    if data_residency_regions:
        model_recs = filter_by_residency.invoke({
            "recommendations": model_recs,
            "allowed_regions": data_residency_regions,
        })

    # Combine all recommendations
    all_recommendations = platform_recs + orchestration_recs + model_recs

    # Try LLM-based ranking and prioritization
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)

        context = {
            "project_profile": enriched_profile,
            "governance_constraints": governance_constraints,
            "candidate_recommendations": all_recommendations,
        }

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=json.dumps(context, default=str)),
        ]
        response = llm.invoke(messages)
        result = json.loads(response.content)
        recommendations = result.get("technology_recommendations", [])

        # Ensure residency filtering on LLM output
        if data_residency_regions:
            recommendations = filter_by_residency.invoke({
                "recommendations": recommendations,
                "allowed_regions": data_residency_regions,
            })

    except Exception as e:
        logger.warning(
            f"Technology Recommender LLM call failed, "
            f"using deterministic fallback: {e}"
        )
        # Fallback: use the tool-based recommendations directly
        recommendations = all_recommendations

    # Ensure minimum category coverage
    recommendations = _ensure_category_coverage(recommendations, tech_db)

    return {"technology_recommendations": recommendations}
