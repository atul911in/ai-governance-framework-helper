# AI Governance Framework Helper - Design Document

## Overview

The AI Governance Framework Helper is a multi-agent application built on **LangGraph** with **OpenAI GPT-4o**. It helps organizations navigate AI governance requirements across different countries and regulatory frameworks by providing tailored compliance advice.

## Architecture

### Multi-Agent Supervisor Pattern

User Input -> Input Validation -> Supervisor -> User Persona Agent -> Supervisor -> Country Policy Agent -> Industry Agent -> Supervisor -> Technology Recommender -> Aggregator -> Output Formatting -> Final Advice

### Agents

| Agent | Responsibility | Model |
|-------|---------------|-------|
| Supervisor | Routes requests to appropriate agents based on state | Deterministic router |
| User Persona | Validates input, enriches profile with risk indicators | GPT-4o |
| Country Policy | Classifies risk per framework, generates obligations | GPT-4o |
| Industry-Specific | Provides sector-tailored compliance guidance | GPT-4o |
| Technology Recommender | Recommends platforms, frameworks, LLMs | GPT-4o |

### Agent Communication

Agents communicate exclusively through a shared LangGraph state object. The supervisor reads the current state and routes to the next agent. Each agent writes its output back to state.

## Supported Governance Frameworks

| Framework | Country/Region | Type |
|-----------|---------------|------|
| EU AI Act | European Union | Risk-based legislation |
| UK AI Regulation | United Kingdom | Principles-based (5 principles) |
| US NIST AI RMF | United States | Voluntary risk management |
| Singapore MAIGF | Singapore | Governance guidance |
| Canada AIDA | Canada | Proposed legislation |
| Australia AI Ethics | Australia | Voluntary ethics principles |
| ISO 42001 | International | AI management system standard |

## Data Sources

- EU AI Act: https://artificialintelligenceact.eu/
- UK AI Regulation: UK Gov PDF
- US NIST AI RMF: https://www.nist.gov/artificial-intelligence
- Singapore MAIGF: https://www.pdpc.gov.sg
- Canada AIDA: https://www.parl.ca/legisinfo/en/bill/44-1/c-27
- Australia AI Ethics: https://www.industry.gov.au/publications/australias-artificial-intelligence-ethics-framework
- ISO 42001: https://www.iso.org/standard/81230.html

## Supported Industries

Banking, Insurance, Healthcare, Retail, Technology, Government, Education, Manufacturing, Telecommunications

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Agent Orchestration | LangGraph (StateGraph) |
| LLM | OpenAI GPT-4o |
| Backend API | FastAPI |
| Frontend UI | Streamlit |
| Data Validation | Pydantic v2 |
| Knowledge Base | Structured JSON files |
| Export | Markdown + PDF (WeasyPrint) |
| Observability | LangSmith |
| Deployment | Streamlit Community Cloud |

## Key Design Decisions

1. Deterministic fallbacks - Every agent has a tool-based fallback if GPT-4o is unavailable
2. Knowledge base as JSON - Framework data is curated and structured, not hallucinated
3. Supervisor pattern - Simple routing logic, easy to debug and extend
4. Sequential execution - Country Policy then Industry for simplicity
5. Data residency filtering - Technology recommendations respect governance constraints

## Deployment

### Streamlit Community Cloud
- Entry point: streamlit_app.py
- Secrets: OPENAI_API_KEY, LANGCHAIN_API_KEY (optional), LANGCHAIN_PROJECT (optional)

### Docker
docker-compose up --build (API on port 8000, UI on port 8501)

### Local
pip install -r requirements.txt
streamlit run streamlit_app.py
