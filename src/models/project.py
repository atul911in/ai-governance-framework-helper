"""Project profile models for the AI Governance Framework Helper."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.models.enums import IndustrySector


class ProjectProfileInput(BaseModel):
    """User-submitted project information."""

    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=50, max_length=5000)
    ai_techniques: list[str] = Field(min_length=1)
    data_types: list[str] = Field(min_length=1)
    deployment_region: str
    target_users: str
    intended_purpose: str
    industry_sector: IndustrySector


class ProjectProfile(ProjectProfileInput):
    """Validated and stored project profile."""

    id: str
    created_at: datetime
    updated_at: datetime
