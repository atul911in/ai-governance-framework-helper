"""Unit tests for the input validation node."""

import pytest

from src.agents.input_validation import input_validation_node
from src.models.enums import GovernanceFrameworkId, IndustrySector


def _valid_profile_dict():
    """Return a valid project profile as a dict."""
    return {
        "name": "Test AI Project",
        "description": "A" * 50,  # Minimum valid length
        "ai_techniques": ["machine_learning"],
        "data_types": ["personal_data"],
        "deployment_region": "EU",
        "target_users": "internal employees",
        "intended_purpose": "automate document review",
        "industry_sector": "banking",
    }


class TestInputValidationNode:
    """Tests for input_validation_node."""

    def test_valid_input_passes(self):
        """Valid profile and frameworks should pass validation."""
        state = {
            "project_profile": _valid_profile_dict(),
            "selected_frameworks": [GovernanceFrameworkId.EU_AI_ACT],
        }
        result = input_validation_node(state)
        assert result["profile_valid"] is True
        assert result["validation_errors"] == []

    def test_missing_profile_fails(self):
        """Missing project_profile should produce an error."""
        state = {
            "project_profile": None,
            "selected_frameworks": [GovernanceFrameworkId.EU_AI_ACT],
        }
        result = input_validation_node(state)
        assert result["profile_valid"] is False
        assert "Project profile is required." in result["validation_errors"]

    def test_empty_frameworks_fails(self):
        """Empty framework selection should produce an error."""
        state = {
            "project_profile": _valid_profile_dict(),
            "selected_frameworks": [],
        }
        result = input_validation_node(state)
        assert result["profile_valid"] is False
        assert any("framework" in e.lower() for e in result["validation_errors"])

    def test_description_too_short_fails(self):
        """Description under 50 chars should be rejected."""
        profile = _valid_profile_dict()
        profile["description"] = "Too short"
        state = {
            "project_profile": profile,
            "selected_frameworks": [GovernanceFrameworkId.EU_AI_ACT],
        }
        result = input_validation_node(state)
        assert result["profile_valid"] is False
        assert any("description" in e.lower() for e in result["validation_errors"])

    def test_description_too_long_fails(self):
        """Description over 5000 chars should be rejected."""
        profile = _valid_profile_dict()
        profile["description"] = "A" * 5001
        state = {
            "project_profile": profile,
            "selected_frameworks": [GovernanceFrameworkId.EU_AI_ACT],
        }
        result = input_validation_node(state)
        assert result["profile_valid"] is False
        assert any("description" in e.lower() for e in result["validation_errors"])

    def test_description_at_min_boundary_passes(self):
        """Description of exactly 50 chars should be accepted."""
        profile = _valid_profile_dict()
        profile["description"] = "A" * 50
        state = {
            "project_profile": profile,
            "selected_frameworks": [GovernanceFrameworkId.EU_AI_ACT],
        }
        result = input_validation_node(state)
        assert result["profile_valid"] is True

    def test_description_at_max_boundary_passes(self):
        """Description of exactly 5000 chars should be accepted."""
        profile = _valid_profile_dict()
        profile["description"] = "A" * 5000
        state = {
            "project_profile": profile,
            "selected_frameworks": [GovernanceFrameworkId.EU_AI_ACT],
        }
        result = input_validation_node(state)
        assert result["profile_valid"] is True

    def test_missing_required_field_produces_error(self):
        """Omitting a required field should produce a field-specific error."""
        profile = _valid_profile_dict()
        del profile["name"]
        state = {
            "project_profile": profile,
            "selected_frameworks": [GovernanceFrameworkId.EU_AI_ACT],
        }
        result = input_validation_node(state)
        assert result["profile_valid"] is False
        assert any("name" in e.lower() for e in result["validation_errors"])

    def test_empty_ai_techniques_fails(self):
        """Empty ai_techniques list should be rejected."""
        profile = _valid_profile_dict()
        profile["ai_techniques"] = []
        state = {
            "project_profile": profile,
            "selected_frameworks": [GovernanceFrameworkId.EU_AI_ACT],
        }
        result = input_validation_node(state)
        assert result["profile_valid"] is False
        assert any("ai_techniques" in e.lower() for e in result["validation_errors"])

    def test_invalid_framework_id_fails(self):
        """Invalid framework ID should produce an error."""
        state = {
            "project_profile": _valid_profile_dict(),
            "selected_frameworks": ["not_a_real_framework"],
        }
        result = input_validation_node(state)
        assert result["profile_valid"] is False
        assert any("invalid" in e.lower() or "framework" in e.lower() for e in result["validation_errors"])

    def test_multiple_valid_frameworks_pass(self):
        """Multiple valid frameworks should pass."""
        state = {
            "project_profile": _valid_profile_dict(),
            "selected_frameworks": [
                GovernanceFrameworkId.EU_AI_ACT,
                GovernanceFrameworkId.US_NIST_AI_RMF,
                GovernanceFrameworkId.ISO_42001,
            ],
        }
        result = input_validation_node(state)
        assert result["profile_valid"] is True
        assert result["validation_errors"] == []

    def test_returns_only_changed_keys(self):
        """Node should return only profile_valid and validation_errors."""
        state = {
            "project_profile": _valid_profile_dict(),
            "selected_frameworks": [GovernanceFrameworkId.EU_AI_ACT],
        }
        result = input_validation_node(state)
        assert set(result.keys()) == {"profile_valid", "validation_errors"}

    def test_pydantic_model_instance_as_profile(self):
        """Should handle a Pydantic model instance as project_profile."""
        from src.models.project import ProjectProfileInput

        profile = ProjectProfileInput(
            name="Test Project",
            description="A" * 100,
            ai_techniques=["deep_learning"],
            data_types=["text"],
            deployment_region="US",
            target_users="customers",
            intended_purpose="chatbot",
            industry_sector=IndustrySector.TECHNOLOGY,
        )
        state = {
            "project_profile": profile,
            "selected_frameworks": [GovernanceFrameworkId.US_NIST_AI_RMF],
        }
        result = input_validation_node(state)
        assert result["profile_valid"] is True
        assert result["validation_errors"] == []
