"""User Persona Agent for the AI Governance Framework Helper.

Enriches project profiles with inferred metadata, determines appropriate
detail level, and validates completeness for downstream agents.
"""

import json
import logging
from typing import Any

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.models.enums import DetailLevel

load_dotenv()

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert AI project analyst. Your role is to:
1. Analyze project profiles and enrich them with inferred metadata
2. Identify risk indicators from project descriptions
3. Categorize the AI use case
4. Determine if the provided information is sufficient for governance analysis

Given a project profile, you must return a JSON object with:
- "risk_indicators": list of identified risk factors (e.g., "processes biometric data", "autonomous decision-making", "affects vulnerable populations")
- "use_case_category": one of ["decision_support", "autonomous_decision", "content_generation", "data_analysis", "monitoring_surveillance", "human_interaction", "safety_critical"]
- "inferred_risk_level": one of ["high", "limited", "minimal"] based on your analysis
- "requires_clarification": boolean indicating if critical information is missing
- "clarification_questions": list of questions if clarification is needed (empty list if not)

Respond ONLY with valid JSON. No markdown, no explanation."""


@tool
def validate_profile(profile: dict) -> dict:
    """Validate completeness of a project profile.

    Checks that all required fields are present and non-empty.

    Args:
        profile: The project profile dictionary to validate.

    Returns:
        A dict with 'valid' (bool) and 'errors' (list of error strings).
    """
    required_fields = [
        "name",
        "description",
        "ai_techniques",
        "data_types",
        "deployment_region",
        "target_users",
        "intended_purpose",
        "industry_sector",
    ]
    errors = []

    for field in required_fields:
        value = profile.get(field)
        if value is None or value == "" or value == []:
            errors.append(f"Missing or empty required field: {field}")

    description = profile.get("description", "")
    if isinstance(description, str):
        if len(description) < 50:
            errors.append("Description must be at least 50 characters.")
        elif len(description) > 5000:
            errors.append("Description must not exceed 5000 characters.")

    return {"valid": len(errors) == 0, "errors": errors}


@tool
def enrich_profile(profile: dict) -> dict:
    """Enrich a project profile with inferred attributes.

    Adds risk indicators and use case category based on profile content.

    Args:
        profile: The project profile dictionary to enrich.

    Returns:
        The profile dict augmented with risk_indicators, use_case_category,
        and inferred_risk_level fields.
    """
    risk_indicators = []
    data_types = profile.get("data_types", [])
    description = profile.get("description", "").lower()
    intended_purpose = profile.get("intended_purpose", "").lower()

    # Infer risk indicators from data types
    sensitive_data_keywords = [
        "biometric", "health", "genetic", "racial", "ethnic",
        "political", "religious", "sexual", "criminal",
    ]
    for dtype in data_types:
        dtype_lower = dtype.lower()
        for keyword in sensitive_data_keywords:
            if keyword in dtype_lower:
                risk_indicators.append(f"processes {keyword} data")

    # Infer risk indicators from description
    high_risk_keywords = [
        ("vulnerable populations", "affects vulnerable populations"),
        ("children", "involves minors or children"),
        ("autonomous decision", "autonomous decision-making"),
        ("credit scoring", "used for credit scoring"),
        ("hiring", "used in employment decisions"),
        ("law enforcement", "law enforcement application"),
        ("surveillance", "surveillance capabilities"),
        ("safety critical", "safety-critical system"),
    ]
    for keyword, indicator in high_risk_keywords:
        if keyword in description or keyword in intended_purpose:
            risk_indicators.append(indicator)

    # Determine use case category
    use_case_category = "data_analysis"
    category_keywords = {
        "decision_support": ["recommend", "suggest", "assist", "support decision"],
        "autonomous_decision": ["automat", "autonomous", "self-driving", "without human"],
        "content_generation": ["generat", "creat", "write", "compose", "chatbot"],
        "monitoring_surveillance": ["monitor", "surveillance", "track", "detect"],
        "human_interaction": ["interact", "convers", "dialog", "chat"],
        "safety_critical": ["safety", "medical", "health", "critical infrastructure"],
    }
    for category, keywords in category_keywords.items():
        for kw in keywords:
            if kw in description or kw in intended_purpose:
                use_case_category = category
                break

    # Infer risk level
    inferred_risk_level = "minimal"
    if risk_indicators:
        inferred_risk_level = "limited"
    if len(risk_indicators) >= 3:
        inferred_risk_level = "high"
    if use_case_category in ("autonomous_decision", "safety_critical"):
        inferred_risk_level = "high"

    enriched = {
        **profile,
        "risk_indicators": risk_indicators,
        "use_case_category": use_case_category,
        "inferred_risk_level": inferred_risk_level,
    }
    return enriched


@tool
def determine_detail_level(preference: str) -> str:
    """Map a user preference string to a DetailLevel enum value.

    Args:
        preference: The user's preference string (e.g., "executive", "detailed",
            "standard", or empty/unknown).

    Returns:
        The corresponding DetailLevel enum value as a string.
    """
    preference_lower = preference.lower().strip() if preference else ""

    if "executive" in preference_lower or "summary" in preference_lower:
        return DetailLevel.EXECUTIVE_SUMMARY.value
    elif "detail" in preference_lower or "implementation" in preference_lower:
        return DetailLevel.DETAILED.value
    else:
        return DetailLevel.STANDARD.value


def user_persona_agent(state: dict[str, Any]) -> dict[str, Any]:
    """Enrich the project profile with inferred metadata.

    Uses GPT-4 to analyze the project profile and infer risk indicators,
    use case category, and whether additional clarification is needed.
    Falls back to deterministic tool-based enrichment if LLM is unavailable.

    Args:
        state: Current graph state with project_profile and detail_level.

    Returns:
        Partial state dict with enriched_profile, profile_valid,
        requires_clarification, clarification_questions, and detail_level.
    """
    project_profile = state.get("project_profile")
    detail_level = state.get("detail_level")

    # Set default detail level to STANDARD when not specified
    if not detail_level:
        detail_level = DetailLevel.STANDARD

    if project_profile is None:
        return {
            "enriched_profile": None,
            "profile_valid": False,
            "requires_clarification": True,
            "clarification_questions": ["Please provide your project profile."],
            "detail_level": detail_level,
        }

    # Convert profile to dict for serialization
    profile_data = (
        project_profile.model_dump()
        if hasattr(project_profile, "model_dump")
        else project_profile
    )

    # Validate the profile using the tool
    validation_result = validate_profile.invoke({"profile": profile_data})
    if not validation_result.get("valid", False):
        return {
            "enriched_profile": None,
            "profile_valid": False,
            "requires_clarification": True,
            "clarification_questions": validation_result.get("errors", []),
            "detail_level": detail_level,
        }

    # Call GPT-4 to enrich the profile with inferred metadata
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=json.dumps(profile_data, default=str)),
        ]
        response = llm.invoke(messages)
        enrichment = json.loads(response.content)
    except Exception as e:
        logger.warning(f"LLM enrichment failed, using fallback: {e}")
        # Fallback: use the deterministic enrich_profile tool
        enrichment_result = enrich_profile.invoke({"profile": profile_data})
        enrichment = {
            "risk_indicators": enrichment_result.get("risk_indicators", []),
            "use_case_category": enrichment_result.get(
                "use_case_category", "data_analysis"
            ),
            "inferred_risk_level": enrichment_result.get(
                "inferred_risk_level", "limited"
            ),
            "requires_clarification": False,
            "clarification_questions": [],
        }

    # Build enriched profile combining original data with inferred attributes
    enriched_profile = {
        **profile_data,
        "risk_indicators": enrichment.get("risk_indicators", []),
        "use_case_category": enrichment.get("use_case_category", "data_analysis"),
        "inferred_risk_level": enrichment.get("inferred_risk_level", "limited"),
    }

    requires_clarification = enrichment.get("requires_clarification", False)
    clarification_questions = enrichment.get("clarification_questions", [])

    return {
        "enriched_profile": enriched_profile,
        "profile_valid": True,
        "requires_clarification": requires_clarification,
        "clarification_questions": clarification_questions,
        "detail_level": detail_level,
    }
