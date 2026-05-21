# Implementation Plan: AI Governance Framework Helper

## Overview

This plan implements a multi-agent LangGraph application that provides AI governance guidance. The implementation proceeds incrementally: project setup, data models, knowledge base, individual agents, graph orchestration, API, export, UI, testing, and containerization. Each step builds on the previous, ensuring no orphaned code.

## Tasks

- [x] 1. Project setup and structure
  - [x] 1.1 Initialize Poetry project with pyproject.toml
    - Create pyproject.toml with Python 3.11+ requirement
    - Add dependencies: langgraph, langchain-openai, openai, fastapi, uvicorn, pydantic (v2), streamlit, hypothesis, pytest, weasyprint, python-dotenv, httpx
    - Add dev dependencies: pytest-asyncio, black, ruff, mypy
    - _Requirements: All_

  - [x] 1.2 Create project directory structure
    - Create directory layout: src/agents/, src/models/, src/knowledge_base/, src/api/, src/export/, src/ui/, src/graph/, tests/unit/, tests/integration/, data/frameworks/, data/technology/, data/industries/
    - Create __init__.py files for all packages
    - Create .env.example with required environment variables (OPENAI_API_KEY)
    - _Requirements: All_

- [x] 2. Implement core data models and enumerations
  - [x] 2.1 Create enumeration models
    - Implement src/models/enums.py with: IndustrySector, DetailLevel, RiskLevel, GovernanceFrameworkId, AdviceCategory, TechCategory
    - All enums must inherit from str, Enum for JSON serialization
    - _Requirements: 1.4, 2.2, 3.1, 4.3, 5.1, 8.6_

  - [x] 2.2 Create project profile models
    - Implement src/models/project.py with ProjectProfileInput and ProjectProfile
    - ProjectProfileInput: name (1-200 chars), description (50-5000 chars), ai_techniques (min 1), data_types (min 1), deployment_region, target_users, intended_purpose, industry_sector
    - ProjectProfile extends ProjectProfileInput with id, created_at, updated_at
    - _Requirements: 1.1, 1.2, 1.4, 1.5_

  - [x] 2.3 Create risk and compliance models
    - Implement src/models/compliance.py with RiskClassification, ComplianceObligation, FrameworkComparison
    - RiskClassification: framework, risk_level, explanation, key_factors, regulatory_obligations, is_flagged
    - ComplianceObligation: category, obligation, recommended_actions, documentation_requirements, timeline, framework_reference, priority
    - FrameworkComparison: frameworks, overlapping_requirements, conflicting_requirements, harmonized_approach
    - _Requirements: 3.1, 3.2, 3.3, 4.2, 4.3, 4.4, 4.5_

  - [x] 2.4 Create technology recommendation models
    - Implement src/models/technology.py with TechnologyRecommendation
    - Fields: category, name, provider, description, key_capabilities, pros, cons, compliance_notes, context_window, cost_per_token, supported_regions
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [x] 2.5 Create advice output and export models
    - Implement src/models/advice.py with ComplianceAdvice and ExportDocument
    - ComplianceAdvice: id, project_id, frameworks, detail_level, risk_classifications, obligations, framework_comparison, industry_guidance, technology_recommendations, generated_at, disclaimer
    - ExportDocument: advice_id, format, project_summary, content, timestamp, version
    - _Requirements: 4.2, 5.1, 6.1, 6.2, 6.3, 6.4, 7.3_

  - [x] 2.6 Create validation and error models
    - Implement src/models/errors.py with ValidationResult, ValidationError, ErrorResponse
    - ValidationResult: valid (bool), errors (list)
    - ValidationError: field, message, code
    - ErrorResponse: error_code, message, details, correlation_id, timestamp
    - _Requirements: 1.3_

  - [x] 2.7 Create LangGraph state model
    - Implement src/models/state.py with GraphState TypedDict
    - Include all state fields: project_profile, selected_frameworks, detail_level, next_agent, agents_completed, requires_clarification, clarification_questions, enriched_profile, profile_valid, validation_errors, risk_classifications, compliance_obligations, framework_comparison, framework_metadata, industry_guidance, industry_best_practices, additional_obligations, technology_recommendations, governance_constraints, final_advice, messages
    - _Requirements: All_

  - [ ]* 2.8 Write property tests for data models (Properties 1-3)
    - **Property 1: Valid input produces valid profile** - Generate arbitrary valid inputs with Hypothesis strategies; verify ProjectProfileInput accepts them and all fields match
    - **Property 2: Missing fields produce field-specific errors** - For any subset of omitted required fields, verify exactly one error per missing field
    - **Property 3: Description length boundary validation** - For strings less than 50 or greater than 5000 chars, verify rejection; for 50-5000 inclusive, verify acceptance
    - **Validates: Requirements 1.2, 1.3, 1.5**

