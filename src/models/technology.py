"""Technology recommendation models for the AI Governance Framework Helper."""

from typing import Optional

from pydantic import BaseModel

from src.models.enums import TechCategory


class TechnologyRecommendation(BaseModel):
    """A technology recommendation with compliance context."""

    category: TechCategory
    name: str
    provider: str
    description: str
    key_capabilities: list[str]
    pros: list[str]
    cons: list[str]
    compliance_notes: str
    context_window: Optional[int] = None
    cost_per_token: Optional[str] = None
    supported_regions: Optional[list[str]] = None
