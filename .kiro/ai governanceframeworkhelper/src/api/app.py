"""FastAPI application for the AI Governance Framework Helper."""

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel, Field

from src.knowledge_base.loader import get_all_frameworks, get_framework
from src.models.enums import DetailLevel, GovernanceFrameworkId, IndustrySector
from src.models.errors import ErrorResponse

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Governance Framework Helper",
    description="Multi-agent system providing AI governance guidance across jurisdictions.",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------


class ProjectProfileInput(BaseModel):
    """User-submitted project information for API input."""

    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=50, max_length=5000)
    ai_techniques: list[str] = Field(min_length=1)
    data_types: list[str] = Field(min_length=1)
    deployment_region: str
    target_users: str
    intended_purpose: str
    industry_sector: IndustrySector


class ProjectProfileResponse(ProjectProfileInput):
    """Response model for a created project profile."""

    id: str
    created_at: datetime
    updated_at: datetime


class AdviceRequest(BaseModel):
    """Request body for advice generation."""

    project_profile: dict
    selected_frameworks: list[str] = Field(min_length=1)
    detail_level: str = "standard"


class ExportRequest(BaseModel):
    """Request body for exporting compliance advice."""

    advice: dict
    format: str = "pdf"  # "pdf" or "markdown"


class FrameworkSummary(BaseModel):
    """Summary representation of a governance framework."""

    framework_id: str
    display_name: str
    country_or_region: str
    summary: str
    last_updated: str = ""
    version: str = ""


class IndustrySummaryResponse(BaseModel):
    """Summary representation of an industry sector."""

    sector: str
    display_name: str


# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------

_projects: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Retry helper
# ---------------------------------------------------------------------------

MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 2.0


def _invoke_graph_with_retry(graph, initial_state: dict, retries: int = MAX_RETRIES) -> dict:
    """Invoke the LangGraph state graph with retry logic for OpenAI API failures.

    Retries up to `retries` times with exponential backoff (2s, 4s, 8s).

    Args:
        graph: Compiled LangGraph state graph.
        initial_state: Initial state dictionary.
        retries: Maximum number of retry attempts.

    Returns:
        The final state dictionary from the graph invocation.

    Raises:
        Exception: If all retries are exhausted.
    """
    last_exception: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            result = graph.invoke(initial_state)
            return result
        except Exception as e:
            last_exception = e
            error_msg = str(e).lower()
            # Retry on OpenAI-related transient errors
            is_retryable = any(
                keyword in error_msg
                for keyword in ["rate_limit", "timeout", "connection", "openai", "429", "503"]
            )
            if not is_retryable or attempt >= retries:
                raise
            backoff = INITIAL_BACKOFF_SECONDS * (2**attempt)
            logger.warning(
                f"OpenAI API error (attempt {attempt + 1}/{retries}): {e}. "
                f"Retrying in {backoff}s..."
            )
            time.sleep(backoff)

    # Should not reach here, but just in case
    raise last_exception  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Task 11.1: Project endpoints
# ---------------------------------------------------------------------------


@app.post("/api/v1/projects", response_model=ProjectProfileResponse)
async def create_project(input_data: ProjectProfileInput):
    """Create and validate a new project profile.

    Validates the input using Pydantic model constraints and creates
    a project profile with a generated ID and timestamps.
    """
    now = datetime.now(timezone.utc)
    project = {
        **input_data.model_dump(),
        "id": str(uuid.uuid4()),
        "created_at": now,
        "updated_at": now,
    }
    _projects[project["id"]] = project
    return project


@app.get("/api/v1/frameworks", response_model=list[FrameworkSummary])
async def list_frameworks():
    """List available governance frameworks with summaries."""
    try:
        frameworks = get_all_frameworks()
    except FileNotFoundError:
        return []

    return [
        FrameworkSummary(
            framework_id=fw["framework_id"],
            display_name=fw["display_name"],
            country_or_region=fw["country_or_region"],
            summary=fw["summary"],
            last_updated=fw.get("last_updated", ""),
            version=fw.get("version", ""),
        )
        for fw in frameworks
    ]


@app.get("/api/v1/frameworks/{framework_id}")
async def get_framework_detail(framework_id: str):
    """Get detailed information about a specific framework."""
    try:
        return get_framework(framework_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Framework not found: {framework_id}")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Invalid framework data: {e}")


@app.get("/api/v1/industries", response_model=list[IndustrySummaryResponse])
async def list_industries():
    """List supported industry sectors."""
    return [
        IndustrySummaryResponse(
            sector=s.value, display_name=s.value.replace("_", " ").title()
        )
        for s in IndustrySector
    ]


# ---------------------------------------------------------------------------
# Task 11.2: Advice generation endpoint
# ---------------------------------------------------------------------------


