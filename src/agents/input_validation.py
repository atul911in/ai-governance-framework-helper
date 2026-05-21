"""Input validation node for the AI Governance Framework Helper.

Validates user-provided project profile and framework selections
before passing to downstream agents.
"""

import logging
from typing import Any

from pydantic import ValidationError

from src.models.enums import GovernanceFrameworkId
from src.models.project import ProjectProfileInput

logger = logging.getLogger(__name__)


def input_validation_node(state: dict[str, Any]) -> dict[str, Any]:
    """Validate user input and set profile_valid flag in state.

    Validates the project_profile against ProjectProfileInput constraints
    and ensures at least one governance framework is selected.

    Args:
        state: Current graph state containing project_profile and
            selected_frameworks.

    Returns:
        Partial state dict with profile_valid and validation_errors fields.
    """
    validation_errors: list[str] = []

    # Validate project profile
    project_profile = state.get("project_profile")
    if project_profile is None:
        validation_errors.append("Project profile is required.")
    else:
        try:
            profile_data = (
                project_profile.model_dump()
                if hasattr(project_profile, "model_dump")
                else project_profile
            )
            ProjectProfileInput(**profile_data)
        except ValidationError as e:
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                msg = error["msg"]
                validation_errors.append(f"{field}: {msg}")

    # Validate framework selection
    selected_frameworks = state.get("selected_frameworks", [])
    if not selected_frameworks:
        validation_errors.append(
            "At least one governance framework must be selected."
        )
    else:
        valid_ids = {fw.value for fw in GovernanceFrameworkId}
        for fw in selected_frameworks:
            fw_value = fw.value if hasattr(fw, "value") else fw
            if fw_value not in valid_ids:
                validation_errors.append(
                    f"Invalid governance framework: {fw_value}"
                )

    # Return partial state update
    if validation_errors:
        logger.info(
            f"Input validation failed with {len(validation_errors)} error(s)."
        )
        return {
            "profile_valid": False,
            "validation_errors": validation_errors,
        }

    logger.info("Input validation passed.")
    return {
        "profile_valid": True,
        "validation_errors": [],
    }