- [x] 3. Implement knowledge base and data layer
  - [x] 3.1 Create governance framework JSON files
    - Create data/frameworks/ with one JSON file per framework: eu_ai_act.json, singapore_maigf.json, us_nist_ai_rmf.json, uk_ai_regulation.json, canada_aida.json, australia_ai_ethics.json, iso_42001.json
    - Each file follows FrameworkKnowledge schema: framework_id, display_name, country_or_region, summary, last_updated, version, risk_tiers, key_obligations, data_residency_requirements
    - Include risk tier definitions with criteria for classification
    - _Requirements: 2.1, 2.2, 2.4, 7.1, 7.2_

  - [x] 3.2 Create technology database JSON
    - Create data/technology/platforms.json with cloud platform entries (AWS, Azure, GCP) including supported regions, compliance certifications
    - Create data/technology/orchestration.json with framework entries (LangGraph, LangChain, Semantic Kernel, Bedrock Agents)
    - Create data/technology/models.json with LLM model entries including name, provider, capabilities, context_window, cost_per_token, supported_regions
    - _Requirements: 8.1, 8.2, 8.3, 8.5_

  - [x] 3.3 Create industry knowledge JSON files
    - Create data/industries/ with one JSON file per sector (banking.json, insurance.json, health.json, retail.json, technology.json, government.json, education.json, manufacturing.json, telecommunications.json)
    - Each file contains sector-specific regulatory context, common AI use cases, and best practices
    - _Requirements: 1.4, 4.3_

  - [x] 3.4 Implement knowledge base loader module
    - Implement src/knowledge_base/loader.py with functions to load and cache framework, technology, and industry JSON data
    - Include validation of loaded data against Pydantic models
    - Implement get_framework(framework_id), get_all_frameworks(), get_technology_db(), get_industry_context(sector)
    - _Requirements: 2.1, 7.1_

  - [ ]* 3.5 Write property tests for framework metadata (Properties 12-13)
    - **Property 12: Framework metadata currency** - For any framework in the knowledge base, last_updated SHALL be a valid datetime not in the future
    - **Property 13: Recent update notification** - For frameworks updated within 30 days, recent_changes notification SHALL be present; for older frameworks, it SHALL NOT
    - **Validates: Requirements 7.1, 7.2**

- [x] 4. Checkpoint - Ensure models and knowledge base are correct
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement User Persona Agent
  - [x] 5.1 Implement input validation node
    - Implement src/agents/input_validation.py with input_validation_node(state: GraphState) -> GraphState
    - Validate all required fields using Pydantic model validation
    - Return validation errors in state if invalid; set profile_valid flag
    - Reject descriptions outside 50-5000 char range
    - Reject empty framework selections
    - _Requirements: 1.2, 1.3, 1.5, 2.5_

  - [x] 5.2 Implement User Persona Agent node
    - Implement src/agents/user_persona.py with user_persona_agent(state: GraphState) -> GraphState
    - Create system prompt for profile enrichment and validation
    - Implement tools: validate_profile, enrich_profile, determine_detail_level
    - Agent enriches profile with inferred risk indicators and use case categories
    - Set default detail_level to STANDARD when not specified
    - Write enriched_profile back to state
    - _Requirements: 1.2, 3.4, 5.4_

  - [ ]* 5.3 Write property tests for validation (Properties 1-3, 6)
    - **Property 1: Valid input produces valid profile** - Verify valid inputs produce valid profiles with matching data
    - **Property 2: Missing fields produce field-specific errors** - Verify each missing field produces exactly one error
    - **Property 3: Description length boundary** - Verify boundary enforcement at 50 and 5000 chars
    - **Property 6: Insufficient information triggers clarification** - Verify ambiguous inputs set requires_clarification=True with at least one question
    - **Validates: Requirements 1.2, 1.3, 1.5, 3.4**

