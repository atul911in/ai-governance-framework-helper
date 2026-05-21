"""Validation and error models for the AI Governance Framework Helper."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ValidationError(BaseModel):
    """A field-level validation error."""

    field: str
    message: str
    code: str  # e.g., "required", "min_length", "invalid_value"


class ValidationResult(BaseModel):
    """Result of input validation, containing validity status and any errors."""

    valid: bool
    errors: list[ValidationError] = []


class ErrorResponse(BaseModel):
    """Standardized API error response format."""

    error_code: str  # Machine-readable error code
    message: str  # Human-readable description
    details: Optional[list[ValidationError]] = None  # Field-level errors
    correlation_id: str  # For debugging/support
    timestamp: datetime
