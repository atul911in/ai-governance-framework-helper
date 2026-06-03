"""Enumeration models for the AI Governance Framework Helper."""

from enum import Enum


class IndustrySector(str, Enum):
    """Industry sectors supported by the governance framework."""

    BANKING = "banking"
    INSURANCE = "insurance"
    HEALTH = "health"
    RETAIL = "retail"
    TECHNOLOGY = "technology"
    GOVERNMENT = "government"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    TELECOMMUNICATIONS = "telecommunications"


class DetailLevel(str, Enum):
    """Level of detail for governance advice output."""

    EXECUTIVE_SUMMARY = "executive_summary"
    STANDARD = "standard"
    DETAILED = "detailed"


class RiskLevel(str, Enum):
    """AI system risk classification levels."""

    UNACCEPTABLE = "unacceptable"
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"


class GovernanceFrameworkId(str, Enum):
    """Identifiers for supported governance frameworks."""

    EU_AI_ACT = "eu_ai_act"
    SINGAPORE_MAIGF = "singapore_maigf"
    US_NIST_AI_RMF = "us_nist_ai_rmf"
    UK_AI_REGULATION = "uk_ai_regulation"
    CANADA_AIDA = "canada_aida"
    AUSTRALIA_AI_ETHICS = "australia_ai_ethics"
    ISO_42001 = "iso_42001"
    AWS_AGENTIC_AI = "aws_agentic_ai_governance"
    MICROSOFT_ACS = "microsoft_acs"
    OPENAI_FRONTIER = "openai_frontier_governance"


class AdviceCategory(str, Enum):
    """Categories of governance advice."""

    DATA_GOVERNANCE = "data_governance"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    FAIRNESS = "fairness"
    SAFETY = "safety"
    HUMAN_OVERSIGHT = "human_oversight"


class TechCategory(str, Enum):
    """Technology stack categories."""

    CLOUD_PLATFORM = "cloud_platform"
    ORCHESTRATION_FRAMEWORK = "orchestration_framework"
    LLM_MODEL = "llm_model"
