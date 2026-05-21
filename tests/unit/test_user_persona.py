"""Unit tests for the User Persona Agent."""

import pytest
from unittest.mock import patch, MagicMock

from src.agents.user_persona import (
    user_persona_agent,
    validate_profile,
    enrich_profile,
    determine_detail_level,
)
from src.models.enums import DetailLevel, IndustrySector


def _valid_profile_dict():
    """Return a valid project profile as a dict."""
    return {
        "name": "Test AI Project",
        "description": "A" * 100,
        "ai_techniques": ["machine_learning", "deep_learning"],
        "data_types": ["personal_data", "text"],
        "deployment_region": "EU",
        "target_users": "internal employees",
        "intended_purpose": "automate document review and classification",
        "industry_sector": "banking",
    }


class TestValidateProfileTool:
    """Tests for the validate_profile tool."""

    def test_valid_profile_passes(self):
        result = validate_profile.invoke({"profile": _valid_profile_dict()})
        assert result["valid"] is True
        assert result["errors"] == []

    def test_missing_name_fails(self):
        profile = _valid_profile_dict()
        del profile["name"]
        result = validate_profile.invoke({"profile": profile})
        assert result["valid"] is False
        assert any("name" in e for e in result["errors"])

    def test_empty_description_fails(self):
        profile = _valid_profile_dict()
        profile["description"] = ""
        result = validate_profile.invoke({"profile": profile})
        assert result["valid"] is False
        assert any("description" in e.lower() for e in result["errors"])

    def test_short_description_fails(self):
        profile = _valid_profile_dict()
        profile["description"] = "Too short"
        result = validate_profile.invoke({"profile": profile})
        assert result["valid"] is False
        assert any("50 characters" in e for e in result["errors"])

    def test_long_description_fails(self):
        profile = _valid_profile_dict()
        profile["description"] = "A" * 5001
        result = validate_profile.invoke({"profile": profile})
        assert result["valid"] is False
        assert any("5000" in e for e in result["errors"])

    def test_empty_ai_techniques_fails(self):
        profile = _valid_profile_dict()
        profile["ai_techniques"] = []
        result = validate_profile.invoke({"profile": profile})
        assert result["valid"] is False
        assert any("ai_techniques" in e for e in result["errors"])


class TestEnrichProfileTool:
    """Tests for the enrich_profile tool."""

    def test_enriches_with_risk_indicators_from_data_types(self):
        profile = _valid_profile_dict()
        profile["data_types"] = ["biometric_data", "health_records"]
        result = enrich_profile.invoke({"profile": profile})
        assert "processes biometric data" in result["risk_indicators"]
        assert "processes health data" in result["risk_indicators"]

    def test_enriches_with_use_case_category(self):
        profile = _valid_profile_dict()
        profile["intended_purpose"] = "automate hiring decisions without human review"
        result = enrich_profile.invoke({"profile": profile})
        assert result["use_case_category"] == "autonomous_decision"

    def test_infers_high_risk_for_autonomous_decisions(self):
        profile = _valid_profile_dict()
        profile["intended_purpose"] = "autonomous decision making for loan approvals"
        result = enrich_profile.invoke({"profile": profile})
        assert result["inferred_risk_level"] == "high"

    def test_infers_minimal_risk_for_simple_analysis(self):
        profile = _valid_profile_dict()
        profile["data_types"] = ["text"]
        profile["description"] = "A simple tool for analyzing sales data trends over time to produce reports for the team"
        profile["intended_purpose"] = "analyze sales data"
        result = enrich_profile.invoke({"profile": profile})
        assert result["inferred_risk_level"] == "minimal"

    def test_preserves_original_profile_fields(self):
        profile = _valid_profile_dict()
        result = enrich_profile.invoke({"profile": profile})
        assert result["name"] == profile["name"]
        assert result["description"] == profile["description"]
        assert result["industry_sector"] == profile["industry_sector"]