- [x] 6. Implement Country Policy Agent
  - [x] 6.1 Implement Country Policy Agent node
    - Implement src/agents/country_policy.py with country_policy_agent(state: GraphState) -> GraphState
    - Create system prompt with governance regulation expertise
    - Implement tools: classify_risk, get_obligations, compare_frameworks, get_framework_metadata
    - classify_risk: determine risk tier based on project profile and framework criteria
    - get_obligations: retrieve obligations filtered by risk level
    - compare_frameworks: identify overlaps and conflicts between multiple frameworks
    - Write risk_classifications, compliance_obligations, framework_comparison, framework_metadata to state
    - Set is_flagged=True for high/unacceptable risk levels
    - _Requirements: 2.3, 3.1, 3.2, 3.3, 4.2, 4.3, 4.4, 4.5, 7.1, 7.2_

  - [ ]* 6.2 Write property tests for risk classification (Properties 4-5, 7-9)
    - **Property 4: Risk classification completeness** - For any valid profile and framework, output SHALL contain valid RiskLevel, non-empty explanation, and at least one key_factor
    - **Property 5: High-risk flagging invariant** - For high/unacceptable risk, is_flagged SHALL be True and regulatory_obligations SHALL be non-empty
    - **Property 7: Compliance advice structural completeness** - Each ComplianceObligation SHALL have non-empty obligation, at least one recommended_action, at least one documentation_requirement, and non-empty framework_reference
    - **Property 8: Advice category taxonomy** - Each ComplianceObligation category SHALL be a valid AdviceCategory enum value
    - **Property 9: Multi-framework comparison completeness** - For 2+ frameworks, comparison SHALL have non-empty overlapping_requirements and harmonized_approach
    - **Validates: Requirements 2.3, 3.1, 3.2, 3.3, 4.2, 4.3, 4.4, 4.5**

- [x] 7. Implement Industry-Specific Agent
  - [x] 7.1 Implement Industry-Specific Agent node
    - Implement src/agents/industry_specific.py with industry_specific_agent(state: GraphState) -> GraphState
    - Create system prompt with industry regulation expertise
    - Implement tools: get_industry_context, map_industry_obligations, get_industry_best_practices
    - Load industry-specific knowledge from JSON data
    - Write industry_guidance, industry_best_practices, additional_obligations to state
    - _Requirements: 1.4, 4.3_

  - [ ]* 7.2 Write unit tests for Industry-Specific Agent
    - Test that each supported industry sector returns valid guidance
    - Test that industry obligations map correctly to advice categories
    - Test graceful handling when industry data is unavailable
    - _Requirements: 1.4, 4.3_

- [x] 8. Implement Technology Recommender Agent
  - [x] 8.1 Implement Technology Recommender Agent node
    - Implement src/agents/technology_recommender.py with technology_recommender_agent(state: GraphState) -> GraphState
    - Create system prompt with AI technology landscape expertise
    - Implement tools: recommend_platforms, recommend_orchestration, recommend_models, filter_by_residency
    - Load technology database from JSON
    - Filter recommendations by data residency constraints from governance_constraints in state
    - Ensure each recommendation includes pros and cons
    - Write technology_recommendations to state
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [ ]* 8.2 Write property tests for technology recommendations (Properties 14-16)
    - **Property 14: Technology recommendations category coverage and completeness** - Output SHALL contain at least one cloud_platform, one orchestration_framework, and one llm_model; each LLM SHALL have non-null name, provider, key_capabilities, context_window, cost_per_token
    - **Property 15: Technology recommendations include pros and cons** - Each TechnologyRecommendation SHALL have at least one pro and one con
    - **Property 16: Data residency filtering** - When governance constraints specify allowed regions, all recommendations with supported_regions SHALL intersect with allowed regions
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6**