@app.post("/api/v1/advice")
async def generate_advice(request: AdviceRequest):
    """Run the full multi-agent LangGraph workflow and return compliance advice.

    Accepts an AdviceRequest with project_profile (dict), selected_frameworks
    (list of framework ID strings), and an optional detail_level.

    Implements retry logic for OpenAI API failures (3 retries, exponential backoff).
    Returns ErrorResponse with correlation ID on failure.
    """
    correlation_id = str(uuid.uuid4())

    # Validate selected_frameworks are valid enum values
    valid_framework_ids = {fw.value for fw in GovernanceFrameworkId}
    invalid_frameworks = [
        fw for fw in request.selected_frameworks if fw not in valid_framework_ids
    ]
    if invalid_frameworks:
        error_response = ErrorResponse(
            error_code="INVALID_FRAMEWORKS",
            message=f"Invalid framework IDs: {', '.join(invalid_frameworks)}",
            details=None,
            correlation_id=correlation_id,
            timestamp=datetime.now(timezone.utc),
        )
        raise HTTPException(status_code=400, detail=error_response.model_dump(mode="json"))

    # Validate detail_level
    valid_detail_levels = {dl.value for dl in DetailLevel}
    if request.detail_level not in valid_detail_levels:
        error_response = ErrorResponse(
            error_code="INVALID_DETAIL_LEVEL",
            message=f"Invalid detail level: {request.detail_level}. "
            f"Valid options: {', '.join(valid_detail_levels)}",
            details=None,
            correlation_id=correlation_id,
            timestamp=datetime.now(timezone.utc),
        )
        raise HTTPException(status_code=400, detail=error_response.model_dump(mode="json"))

    # Build initial state for the graph
    initial_state = {
        "project_profile": request.project_profile,
        "selected_frameworks": request.selected_frameworks,
        "detail_level": request.detail_level,
        "profile_valid": False,
        "validation_errors": [],
        "agents_completed": [],
        "requires_clarification": False,
        "clarification_questions": [],
        "enriched_profile": None,
        "risk_classifications": [],
        "compliance_obligations": [],
        "framework_comparison": None,
        "framework_metadata": [],
        "industry_guidance": "",
        "industry_best_practices": [],
        "additional_obligations": [],
        "technology_recommendations": [],
        "governance_constraints": {},
        "final_advice": None,
        "next_agent": "",
        "messages": [],
    }

    try:
        from src.graph.builder import build_governance_graph

        graph = build_governance_graph()
        result = _invoke_graph_with_retry(graph, initial_state)
        final_advice = result.get("final_advice")
        if final_advice is None:
            error_response = ErrorResponse(
                error_code="ADVICE_GENERATION_FAILED",
                message="The multi-agent workflow completed but did not produce final advice.",
                details=None,
                correlation_id=correlation_id,
                timestamp=datetime.now(timezone.utc),
            )
            raise HTTPException(status_code=500, detail=error_response.model_dump(mode="json"))
        return final_advice
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Advice generation failed [correlation_id={correlation_id}]: {e}")
        error_response = ErrorResponse(
            error_code="INTERNAL_ERROR",
            message=f"Advice generation failed: {str(e)}",
            details=None,
            correlation_id=correlation_id,
            timestamp=datetime.now(timezone.utc),
        )
        raise HTTPException(status_code=500, detail=error_response.model_dump(mode="json"))


# ---------------------------------------------------------------------------
# Task 11.3: Export endpoint
# ---------------------------------------------------------------------------


@app.post("/api/v1/export")
async def export_advice(request: ExportRequest):
    """Export compliance advice as PDF or Markdown.

    Accepts an ExportRequest with advice (dict) and format ("pdf" or "markdown").
    Returns the generated document content.

    For markdown format, returns plain text with the markdown content.
    For PDF format, attempts PDF generation; falls back to markdown if PDF fails.
    """
    correlation_id = str(uuid.uuid4())

    # Validate format
    if request.format not in ("pdf", "markdown"):
        error_response = ErrorResponse(
            error_code="INVALID_EXPORT_FORMAT",
            message=f"Invalid export format: {request.format}. Must be 'pdf' or 'markdown'.",
            details=None,
            correlation_id=correlation_id,
            timestamp=datetime.now(timezone.utc),
        )
        raise HTTPException(status_code=400, detail=error_response.model_dump(mode="json"))

    # Extract project profile from advice for the export
    project_profile = request.advice.get("project_profile", {})

    try:
        from src.export.markdown import generate_markdown

        if request.format == "markdown":
            md_content = generate_markdown(request.advice, project_profile)
            return PlainTextResponse(
                content=md_content,
                media_type="text/markdown",
                headers={"Content-Disposition": "attachment; filename=compliance_report.md"},
            )
        else:
            # PDF format
            try:
                from src.export.pdf import generate_pdf

                pdf_bytes = generate_pdf(request.advice, project_profile)
                if pdf_bytes:
                    return Response(
                        content=pdf_bytes,
                        media_type="application/pdf",
                        headers={
                            "Content-Disposition": "attachment; filename=compliance_report.pdf"
                        },
                    )
                else:
                    # Fallback to markdown if PDF generation returns empty
                    md_content = generate_markdown(request.advice, project_profile)
                    return PlainTextResponse(
                        content=md_content,
                        media_type="text/markdown",
                        headers={
                            "Content-Disposition": (
                                "attachment; filename=compliance_report.md"
                            )
                        },
                    )
            except ImportError:
                # WeasyPrint not available, fallback to markdown
                logger.warning("PDF generation unavailable, falling back to markdown export.")
                md_content = generate_markdown(request.advice, project_profile)
                return PlainTextResponse(
                    content=md_content,
                    media_type="text/markdown",
                    headers={
                        "Content-Disposition": "attachment; filename=compliance_report.md"
                    },
                )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export failed [correlation_id={correlation_id}]: {e}")
        error_response = ErrorResponse(
            error_code="EXPORT_FAILED",
            message=f"Export generation failed: {str(e)}",
            details=None,
            correlation_id=correlation_id,
            timestamp=datetime.now(timezone.utc),
        )
        raise HTTPException(status_code=500, detail=error_response.model_dump(mode="json"))
