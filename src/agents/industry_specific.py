"""Industry-Specific Agent for the AI Governance Framework Helper.

Provides industry-tailored compliance guidance based on sector-specific
regulations, common AI use cases, and best practices.
"""

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

SYSTEM_PROMPT = """You are an expert in industry-specific AI regulations and best practices. You understand how general governance frameworks apply differently across sectors.

Given a project profile with its industry sector and the sector-specific knowledge base, provide tailored guidance that combines the industry regulatory context with the project's specific characteristics.

You must:
1. Analyze the project's use case within the industry context
2. Identify sector-specific compliance obligations beyond general framework requirements
3. Recommend industry best practices relevant to the project

Return a JSON object with:
{
  "industry_guidance": "Comprehensive paragraph of industry-specific compliance guidance tailored to this project, referencing relevant sector regulations and how they interact with the selected governance frameworks",
  "industry_best_practices": ["practice1", "practice2", "practice3"],
  "additional_obligations": [
    {
      "category": "data_governance|transparency|accountability|fairness|safety|human_oversight",
      "obligation": "Industry-specific obligation text",
      "recommended_actions": ["action1", "action2"],
      "documentation_requirements": ["doc1"],
      "timeline": null,
      "framework_reference": "Source regulation or standard",
      "priority": "high|medium|low"
    }
  ]
}

Respond ONLY with valid JSON. No markdown, no explanation."""