- [x] 9. Checkpoint - Ensure all agents work independently
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement Supervisor Agent and LangGraph state graph
  - [x] 10.1 Implement Supervisor Agent with routing logic
    - Implement src/agents/supervisor.py with supervisor_node(state: GraphState) -> GraphState
    - Implement supervisor_router(state: GraphState) -> str routing function
    - Routing logic: if not profile_valid then user_persona; if no risk_classifications then parallel_analysis (country_policy + industry_specific); if no technology_recommendations then technology_recommender; else aggregator
    - Use GPT-4 function-calling for dynamic routing decisions
    - _Requirements: All_

  - [x] 10.2 Implement Response Aggregator node
    - Implement src/graph/aggregator.py with aggregator_node(state: GraphState) -> GraphState
    - Combine outputs from all agents into a single ComplianceAdvice object
    - Include disclaimer text in final output
    - Handle partial results gracefully (if an agent failed, mark section as unavailable)
    - _Requirements: 4.2, 7.3_

  - [x] 10.3 Implement Output Formatting node
    - Implement src/graph/output_formatting.py with output_formatting_node(state: GraphState) -> GraphState
    - Format final_advice based on detail_level (executive_summary: max 500 words, standard, detailed)
    - For executive_summary, truncate/summarize to meet word limit
    - For detailed, include step-by-step implementation recommendations and checklists
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 10.4 Build and compile the LangGraph state graph
    - Implement src/graph/builder.py with build_governance_graph() -> CompiledGraph
    - Add all nodes: input_validation, supervisor, user_persona, country_policy, industry_specific, technology_recommender, aggregator, output_formatting
    - Set entry point to input_validation
    - Add conditional edges from supervisor using supervisor_router
    - Add parallel execution branch for country_policy and industry_specific
    - Add edge from aggregator to output_formatting, output_formatting to END
    - Compile and return the graph
    - _Requirements: All_

  - [ ]* 10.5 Write property test for executive summary word limit (Property 10)
    - **Property 10: Executive summary word limit** - For any advice with detail_level=executive_summary, total word count of combined advice text SHALL not exceed 500 words
    - **Validates: Requirements 5.2**

- [x] 11. Implement FastAPI endpoints
  - [x] 11.1 Create FastAPI application with project endpoints
    - Implement src/api/app.py with FastAPI app initialization
    - Implement POST /api/v1/projects - Create and validate a new project profile
    - Implement GET /api/v1/frameworks - List available governance frameworks with summaries
    - Implement GET /api/v1/frameworks/{framework_id} - Get detailed framework information
    - Implement GET /api/v1/industries - List supported industry sectors
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.4_

  - [x] 11.2 Implement advice generation endpoint
    - Implement POST /api/v1/advice - Run the full multi-agent LangGraph workflow
    - Accept AdviceRequest with project_id, selected_frameworks, detail_level
    - Invoke the compiled state graph and return ComplianceAdvice
    - Implement error handling with ErrorResponse format and correlation IDs
    - Implement retry logic for OpenAI API failures (3 retries, exponential backoff)
    - _Requirements: 4.1, 4.2_

  - [x] 11.3 Implement export endpoint
    - Implement POST /api/v1/export - Export compliance advice as PDF or Markdown
    - Accept ExportRequest with advice_id and format (pdf/markdown)
    - Return FileResponse with generated document
    - _Requirements: 6.1, 6.4_

  - [ ]* 11.4 Write unit tests for API endpoints
    - Test project creation with valid/invalid inputs
    - Test framework listing returns all 7 frameworks
    - Test advice generation returns proper ComplianceAdvice structure
    - Test export endpoint for both PDF and Markdown formats
    - Test error responses have correct format
    - _Requirements: 1.2, 1.3, 2.2, 4.1, 6.1, 6.4_

- [x] 12. Implement export functionality
  - [x] 12.1 Implement Markdown export
    - Implement src/export/markdown.py with generate_markdown(advice: ComplianceAdvice, profile: ProjectProfile) -> str
    - Include project summary, selected frameworks, risk classifications, all compliance advice, technology recommendations
    - Include timestamp and version identifier
    - _Requirements: 6.2, 6.3, 6.4_

  - [x] 12.2 Implement PDF export with WeasyPrint
    - Implement src/export/pdf.py with generate_pdf(advice: ComplianceAdvice, profile: ProjectProfile) -> bytes
    - Create HTML template for the compliance report
    - Convert to PDF using WeasyPrint
    - Include all sections: project summary, frameworks, risk classification, compliance advice, technology recommendations
    - Include timestamp and version identifier
    - Implement fallback to Markdown if PDF generation fails
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ]* 12.3 Write property tests for export (Property 11)
    - **Property 11: Export document completeness** - For any generated ExportDocument, it SHALL contain non-null project_summary, full ComplianceAdvice content, valid timestamp, and non-empty version string
    - **Validates: Requirements 6.2, 6.3**

