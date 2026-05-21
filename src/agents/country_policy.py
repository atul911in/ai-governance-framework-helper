"""Country Policy Agent for the AI Governance Framework Helper.

Provides governance framework knowledge for specific jurisdictions,
performs risk classification, and generates framework-specific compliance obligations.
"""

import json
import logging
from typing import Any

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.knowledge_base.loader import get_framework, get_all_frameworks
from src.models.enums import AdviceCategory, GovernanceFrameworkId, RiskLevel

load_dotenv()

logger = logging.getLogger(__name__)
SYSTEM_PROMPT = """You are an expert in international AI governance regulations with deep knowledge of risk classification criteria, compliance obligations, timelines, and cross-framework analysis.

Given a project profile and governance framework data, you must:
1. Classify the project's risk level according to the framework's criteria
2. Identify specific compliance obligations that apply
3. Provide framework references for each obligation

Return a JSON object with:
{
  "risk_classifications": [
    {
      "framework": "<framework_id>",
      "risk_level": "unacceptable|high|limited|minimal",
      "explanation": "Why this risk level was assigned",
      "key_factors": ["factor1", "factor2"],
      "regulatory_obligations": ["obligation1", "obligation2"],
      "is_flagged": true/false (true if high or unacceptable)
    }
  ],
  "compliance_obligations": [
    {
      "category": "data_governance|transparency|accountability|fairness|safety|human_oversight",
      "obligation": "Specific obligation text",
      "recommended_actions": ["action1", "action2"],
      "documentation_requirements": ["doc1", "doc2"],
      "timeline": "Timeline if applicable or null",
      "framework_reference": "Article/Section reference",
      "priority": "high|medium|low"
    }
  ],
  "framework_comparison": null or {
    "frameworks": ["framework_id1", "framework_id2"],
    "overlapping_requirements": ["requirement1"],
    "conflicting_requirements": [{"area": "...", "conflict": "..."}],
    "harmonized_approach": "Suggested harmonized approach"
  },
  "governance_constraints": {
    "data_residency_regions": ["region1", "region2"],
    "requires_human_oversight": true/false,
    "requires_conformity_assessment": true/false
  }
}

Respond ONLY with valid JSON. No markdown, no explanation."""


@tool
def classify_risk(profile: dict, framework_id: str) -> dict:
    """Determine risk tier based on project profile and framework criteria.

    Loads the governance framework data and matches the project profile
    against the framework's risk tier criteria to determine classification.

    Args:
        profile: The enriched project profile dictionary.
        framework_id: The governance framework identifier (e.g., 'eu_ai_act').

    Returns:
        A dict with framework, risk_level, explanation, key_factors,
        regulatory_obligations, and is_flagged fields.
    """
    try:
        framework_data = get_framework(framework_id)
    except FileNotFoundError:
        return {
            "framework": framework_id,
            "risk_level": "limited",
            "explanation": f"Framework data not found for {framework_id}. Defaulting to limited risk.",
            "key_factors": ["Framework data unavailable"],
            "regulatory_obligations": [],
            "is_flagged": False,
        }

    risk_tiers = framework_data.get("risk_tiers", [])
    description = profile.get("description", "").lower()
    intended_purpose = profile.get("intended_purpose", "").lower()
    data_types = [dt.lower() for dt in profile.get("data_types", [])]
    ai_techniques = [t.lower() for t in profile.get("ai_techniques", [])]
    risk_indicators = profile.get("risk_indicators", [])
    use_case_category = profile.get("use_case_category", "")

    # Check tiers from highest risk to lowest
    matched_tier = None
    matched_factors = []

    for tier in risk_tiers:
        tier_criteria = tier.get("criteria", [])
        factors = []

        for criterion in tier_criteria:
            criterion_lower = criterion.lower()
            if _matches_criterion(
                criterion_lower, description, intended_purpose,
                data_types, ai_techniques, risk_indicators, use_case_category
            ):
                factors.append(criterion)

        if factors:
            if matched_tier is None or _risk_level_priority(
                tier.get("risk_level", "minimal")
            ) > _risk_level_priority(
                matched_tier.get("risk_level", "minimal")
            ):
                matched_tier = tier
                matched_factors = factors

    # Default to minimal if no criteria matched
    if matched_tier is None:
        risk_level = "minimal"
        explanation = (
            "No specific high-risk criteria matched for this project under "
            f"the {framework_data.get('display_name', framework_id)} framework."
        )
        key_factors = ["No high-risk indicators identified"]
    else:
        risk_level = matched_tier.get("risk_level", "minimal")
        explanation = (
            f"Project classified as {matched_tier.get('tier_name', risk_level)} "
            f"under {framework_data.get('display_name', framework_id)}: "
            f"{matched_tier.get('description', '')}"
        )
        key_factors = matched_factors

    # Get regulatory obligations for this risk level
    regulatory_obligations = []
    for obligation in framework_data.get("key_obligations", []):
        applies_to = obligation.get("applies_to_risk_levels", [])
        if risk_level in applies_to:
            regulatory_obligations.append(obligation.get("obligation", ""))

    is_flagged = risk_level in ("high", "unacceptable")

    return {
        "framework": framework_id,
        "risk_level": risk_level,
        "explanation": explanation,
        "key_factors": key_factors,
        "regulatory_obligations": regulatory_obligations,
        "is_flagged": is_flagged,
    }


