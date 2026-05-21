"""Results display page for the AI Governance Framework Helper."""

import streamlit as st

from src.graph.builder import build_governance_graph


def _generate_advice_direct(
    project_profile: dict, selected_frameworks: list[str], detail_level: str
) -> dict | None:
    """Invoke the LangGraph directly to generate compliance advice."""
    try:
        graph = build_governance_graph()
        initial_state = {
            "project_profile": project_profile,
            "selected_frameworks": selected_frameworks,
            "detail_level": detail_level,
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
        result = graph.invoke(initial_state)
        return result.get("final_advice")
    except Exception as e:
        st.error(f"❌ Error generating advice: {str(e)}")
        return None


def _render_risk_classifications(risk_classifications: list[dict]):
    """Render risk classification results with prominent flagging."""
    st.subheader("⚠️ Risk Classifications")

    for rc in risk_classifications:
        risk_level = rc.get("risk_level", "unknown")
        framework = rc.get("framework", "Unknown")
        explanation = rc.get("explanation", "")
        key_factors = rc.get("key_factors", [])
        is_flagged = rc.get("is_flagged", False)

        # Color-coded risk display
        if risk_level in ("unacceptable", "high"):
            st.error(f"🚨 **{framework}**: {risk_level.upper()} RISK")
        elif risk_level == "limited":
            st.warning(f"⚠️ **{framework}**: {risk_level.upper()} RISK")
        else:
            st.success(f"✅ **{framework}**: {risk_level.upper()} RISK")

        st.markdown(f"**Explanation:** {explanation}")

        if key_factors:
            st.markdown("**Key Factors:**")
            for factor in key_factors:
                st.markdown(f"  - {factor}")

        if is_flagged:
            obligations = rc.get("regulatory_obligations", [])
            if obligations:
                st.markdown("**Regulatory Obligations:**")
                for obligation in obligations:
                    st.markdown(f"  - ⚡ {obligation}")

        st.markdown("---")


def _render_compliance_obligations(obligations: list[dict]):
    """Render compliance obligations organized by category tabs."""
    st.subheader("📋 Compliance Obligations")

    if not obligations:
        st.info("No compliance obligations generated.")
        return

    # Group by category
    categories: dict[str, list[dict]] = {}
    for ob in obligations:
        cat = ob.get("category", "other")
        display_cat = cat.replace("_", " ").title()
        if display_cat not in categories:
            categories[display_cat] = []
        categories[display_cat].append(ob)

    # Create tabs for each category
    if categories:
        tabs = st.tabs(list(categories.keys()))
        for tab, (cat_name, cat_obligations) in zip(tabs, categories.items()):
            with tab:
                for ob in cat_obligations:
                    priority = ob.get("priority", "medium")
                    priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                        priority, "⚪"
                    )

                    st.markdown(f"{priority_icon} **{ob.get('obligation', '')}**")
                    st.caption(f"Reference: {ob.get('framework_reference', 'N/A')}")

                    actions = ob.get("recommended_actions", [])
                    if actions:
                        st.markdown("**Recommended Actions:**")
                        for action in actions:
                            st.markdown(f"  - {action}")

                    docs = ob.get("documentation_requirements", [])
                    if docs:
                        st.markdown("**Documentation Requirements:**")
                        for doc in docs:
                            st.markdown(f"  - 📄 {doc}")

                    timeline = ob.get("timeline")
                    if timeline:
                        st.markdown(f"**Timeline:** {timeline}")

                    st.markdown("---")


def _render_framework_comparison(comparison: dict | None):
    """Render framework comparison when multiple frameworks are selected."""
    st.subheader("🔄 Framework Comparison")

    if not comparison:
        st.info("Framework comparison is available when multiple frameworks are selected.")
        return

    overlapping = comparison.get("overlapping_requirements", [])
    conflicting = comparison.get("conflicting_requirements", [])
    harmonized = comparison.get("harmonized_approach", "")

    if overlapping:
        st.markdown("**Overlapping Requirements:**")
        for req in overlapping:
            st.markdown(f"  - ✓ {req}")

    if conflicting:
        st.markdown("**Conflicting Requirements:**")
        for conflict in conflicting:
            if isinstance(conflict, dict):
                st.markdown(f"  - ⚡ {conflict.get('description', str(conflict))}")
            else:
                st.markdown(f"  - ⚡ {conflict}")

    if harmonized:
        st.markdown("**Harmonized Approach:**")
        st.markdown(harmonized)