- [x] 13. Checkpoint - Ensure backend is fully functional
  - Ensure all tests pass, ask the user if questions arise.

- [x] 14. Implement Streamlit UI
  - [x] 14.1 Create main Streamlit application layout
    - Implement src/ui/app.py as the Streamlit entry point
    - Create multi-page layout with sidebar navigation
    - Pages: Project Input, Framework Selection, Results, Export
    - _Requirements: 1.1, 2.1_

  - [x] 14.2 Implement Project Input form page
    - Implement src/ui/pages/project_input.py
    - Create form with all required fields: project name, description, AI techniques (multi-select), data types (multi-select), deployment region, target users, intended purpose, industry sector (dropdown)
    - Implement client-side validation with error highlighting for missing/invalid fields
    - Display character count for description field
    - _Requirements: 1.1, 1.3, 1.4, 1.5_

  - [x] 14.3 Implement Framework Selection page
    - Implement src/ui/pages/framework_selection.py
    - Display frameworks organized by country/region with summary descriptions
    - Support multi-select with checkboxes
    - Show last-updated date and recent changes notification for each framework
    - Prevent proceeding without at least one selection
    - _Requirements: 2.1, 2.2, 2.4, 2.5, 7.1, 7.2_

  - [x] 14.4 Implement Results display page
    - Implement src/ui/pages/results.py
    - Display risk classification with prominent flagging for high/unacceptable risk
    - Show compliance advice organized by category tabs
    - Display framework comparison when multiple frameworks selected
    - Show technology recommendations in categorized sections
    - Include detail level selector (Executive Summary / Standard / Detailed)
    - Display disclaimer
    - _Requirements: 3.2, 3.3, 4.2, 4.3, 4.4, 5.1, 7.3, 8.6_

  - [x] 14.5 Implement Export page
    - Implement src/ui/pages/export.py
    - Provide download buttons for PDF and Markdown formats
    - Show preview of export content
    - _Requirements: 6.1, 6.4_

  - [ ]* 14.6 Write unit tests for Streamlit UI components
    - Test form validation logic
    - Test framework selection state management
    - Test detail level switching
    - _Requirements: 1.3, 2.5, 5.1_

- [x] 15. Implement integration tests
  - [ ]* 15.1 Write integration tests for full LangGraph workflow
    - Implement tests/integration/test_full_workflow.py
    - Test end-to-end advice generation with valid project profile and single framework
    - Test multi-framework comparative analysis
    - Test parallel execution of Country Policy and Industry agents
    - Test graceful degradation when an agent fails
    - Verify advice generation completes within 30 seconds
    - _Requirements: 4.1, 4.4_

  - [ ]* 15.2 Write integration tests for API endpoints
    - Implement tests/integration/test_api_endpoints.py
    - Test full request/response cycle through FastAPI
    - Test error handling and validation error responses
    - Test export endpoint generates valid PDF and Markdown files
    - _Requirements: 1.2, 1.3, 6.1, 6.4_

- [x] 16. Docker containerization
  - [x] 16.1 Create Dockerfile and docker-compose
    - Create Dockerfile with Python 3.11 base, Poetry install, WeasyPrint system dependencies
    - Create docker-compose.yml with services: api (FastAPI + uvicorn), ui (Streamlit)
    - Configure environment variables for OPENAI_API_KEY
    - Expose ports: 8000 (API), 8501 (Streamlit)
    - Create .dockerignore to exclude tests, .env, __pycache__
    - _Requirements: All_

  - [ ]* 16.2 Write smoke tests for Docker deployment
    - Test that containers build successfully
    - Test that API health endpoint responds
    - Test that Streamlit UI loads
    - _Requirements: All_

- [x] 17. Final checkpoint - Full system verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with * are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate the 16 universal correctness properties defined in the design
- Unit tests validate specific examples and edge cases
- The knowledge base JSON files should contain representative data; full regulatory content can be expanded iteratively
- All agents use OpenAI GPT-4 via langchain-openai; ensure OPENAI_API_KEY is configured before running integration tests