@tool
def get_obligations(framework_id: str, risk_level: str) -> list[dict]:
    """Retrieve compliance obligations filtered by risk level.

    Loads the governance framework and returns obligations that apply
    to the specified risk level.

    Args:
        framework_id: The governance framework identifier (e.g., 'eu_ai_act').
        risk_level: The risk level to filter by (e.g., 'high', 'limited').

    Returns:
        A list of obligation dicts with category, obligation, recommended_actions,
        documentation_requirements, timeline, framework_reference, and priority.
    """
    try:
        framework_data = get_framework(framework_id)
    except FileNotFoundError:
        logger.warning(f"Framework data not found for: {framework_id}")
        return []

    display_name = framework_data.get("display_name", framework_id)
    obligations = []

    for obligation_def in framework_data.get("key_obligations", []):
        applies_to = obligation_def.get("applies_to_risk_levels", [])
        if risk_level in applies_to:
            priority = "high" if risk_level in ("high", "unacceptable") else "medium"

            obligations.append({
                "category": obligation_def.get("category", "accountability"),
                "obligation": obligation_def.get("obligation", ""),
                "recommended_actions": [
                    f"Review and implement: {obligation_def.get('obligation', '')}",
                    f"Refer to {obligation_def.get('article_reference', '')} for detailed requirements",
                ],
                "documentation_requirements": [
                    f"Document compliance with {obligation_def.get('article_reference', '')}",
                    "Maintain evidence of implementation measures",
                ],
                "timeline": framework_data.get("enforcement_timeline"),
                "framework_reference": (
                    f"{display_name}, {obligation_def.get('article_reference', '')}"
                ),
                "priority": priority,
            })

    return obligations


@tool
def compare_frameworks(framework_ids: list[str], profile: dict) -> dict:
    """Compare multiple governance frameworks for overlaps and conflicts.

    Analyzes the selected frameworks to identify overlapping requirements,
    conflicting requirements, and suggests a harmonized approach.

    Args:
        framework_ids: List of framework identifiers to compare.
        profile: The enriched project profile for context.

    Returns:
        A dict with frameworks, overlapping_requirements,
        conflicting_requirements, and harmonized_approach.
    """
    if len(framework_ids) < 2:
        return {
            "frameworks": framework_ids,
            "overlapping_requirements": [],
            "conflicting_requirements": [],
            "harmonized_approach": "Single framework selected; no comparison needed.",
        }

    frameworks_data = []
    for fw_id in framework_ids:
        try:
            data = get_framework(fw_id)
            frameworks_data.append(data)
        except FileNotFoundError:
            logger.warning(f"Framework not found for comparison: {fw_id}")
            continue

    if len(frameworks_data) < 2:
        return {
            "frameworks": framework_ids,
            "overlapping_requirements": [],
            "conflicting_requirements": [],
            "harmonized_approach": "Insufficient framework data for comparison.",
        }

    # Find overlapping obligation categories
    all_categories: dict[str, list[str]] = {}
    for fw_data in frameworks_data:
        fw_name = fw_data.get("display_name", fw_data.get("framework_id", ""))
        for obligation in fw_data.get("key_obligations", []):
            category = obligation.get("category", "")
            if category not in all_categories:
                all_categories[category] = []
            if fw_name not in all_categories[category]:
                all_categories[category].append(fw_name)

    # Overlapping: categories present in multiple frameworks
    overlapping_requirements = []
    for category, fw_names in all_categories.items():
        if len(fw_names) > 1:
            overlapping_requirements.append(
                f"{category.replace('_', ' ').title()} requirements shared by: "
                f"{', '.join(fw_names)}"
            )

    # Identify potential conflicts
    conflicting_requirements = []
    risk_approaches = {}
    for fw_data in frameworks_data:
        fw_name = fw_data.get("display_name", "")
        tiers = fw_data.get("risk_tiers", [])
        risk_approaches[fw_name] = [t.get("risk_level") for t in tiers]

    # Check for structural differences in risk tier systems
    tier_counts = {
        fw_name: len(levels) for fw_name, levels in risk_approaches.items()
    }
    if len(set(tier_counts.values())) > 1:
        conflicting_requirements.append({
            "area": "Risk Classification Structure",
            "conflict": (
                "Frameworks use different numbers of risk tiers: "
                + ", ".join(
                    f"{fw} ({count} tiers)"
                    for fw, count in tier_counts.items()
                )
            ),
        })

    # Check for data residency conflicts
    residency_reqs = {}
    for fw_data in frameworks_data:
        fw_name = fw_data.get("display_name", "")
        residency = fw_data.get("data_residency_requirements", [])
        if residency:
            residency_reqs[fw_name] = residency

    if len(residency_reqs) > 1:
        all_regions = set()
        for regions in residency_reqs.values():
            all_regions.update(regions)
        if len(all_regions) > 1:
            conflicting_requirements.append({
                "area": "Data Residency",
                "conflict": (
                    "Different data residency requirements: "
                    + ", ".join(
                        f"{fw}: {', '.join(regions)}"
                        for fw, regions in residency_reqs.items()
                    )
                ),
            })

    # Generate harmonized approach
    harmonized_parts = []
    if overlapping_requirements:
        harmonized_parts.append(
            "Implement shared requirements first to maximize compliance coverage"
        )
    if conflicting_requirements:
        harmonized_parts.append(
            "For conflicting requirements, adopt the strictest standard to ensure "
            "compliance across all jurisdictions"
        )
    if residency_reqs:
        harmonized_parts.append(
            "Deploy in regions that satisfy all data residency constraints simultaneously"
        )
    harmonized_parts.append(
        "Maintain documentation that addresses the union of all framework requirements"
    )

    harmonized_approach = ". ".join(harmonized_parts) + "."

    return {
        "frameworks": framework_ids,
        "overlapping_requirements": overlapping_requirements,
        "conflicting_requirements": conflicting_requirements,
        "harmonized_approach": harmonized_approach,
    }


