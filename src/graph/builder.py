"""LangGraph state graph builder for the AI Governance Framework Helper."""

import logging

from langgraph.graph import END, StateGraph

from src.agents.country_policy import country_policy_agent
from src.agents.industry_specific import industry_specific_agent
from src.agents.input_validation import input_validation_node
from src.agents.supervisor import supervisor_node, supervisor_router
from src.agents.technology_recommender import technology_recommender_agent
from src.agents.user_persona import user_persona_agent
from src.graph.aggregator import aggregator_node
from src.graph.output_formatting import output_formatting_node
from src.graph.state import GovernanceGraphState

logger = logging.getLogger(__name__)


def build_governance_graph():
    """Build and compile the governance advisory state graph."""
    graph = StateGraph(GovernanceGraphState)

    # Add all nodes
    graph.add_node("input_validation", input_validation_node)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("user_persona", user_persona_agent)
    graph.add_node("country_policy", country_policy_agent)
    graph.add_node("industry_specific", industry_specific_agent)
    graph.add_node("technology_recommender", technology_recommender_agent)
    graph.add_node("aggregator", aggregator_node)
    graph.add_node("output_formatting", output_formatting_node)

    # Set entry point
    graph.set_entry_point("input_validation")

    # Edge from input_validation to supervisor
    graph.add_edge("input_validation", "supervisor")

    # Conditional edges from supervisor using supervisor_router
    graph.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {
            "user_persona": "user_persona",
            "parallel_analysis": "country_policy",
            "technology_recommender": "technology_recommender",
            "aggregator": "aggregator",
        },
    )

    # Agent nodes route back to supervisor
    graph.add_edge("user_persona", "supervisor")
    graph.add_edge("country_policy", "industry_specific")
    graph.add_edge("industry_specific", "supervisor")
    graph.add_edge("technology_recommender", "supervisor")

    # Aggregator to output formatting to END
    graph.add_edge("aggregator", "output_formatting")
    graph.add_edge("output_formatting", END)

    # Compile the graph
    compiled = graph.compile()
    logger.info("Governance state graph compiled successfully.")
    return compiled
