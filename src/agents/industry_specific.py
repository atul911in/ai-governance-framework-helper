"""Industry-Specific Agent for the AI Governance Framework Helper."""

import json
import logging
from typing import Any

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.knowledge_base.loader import get_industry_context
from src.models.enums import AdviceCategory

load_dotenv()

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert in industry-specific AI regulations. Given a project profile and industry knowledge, return JSON with: industry_guidance (string), industry_best_practices (list), additional_obligations (list of dicts with category, obligation, recommended_actions, documentation_requirements, timeline, framework_reference, priority). Respond ONLY with valid JSON."""


@tool
def get_industry_context_tool(sector: str) -> dict:
    """Load industry knowledge for a sector."""
    try:
        return get_industry_context(sector)
    except FileNotFoundError:
        return {"sector": sector, "regulatory_context": "", "common_ai_use_cases": [], "best_practices": [], "sector_specific_obligations": []}


@tool
def get_industry_best_practices(sector: str, use_case: str) -> list:
    """Get best practices for a sector."""
    try:
        data = get_industry_context(sector)
        return data.get("best_practices", [])
    except FileNotFoundError:
        return []


@tool
def map_industry_obligations(sector: str, framework_ids: list) -> list:
    """Map sector-specific obligations."""
    try:
        data = get_industry_context(sector)
    except FileNotFoundError:
        return []
    obligations = []
    for ob in data.get("sector_specific_obligations", []):
        obligations.append({
            "category": ob.get("category", "accountability"),
            "obligation": ob.get("obligation", ""),
            "recommended_actions": [f"Implement: {ob.get('obligation', '')}"],
            "documentation_requirements": [f"Document compliance with {ob.get('source', '')}"],
            "timeline": None,
            "framework_reference": ob.get("source", ""),
            "priority": "medium",
        })
    return obligations


def industry_specific_agent(state: dict[str, Any]) -> dict[str, Any]:
    """Generate industry-specific compliance guidance."""
    enriched_profile = state.get("enriched_profile") or state.get("project_profile") or {}
    selected_frameworks = state.get("selected_frameworks", [])

    sector = enriched_profile.get("industry_sector", "")
    if hasattr(sector, "value"):
        sector = sector.value

    if not sector:
        return {
            "industry_guidance": "No industry sector specified. General governance guidance applies.",
            "industry_best_practices": [],
            "additional_obligations": [],
        }

    framework_ids = [fw.value if hasattr(fw, "value") else fw for fw in selected_frameworks]

    # Load industry data
    industry_data = get_industry_context_tool.invoke({"sector": sector})

    # Try LLM
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        context = {"project_profile": enriched_profile, "industry_data": industry_data, "frameworks": framework_ids}
        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=json.dumps(context, default=str))]
        response = llm.invoke(messages)
        result = json.loads(response.content)
        return {
            "industry_guidance": result.get("industry_guidance", ""),
            "industry_best_practices": result.get("industry_best_practices", []),
            "additional_obligations": result.get("additional_obligations", []),
        }
    except Exception as e:
        logger.warning(f"Industry agent LLM failed, using fallback: {e}")

    # Fallback
    best_practices = get_industry_best_practices.invoke({"sector": sector, "use_case": enriched_profile.get("intended_purpose", "")})
    obligations = map_industry_obligations.invoke({"sector": sector, "framework_ids": framework_ids})
    guidance = industry_data.get("regulatory_context", "No specific industry guidance available.")

    return {
        "industry_guidance": guidance,
        "industry_best_practices": best_practices,
        "additional_obligations": obligations,
    }