@tool
def get_framework_metadata(framework_id: str) -> dict:
    """Return metadata for a governance framework.

    Retrieves display name, last updated date, version, and source URL
    for the specified framework.

    Args:
        framework_id: The governance framework identifier (e.g., 'eu_ai_act').

    Returns:
        A dict with framework_id, display_name, last_updated, version,
        source_url, and recent_changes fields.
    """
    try:
        data = get_framework(framework_id)
    except FileNotFoundError:
        return {
            "framework_id": framework_id,
            "display_name": framework_id,
            "last_updated": None,
            "version": None,
            "source_url": None,
            "recent_changes": [],
        }

    return {
        "framework_id": framework_id,
        "display_name": data.get("display_name", framework_id),
        "last_updated": data.get("last_updated"),
        "version": data.get("version"),
        "source_url": data.get("source_url"),
        "recent_changes": data.get("recent_changes", []),
    }


def _matches_criterion(
    criterion: str,
    description: str,
    intended_purpose: str,
    data_types: list[str],
    ai_techniques: list[str],
    risk_indicators: list[str],
    use_case_category: str,
) -> bool:
    """Check if a project matches a risk tier criterion.

    Uses keyword matching to determine if the project's attributes
    align with a given risk criterion.
    """
    criterion_keywords = _extract_keywords(criterion)

    # Check against description and intended purpose
    combined_text = f"{description} {intended_purpose}"
    for keyword in criterion_keywords:
        if keyword in combined_text:
            return True

    # Check against data types
    for dtype in data_types:
        for keyword in criterion_keywords:
            if keyword in dtype:
                return True

    # Check against risk indicators
    for indicator in risk_indicators:
        indicator_lower = indicator.lower()
        for keyword in criterion_keywords:
            if keyword in indicator_lower:
                return True

    # Check use case category alignment
    category_criterion_map = {
        "autonomous_decision": [
            "autonomous", "decision", "employment", "credit",
            "access to", "recruitment", "termination",
        ],
        "monitoring_surveillance": [
            "surveillance", "biometric", "monitoring", "identification",
            "remote", "real-time",
        ],
        "safety_critical": [
            "critical infrastructure", "safety", "health", "medical",
        ],
    }
    if use_case_category in category_criterion_map:
        for kw in category_criterion_map[use_case_category]:
            if kw in criterion:
                return True

    return False


def _extract_keywords(criterion: str) -> list[str]:
    """Extract meaningful keywords from a criterion string."""
    key_phrases = [
        "biometric", "identification", "critical infrastructure",
        "education", "vocational", "employment", "recruitment",
        "credit scoring", "insurance", "law enforcement",
        "migration", "asylum", "border", "justice", "democratic",
        "social scoring", "surveillance", "manipulation",
        "vulnerable", "children", "emotion recognition",
        "facial", "autonomous", "safety", "health",
        "chatbot", "interact", "synthetic", "deepfake",
        "content generation", "spam", "video game", "inventory",
        "worker management", "self-employment", "promotion",
        "termination", "essential", "public service",
    ]

    matched = [phrase for phrase in key_phrases if phrase in criterion]
    return matched if matched else [criterion[:30]]