class TestDetermineDetailLevelTool:
    """Tests for the determine_detail_level tool."""

    def test_executive_summary(self):
        result = determine_detail_level.invoke({"preference": "executive summary"})
        assert result == "executive_summary"

    def test_detailed(self):
        result = determine_detail_level.invoke({"preference": "detailed implementation"})
        assert result == "detailed"

    def test_standard_default(self):
        result = determine_detail_level.invoke({"preference": "standard"})
        assert result == "standard"

    def test_empty_defaults_to_standard(self):
        result = determine_detail_level.invoke({"preference": ""})
        assert result == "standard"

    def test_unknown_defaults_to_standard(self):
        result = determine_detail_level.invoke({"preference": "something random"})
        assert result == "standard"


class TestUserPersonaAgent:
    """Tests for the user_persona_agent node function."""

    def test_none_profile_returns_clarification(self):
        state = {"project_profile": None, "detail_level": None}
        result = user_persona_agent(state)
        assert result["enriched_profile"] is None
        assert result["profile_valid"] is False
        assert result["requires_clarification"] is True
        assert len(result["clarification_questions"]) > 0

    def test_defaults_detail_level_to_standard(self):
        state = {"project_profile": None, "detail_level": None}
        result = user_persona_agent(state)
        assert result["detail_level"] == DetailLevel.STANDARD

    def test_preserves_existing_detail_level(self):
        state = {
            "project_profile": None,
            "detail_level": DetailLevel.DETAILED,
        }
        result = user_persona_agent(state)
        assert result["detail_level"] == DetailLevel.DETAILED

    @patch("src.agents.user_persona.ChatOpenAI")
    def test_valid_profile_returns_enriched(self, mock_openai):
        """Test that a valid profile is enriched via LLM (mocked)."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"risk_indicators": ["processes personal data"], "use_case_category": "decision_support", "inferred_risk_level": "limited", "requires_clarification": false, "clarification_questions": []}'
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm

        state = {
            "project_profile": _valid_profile_dict(),
            "detail_level": DetailLevel.STANDARD,
        }
        result = user_persona_agent(state)
        assert result["profile_valid"] is True
        assert result["enriched_profile"] is not None
        assert result["enriched_profile"]["name"] == "Test AI Project"
        assert "risk_indicators" in result["enriched_profile"]
        assert "use_case_category" in result["enriched_profile"]

    @patch("src.agents.user_persona.ChatOpenAI")
    def test_llm_failure_uses_fallback(self, mock_openai):
        """Test that LLM failure falls back to deterministic enrichment."""
        mock_openai.side_effect = Exception("API unavailable")

        state = {
            "project_profile": _valid_profile_dict(),
            "detail_level": DetailLevel.STANDARD,
        }
        result = user_persona_agent(state)
        assert result["profile_valid"] is True
        assert result["enriched_profile"] is not None
        assert "risk_indicators" in result["enriched_profile"]
        assert "use_case_category" in result["enriched_profile"]

    def test_invalid_profile_returns_errors(self):
        """Test that an invalid profile returns validation errors."""
        state = {
            "project_profile": {"name": "Test", "description": "short"},
            "detail_level": None,
        }
        result = user_persona_agent(state)
        assert result["profile_valid"] is False
        assert result["requires_clarification"] is True
        assert len(result["clarification_questions"]) > 0

    @patch("src.agents.user_persona.ChatOpenAI")
    def test_pydantic_model_as_input(self, mock_openai):
        """Test that a Pydantic model instance is handled correctly."""
        from src.models.project import ProjectProfileInput

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"risk_indicators": [], "use_case_category": "data_analysis", "inferred_risk_level": "minimal", "requires_clarification": false, "clarification_questions": []}'
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm

        profile = ProjectProfileInput(
            name="Test Project",
            description="A" * 100,
            ai_techniques=["deep_learning"],
            data_types=["text"],
            deployment_region="US",
            target_users="customers",
            intended_purpose="chatbot for customer support",
            industry_sector=IndustrySector.TECHNOLOGY,
        )
        state = {
            "project_profile": profile,
            "detail_level": None,
        }
        result = user_persona_agent(state)
        assert result["profile_valid"] is True
        assert result["detail_level"] == DetailLevel.STANDARD
