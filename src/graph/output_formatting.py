"""Output Formatting node for the AI Governance Framework Helper.

Formats the final advice based on the requested detail level:
- executive_summary: max 500 words total, top obligations by priority
- standard: no modification
- detailed: implementation checklists and expanded guidance
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

MAX_EXECUTIVE_SUMMARY_WORDS = 500


def output_formatting_node(state: dict[str, Any]) -> dict[str, Any]:
    """Format the final advice based on the requested detail level.

    Args:
        state: Current graph state with final_advice and detail_level.

    Returns:
        Partial state dict with {"final_advice": formatted_advice}.
    """
    final_advice = state.get("final_advice")
    if final_advice is None:
        return {"final_advice": None}

    detail_level = final_advice.get("detail_level", "standard")

    if detail_level == "executive_summary":
        final_advice = _format_executive_summary(final_advice)
    elif detail_level == "detailed":
        final_advice = _format_detailed(final_advice, state)
    # standard: no additional formatting needed

    return {"final_advice": final_advice}


def _count_words(text: str) -> int:
    """Count words in a text string."""
    if not text:
        return 0
    return len(text.split())


def _truncate_to_word_limit(text: str, max_words: int) -> str:
    """Truncate text to a maximum number of words."""
    if not text:
        return text
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def _get_advice_word_count(advice: dict) -> int:
    """Calculate total word count of the advice text content.

    Counts words in industry_guidance and all obligation descriptions
    plus their recommended_actions.
    """
    total = 0
    total += _count_words(advice.get("industry_guidance", ""))

    for obligation in advice.get("obligations", []):
        if isinstance(obligation, dict):
            total += _count_words(obligation.get("obligation", ""))
            for action in obligation.get("recommended_actions", []):
                total += _count_words(action)

    return total


def _format_executive_summary(advice: dict) -> dict:
    """Truncate advice to executive summary format (max 500 words total).

    Strategy:
    1. Sort obligations by priority, keep top 3-5
    2. Truncate industry_guidance to fit within word budget
    3. Ensure total word count doesn't exceed 500 words
    """
    advice = dict(advice)  # shallow copy to avoid mutating original

    # Sort obligations by priority and limit to top 5
    obligations = list(advice.get("obligations", []))
    priority_order = {"high": 0, "medium": 1, "low": 2}
    sorted_obligations = sorted(
        obligations,
        key=lambda x: priority_order.get(
            x.get("priority", "low") if isinstance(x, dict) else "low", 2
        ),
    )
    # Keep top 5 obligations initially
    advice["obligations"] = sorted_obligations[:5]

    # Limit tech recommendations to 1 per category for brevity
    tech_recs = advice.get("technology_recommendations", [])
    seen_categories = set()
    filtered_recs = []
    for rec in tech_recs:
        cat = rec.get("category", "") if isinstance(rec, dict) else ""
        if cat not in seen_categories:
            seen_categories.add(cat)
            filtered_recs.append(rec)
    advice["technology_recommendations"] = filtered_recs

    # Enforce the 500-word total limit
    # Calculate word budget: reserve words for obligations, truncate guidance
    obligation_words = 0
    for obligation in advice["obligations"]:
        if isinstance(obligation, dict):
            obligation_words += _count_words(obligation.get("obligation", ""))
            for action in obligation.get("recommended_actions", []):
                obligation_words += _count_words(action)

    # Allocate remaining word budget to industry_guidance
    guidance_budget = MAX_EXECUTIVE_SUMMARY_WORDS - obligation_words
    if guidance_budget < 50:
        # If obligations take too much space, reduce to top 3
        advice["obligations"] = sorted_obligations[:3]
        obligation_words = 0
        for obligation in advice["obligations"]:
            if isinstance(obligation, dict):
                obligation_words += _count_words(obligation.get("obligation", ""))
                for action in obligation.get("recommended_actions", []):
                    obligation_words += _count_words(action)
        guidance_budget = MAX_EXECUTIVE_SUMMARY_WORDS - obligation_words

    # Truncate industry guidance to fit budget
    guidance_budget = max(guidance_budget, 0)
    guidance = advice.get("industry_guidance", "")
    advice["industry_guidance"] = _truncate_to_word_limit(guidance, guidance_budget)

    # Final check: if still over budget, progressively trim obligations
    total = _get_advice_word_count(advice)
    while total > MAX_EXECUTIVE_SUMMARY_WORDS and len(advice["obligations"]) > 1:
        advice["obligations"] = advice["obligations"][:-1]
        total = _get_advice_word_count(advice)

    # Last resort: truncate guidance further if still over
    if total > MAX_EXECUTIVE_SUMMARY_WORDS:
        guidance = advice.get("industry_guidance", "")
        words = guidance.split() if guidance else []
        overage = total - MAX_EXECUTIVE_SUMMARY_WORDS
        new_limit = max(len(words) - overage, 0)
        advice["industry_guidance"] = _truncate_to_word_limit(guidance, new_limit)

    logger.info(
        "Executive summary formatted: %d words, %d obligations.",
        _get_advice_word_count(advice),
        len(advice.get("obligations", [])),
    )

    return advice


def _format_detailed(advice: dict, state: dict[str, Any]) -> dict:
    """Add implementation checklists and expand guidance for detailed output.

    Enhancements:
    1. Keep all obligations (no truncation)
    2. Add implementation_checklist to each obligation with step-by-step items
    3. Expand industry_guidance with best practices
    """
    advice = dict(advice)  # shallow copy

    obligations = list(advice.get("obligations", []))

    for obligation in obligations:
        if not isinstance(obligation, dict):
            continue

        actions = obligation.get("recommended_actions", [])
        docs = obligation.get("documentation_requirements", [])

        # Build step-by-step implementation checklist
        checklist = []
        for i, action in enumerate(actions, 1):
            checklist.append({
                "step": i,
                "item": action,
                "completed": False,
            })
        for doc in docs:
            checklist.append({
                "step": len(checklist) + 1,
                "item": f"Prepare documentation: {doc}",
                "completed": False,
            })

        obligation["implementation_checklist"] = checklist

    advice["obligations"] = obligations

    # Expand industry_guidance with best practices
    # Best practices may be in the advice dict (from aggregator) or in state
    industry_best_practices = (
        advice.get("industry_best_practices")
        or state.get("industry_best_practices")
        or []
    )
    if industry_best_practices:
        guidance = advice.get("industry_guidance", "")
        practices_section = "\n\nBest Practices:\n" + "\n".join(
            f"- {practice}" for practice in industry_best_practices
        )
        advice["industry_guidance"] = guidance + practices_section

    logger.info(
        "Detailed format applied: %d obligations with checklists.",
        len(obligations),
    )

    return advice