def _risk_level_priority(risk_level: str) -> int:
    """Return numeric priority for a risk level (higher = more risky)."""
    priorities = {
        "unacceptable": 4,
        "high": 3,
        "limited": 2,
        "minimal": 1,
    }
    return priorities.get(risk_level, 0)


def country_policy_agent(state: dict[str, Any]) -> dict[str, Any]:
    """Classify risk and generate compliance obligations for selected frameworks.

    Uses GPT-4 with governance framework knowledge to classify the project's
    risk level and generate specific compliance obligations. Falls back to
    deterministic classification if LLM is unavailable.

    Args:
        state: Current graph state with enriched_profile and selected_frameworks.

    Returns:
        Partial state dict with risk_classifications, compliance_obligations,
        framework_comparison, framework_metadata, and governance_constraints.
    """
    enriched_profile = state.get("enriched_profile") or state.get("project_profile") or {}
    selected_frameworks = state.get("selected_frameworks", [])

    if not selected_frameworks:
        return {
            "risk_classifications": [],
            "compliance_obligations": [],
            "framework_comparison": None,
            "framework_metadata": [],
            "governance_constraints": {},
        }

    # Resolve framework IDs
    framework_ids = []
    for fw in selected_frameworks:
        fw_id = fw.value if hasattr(fw, "value") else fw
        framework_ids.append(fw_id)

    # Load framework metadata
    framework_metadata_list = []
    for fw_id in framework_ids:
        metadata = get_framework_metadata.invoke({"framework_id": fw_id})
        framework_metadata_list.append(metadata)

    # Load framework data for LLM context
    framework_data = []
    for fw_id in framework_ids:
        try:
            data = get_framework(fw_id)
            framework_data.append(data)
        except FileNotFoundError:
            logger.warning(f"Framework data not found for: {fw_id}")
            continue

    if not framework_data:
        return {
            "risk_classifications": [],
            "compliance_obligations": [],
            "framework_comparison": None,
            "framework_metadata": framework_metadata_list,
            "governance_constraints": {},
        }

    # Try LLM-based classification first
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        context = {
            "project_profile": enriched_profile,
            "frameworks": framework_data,
            "multiple_frameworks": len(framework_data) > 1,
        }
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=json.dumps(context, default=str)),
        ]
        response = llm.invoke(messages)
        result = json.loads(response.content)

        # Ensure is_flagged is set correctly for all classifications
        risk_classifications = result.get("risk_classifications", [])
        for rc in risk_classifications:
            risk_level = rc.get("risk_level", "minimal")
            rc["is_flagged"] = risk_level in ("high", "unacceptable")

        return {
            "risk_classifications": risk_classifications,
            "compliance_obligations": result.get("compliance_obligations", []),
            "framework_comparison": result.get("framework_comparison"),
            "framework_metadata": framework_metadata_list,
            "governance_constraints": result.get("governance_constraints", {}),
        }

    except Exception as e:
        logger.warning(f"LLM classification failed, using deterministic fallback: {e}")

    # Fallback: deterministic classification using tools
    risk_classifications = []
    compliance_obligations = []
    data_residency_regions = []

    for fw_id in framework_ids:
        # Classify risk deterministically
        classification = classify_risk.invoke({
            "profile": enriched_profile,
            "framework_id": fw_id,
        })
        risk_classifications.append(classification)

        # Get obligations for the classified risk level
        risk_level = classification.get("risk_level", "minimal")
        obligations = get_obligations.invoke({
            "framework_id": fw_id,
            "risk_level": risk_level,
        })
        compliance_obligations.extend(obligations)

        # Collect data residency requirements
        try:
            fw_data = get_framework(fw_id)
            residency = fw_data.get("data_residency_requirements") or []
            data_residency_regions.extend(residency)
        except FileNotFoundError:
            pass

    # Generate framework comparison if multiple frameworks
    framework_comparison = None
    if len(framework_ids) > 1:
        framework_comparison = compare_frameworks.invoke({
            "framework_ids": framework_ids,
            "profile": enriched_profile,
        })

    # Build governance constraints
    has_high_risk = any(
        rc.get("risk_level") in ("high", "unacceptable")
        for rc in risk_classifications
    )
    governance_constraints = {
        "data_residency_regions": list(set(data_residency_regions)),
        "requires_human_oversight": has_high_risk,
        "requires_conformity_assessment": has_high_risk,
    }

    return {
        "risk_classifications": risk_classifications,
        "compliance_obligations": compliance_obligations,
        "framework_comparison": framework_comparison,
        "framework_metadata": framework_metadata_list,
        "governance_constraints": governance_constraints,
    }