def _render_technology_recommendations(recommendations: list[dict]):
    """Render technology recommendations in categorized sections."""
    st.subheader("💻 Technology Recommendations")

    if not recommendations:
        st.info("No technology recommendations generated.")
        return

    # Group by category
    categories: dict[str, list[dict]] = {}
    for rec in recommendations:
        cat = rec.get("category", "other")
        display_cat = cat.replace("_", " ").title()
        if display_cat not in categories:
            categories[display_cat] = []
        categories[display_cat].append(rec)

    for cat_name, cat_recs in categories.items():
        st.markdown(f"### {cat_name}")

        for rec in cat_recs:
            with st.expander(f"**{rec.get('name', 'Unknown')}** - {rec.get('provider', '')}"):
                st.markdown(rec.get("description", ""))

                capabilities = rec.get("key_capabilities", [])
                if capabilities:
                    st.markdown("**Key Capabilities:**")
                    for cap in capabilities:
                        st.markdown(f"  - {cap}")

                col1, col2 = st.columns(2)
                with col1:
                    pros = rec.get("pros", [])
                    if pros:
                        st.markdown("**✅ Pros:**")
                        for pro in pros:
                            st.markdown(f"  - {pro}")

                with col2:
                    cons = rec.get("cons", [])
                    if cons:
                        st.markdown("**❌ Cons:**")
                        for con in cons:
                            st.markdown(f"  - {con}")

                # LLM-specific details
                context_window = rec.get("context_window")
                cost_per_token = rec.get("cost_per_token")
                if context_window:
                    st.caption(f"Context Window: {context_window:,} tokens")
                if cost_per_token:
                    st.caption(f"Cost: {cost_per_token}")

                compliance_notes = rec.get("compliance_notes", "")
                if compliance_notes:
                    st.info(f"📋 {compliance_notes}")


def render():
    """Render the Results display page."""
    st.header("📊 Results")
    st.markdown("View your AI governance compliance analysis results.")
    st.markdown("---")

    # Check prerequisites
    if not st.session_state.project_profile:
        st.warning("⚠️ Please complete the **Project Input** step first.")
        return

    if not st.session_state.selected_frameworks:
        st.warning("⚠️ Please select at least one framework in **Framework Selection**.")
        return

    # Detail level selector
    detail_options = {
        "Executive Summary": "executive_summary",
        "Standard": "standard",
        "Detailed": "detailed",
    }
    col1, col2 = st.columns([2, 1])
    with col1:
        detail_display = st.selectbox(
            "Detail Level",
            options=list(detail_options.keys()),
            index=list(detail_options.values()).index(st.session_state.detail_level),
            help="Control the level of detail in the generated advice",
        )
        st.session_state.detail_level = detail_options[detail_display]

    with col2:
        generate_btn = st.button("🔄 Generate Advice", use_container_width=True)

    st.markdown("---")

    # Generate advice
    if generate_btn:
        with st.spinner("Generating compliance advice... This may take up to 30 seconds."):
            result = _generate_advice_direct(
                project_profile=st.session_state.project_profile,
                selected_frameworks=st.session_state.selected_frameworks,
                detail_level=st.session_state.detail_level,
            )
            if result:
                st.session_state.advice_result = result
                st.success("✅ Advice generated successfully!")

    # Display results
    advice = st.session_state.advice_result
    if not advice:
        st.info("ℹ️ Click **Generate Advice** to run the analysis.")
        return

    # Risk Classifications
    risk_classifications = advice.get("risk_classifications", [])
    if risk_classifications:
        _render_risk_classifications(risk_classifications)

    # Compliance Obligations
    obligations = advice.get("obligations", [])
    if obligations:
        _render_compliance_obligations(obligations)

    # Framework Comparison (only for multiple frameworks)
    if len(st.session_state.selected_frameworks) > 1:
        comparison = advice.get("framework_comparison")
        _render_framework_comparison(comparison)

    # Industry Guidance
    industry_guidance = advice.get("industry_guidance", "")
    if industry_guidance:
        st.subheader("🏭 Industry Guidance")
        st.markdown(industry_guidance)

    # Technology Recommendations
    tech_recs = advice.get("technology_recommendations", [])
    if tech_recs:
        _render_technology_recommendations(tech_recs)

    # Disclaimer
    st.markdown("---")
    disclaimer = advice.get(
        "disclaimer",
        "This advice is informational and does not constitute legal counsel.",
    )
    st.caption(f"⚖️ **Disclaimer:** {disclaimer}")
