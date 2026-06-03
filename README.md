# AI Governance Framework Helper

A multi-agent AI application that helps organizations navigate AI governance requirements across 10 governance frameworks from 7+ jurisdictions.

Built with **LangGraph** + **OpenAI GPT-4o** + **Streamlit**.

## Live Demo

Deploy on Streamlit Community Cloud with your own OpenAI API key.

## Features

- **10 Governance Frameworks** including EU AI Act, UK AI Regulation, US NIST AI RMF, AWS Agentic AI Governance, Microsoft ACS, and OpenAI Frontier Governance
- **9 Industry Sectors** with tailored compliance guidance
- **Multi-Agent Architecture** with 5 specialized AI agents orchestrated by a supervisor
- **Risk Classification** per framework with detailed explanations
- **Compliance Obligations** with actionable recommendations and framework references
- **Technology Recommendations** (cloud platforms, orchestration frameworks, LLM models) filtered by data residency
- **Cross-Framework Comparison** highlighting overlaps and conflicts
- **Export** to Markdown (PDF available locally)
- **LangSmith Integration** for observability and tracing

## Architecture

`
User -> Input Validation -> Supervisor -> User Persona Agent
                                       -> Country Policy Agent -> Industry Agent
                                       -> Technology Recommender Agent
                                       -> Aggregator -> Output Formatting -> Result
`

5 specialized agents communicate through a shared LangGraph state graph:
- **Supervisor** - Deterministic router
- **User Persona** - Validates and enriches project profiles
- **Country Policy** - Risk classification and compliance obligations
- **Industry-Specific** - Sector-tailored guidance
- **Technology Recommender** - Platform and model recommendations

## Supported Frameworks

| Framework | Source | Year |
|-----------|--------|------|
| EU AI Act | artificialintelligenceact.eu | 2024 |
| UK AI Regulation | UK Gov (5 Principles) | 2024 |
| US NIST AI RMF | NIST AI 100-1 | 2023 |
| Singapore MAIGF | PDPC/IMDA | 2024 |
| Canada AIDA | Parliament of Canada | 2024 |
| Australia AI Ethics | Dept of Industry | 2024 |
| ISO 42001 | ISO | 2023 |
| AWS Agentic AI Governance | AWS | 2026 |
| Microsoft Agent Control Spec | Microsoft (Open Source) | 2026 |
| OpenAI Frontier Governance | OpenAI | 2026 |

## Quick Start

### Local Development

`ash
pip install -r requirements.txt
streamlit run streamlit_app.py
`

### Environment Variables

`
OPENAI_API_KEY=sk-your-key
LANGCHAIN_API_KEY=lsv2_pt_your-key  # Optional: LangSmith tracing
LANGCHAIN_PROJECT=ai-governance-helper  # Optional
`

### Docker

`ash
docker-compose up --build
`
- API: http://localhost:8000
- UI: http://localhost:8501

## Tech Stack

- **LangGraph** - Multi-agent orchestration
- **OpenAI GPT-4o** - Agent reasoning
- **Streamlit** - Frontend UI
- **FastAPI** - REST API
- **Pydantic v2** - Data validation
- **LangSmith** - Observability

## Project Structure

`
src/
  agents/          # 5 agent implementations + input validation
  graph/           # LangGraph state graph builder
  models/          # Pydantic data models
  knowledge_base/  # JSON loader
  api/             # FastAPI endpoints
  export/          # Markdown + PDF generation
  ui/              # Streamlit pages
data/
  frameworks/      # 10 governance framework JSONs
  technology/      # Platform, orchestration, model data
  industries/      # 9 industry knowledge files
`

## License

MIT
