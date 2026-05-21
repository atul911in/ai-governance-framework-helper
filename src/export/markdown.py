"""Markdown export for the AI Governance Framework Helper."""

from datetime import datetime, timezone
from typing import Any

VERSION = "1.0.0"


def generate_markdown(advice: dict, profile: dict) -> str:
    """Generate a Markdown compliance report.

    Args:
        advice: ComplianceAdvice dictionary.
        profile: ProjectProfile dictionary.

    Returns:
        Formatted Markdown string.
    """
    lines: list[str] = []
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Header
    lines.append("# AI Governance Compliance Report")
    lines.append("")
    lines.append(f"Generated: {timestamp}")
    lines.append(f"Version: {VERSION}")
    lines.append("")

    # Project Summary
    lines.append("## Project Summary")
    lines.append("")
    lines.append(f"- Name: {profile.get('name', 'N/A')}")
    lines.append(f"- Industry: {profile.get('industry_sector', 'N/A')}")
    lines.append(f"- Deployment Region: {profile.get('deployment_region', 'N/A')}")
    lines.append(f"- Target Users: {profile.get('target_users', 'N/A')}")
    lines.append(f"- Intended Purpose: {profile.get('intended_purpose', 'N/A')}")
    lines.append(f"- AI Techniques: {', '.join(profile.get('ai_techniques', []))}")
    lines.append(f"- Data Types: {', '.join(profile.get('data_types', []))}")
    lines.append("")
    lines.append(f"**Description:** {profile.get('description', 'N/A')}")
    lines.append("")

    # Selected Frameworks
    lines.append("## Selected Governance Frameworks")
    lines.append("")
    for fw in advice.get("frameworks", []):
        lines.append(f"- {fw}")
    lines.append("")

    # Risk Classification
    lines.append("## Risk Classification")
    lines.append("")
    for rc in advice.get("risk_classifications", []):
        framework_name = rc.get("framework", "Unknown")
        lines.append(f"### {framework_name}")
        lines.append("")
        lines.append(f"- Risk Level: {rc.get('risk_level', 'N/A')}")
        lines.append(f"- Explanation: {rc.get('explanation', 'N/A')}")
        if rc.get("is_flagged"):
            lines.append("- **\u26a0\ufe0f FLAGGED: High or unacceptable risk level**")
        lines.append("")
        if rc.get("key_factors"):
            lines.append("Key Factors:")
            for factor in rc["key_factors"]:
                lines.append(f"- {factor}")
            lines.append("")
        if rc.get("regulatory_obligations"):
            lines.append("Regulatory Obligations:")
            for obligation in rc["regulatory_obligations"]:
                lines.append(f"- {obligation}")
            lines.append("")

    # Compliance Obligations
    lines.append("## Compliance Obligations")
    lines.append("")
    obligations = advice.get("obligations", [])
    # Group by category
    categories: dict[str, list[dict]] = {}
    for ob in obligations:
        cat = ob.get("category", "other")
        categories.setdefault(cat, []).append(ob)

    for category, obs in categories.items():
        lines.append(f"### {_format_category(category)}")
        lines.append("")
        for ob in obs:
            lines.append(f"- Obligation: {ob.get('obligation', '')}")
            if ob.get("recommended_actions"):
                lines.append("  - Recommended Actions:")
                for action in ob["recommended_actions"]:
                    lines.append(f"    - {action}")
            lines.append(f"  - Framework Reference: {ob.get('framework_reference', 'N/A')}")
            lines.append(f"  - Priority: {ob.get('priority', 'medium')}")
            if ob.get("timeline"):
                lines.append(f"  - Timeline: {ob['timeline']}")
            lines.append("")

    # Framework Comparison
    comparison = advice.get("framework_comparison")
    if comparison:
        lines.append("## Framework Comparison")
        lines.append("")
        if comparison.get("overlapping_requirements"):
            lines.append("### Overlapping Requirements")
            lines.append("")
            for req in comparison["overlapping_requirements"]:
                lines.append(f"- {req}")
            lines.append("")
        if comparison.get("conflicting_requirements"):
            lines.append("### Conflicting Requirements")
            lines.append("")
            for conflict in comparison["conflicting_requirements"]:
                lines.append(f"- {conflict}")
            lines.append("")
        if comparison.get("harmonized_approach"):
            lines.append("### Harmonized Approach")
            lines.append("")
            lines.append(comparison["harmonized_approach"])
            lines.append("")

    # Industry Guidance
    if advice.get("industry_guidance"):
        lines.append("## Industry-Specific Guidance")
        lines.append("")
        lines.append(advice["industry_guidance"])
        lines.append("")

    # Technology Recommendations
    tech_recs = advice.get("technology_recommendations", [])
    if tech_recs:
        lines.append("## Technology Recommendations")
        lines.append("")

        # Group by category
        cloud = [r for r in tech_recs if r.get("category") == "cloud_platform"]
        orchestration = [r for r in tech_recs if r.get("category") == "orchestration_framework"]
        models = [r for r in tech_recs if r.get("category") == "llm_model"]
        other = [
            r
            for r in tech_recs
            if r.get("category") not in ("cloud_platform", "orchestration_framework", "llm_model")
        ]

        if cloud:
            lines.append("### Cloud Platforms")
            lines.append("")
            for rec in cloud:
                _append_tech_rec(lines, rec)

        if orchestration:
            lines.append("### Orchestration Frameworks")
            lines.append("")
            for rec in orchestration:
                _append_tech_rec(lines, rec)

        if models:
            lines.append("### LLM Models")
            lines.append("")
            for rec in models:
                _append_tech_rec(lines, rec)

        if other:
            lines.append("### Other")
            lines.append("")
            for rec in other:
                _append_tech_rec(lines, rec)

    # Disclaimer
    disclaimer = advice.get(
        "disclaimer", "This advice is informational and does not constitute legal counsel."
    )
    lines.append("## Disclaimer")
    lines.append("")
    lines.append(disclaimer)
    lines.append("")

    return "\n".join(lines)


def _append_tech_rec(lines: list[str], rec: dict) -> None:
    """Append a single technology recommendation to the lines list."""
    lines.append(f"**{rec.get('name', 'Unknown')}** ({rec.get('provider', '')})")
    lines.append("")
    lines.append(rec.get("description", ""))
    lines.append("")
    if rec.get("key_capabilities"):
        lines.append("Key Capabilities:")
        for cap in rec["key_capabilities"]:
            lines.append(f"- {cap}")
        lines.append("")
    if rec.get("pros"):
        lines.append("Pros:")
        for pro in rec["pros"]:
            lines.append(f"- {pro}")
        lines.append("")
    if rec.get("cons"):
        lines.append("Cons:")
        for con in rec["cons"]:
            lines.append(f"- {con}")
        lines.append("")
    if rec.get("compliance_notes"):
        lines.append(f"Compliance Notes: {rec['compliance_notes']}")
        lines.append("")
    if rec.get("context_window"):
        lines.append(f"Context Window: {rec['context_window']}")
    if rec.get("cost_per_token"):
        lines.append(f"Cost per Token: {rec['cost_per_token']}")
    if rec.get("supported_regions"):
        lines.append(f"Supported Regions: {', '.join(rec['supported_regions'])}")
    lines.append("")


def _format_category(category: str) -> str:
    """Format a category enum value into a human-readable title."""
    return category.replace("_", " ").title()
