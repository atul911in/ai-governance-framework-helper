"""Export page for the AI Governance Framework Helper."""

import streamlit as st

from src.export.markdown import generate_markdown


def _generate_markdown_preview(advice: dict) -> str:
    """Generate a local markdown preview of the advice content."""
    lines = []
    lines.append("# AI Governance Compliance Report\n")

    # Project summary
    profile = st.session_state.project_profile
    if profile:
        lines.append("## Project Summary\n")
        lines.append(f"- **Name:** {profile.get('name', 'N/A')}")
        lines.append(f"- **Industry:** {profile.get('industry_sector', 'N/A').replace('_', ' ').title()}")
        lines.append(f"- **Region:** {profile.get('deployment_region', 'N/A')}")
        lines.append(f"- **Purpose:** {profile.get('intended_purpose', 'N/A')}")
        lines.append("")

    # Frameworks
    frameworks = advice.get("frameworks", st.session_state.selected_frameworks)
    if frameworks:
        lines.append("## Selected Frameworks\n")
        for fw in frameworks:
            lines.append(f"- {fw}")
        lines.append("")

    # Risk Classifications
    risk_classifications = advice.get("risk_classifications", [])
    if risk_classifications:
        lines.append("## Risk Classifications\n")
        for rc in risk_classifications:
            level = rc.get("risk_level", "unknown").upper()
            framework = rc.get("framework", "Unknown")
            lines.append(f"### {framework}: {level} RISK\n")
            lines.append(f"{rc.get('explanation', '')}\n")
        lines.append("")

    # Obligations
    obligations = advice.get("obligations", [])
    if obligations:
        lines.append("## Compliance Obligations\n")
        for ob in obligations:
            lines.append(f"### {ob.get('obligation', '')}\n")
            lines.append(f"- **Category:** {ob.get('category', 'N/A').replace('_', ' ').title()}")
            lines.append(f"- **Priority:** {ob.get('priority', 'N/A')}")
            lines.append(f"- **Reference:** {ob.get('framework_reference', 'N/A')}")
            actions = ob.get("recommended_actions", [])
            if actions:
                lines.append("- **Actions:**")
                for action in actions:
                    lines.append(f"  - {action}")
            lines.append("")

    # Technology Recommendations
    tech_recs = advice.get("technology_recommendations", [])
    if tech_recs:
        lines.append("## Technology Recommendations\n")
        for rec in tech_recs:
            lines.append(f"### {rec.get('name', 'Unknown')} ({rec.get('provider', '')})\n")
            lines.append(f"{rec.get('description', '')}\n")
        lines.append("")

    # Disclaimer
    disclaimer = advice.get(
        "disclaimer",
        "This advice is informational and does not constitute legal counsel.",
    )
    lines.append("---\n")
    lines.append(f"*{disclaimer}*\n")

    return "\n".join(lines)


def render():
    """Render the Export page."""
    st.header("📥 Export")
    st.markdown("Download your compliance report in Markdown format.")
    st.markdown("---")

    # Check prerequisites
    if not st.session_state.advice_result:
        st.warning("⚠️ Please generate results first in the **Results** page.")
        return

    advice = st.session_state.advice_result
    profile = st.session_state.project_profile or {}

    # Export buttons
    st.subheader("Download Report")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📄 Markdown Format")
        st.caption("Full compliance report using the export module")
        if st.button("⬇️ Export as Markdown", use_container_width=True):
            with st.spinner("Generating Markdown..."):
                try:
                    md_content = generate_markdown(advice, profile)
                    st.download_button(
                        label="📥 Download Markdown",
                        data=md_content,
                        file_name="compliance_report.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"❌ Error generating markdown: {str(e)}")

    with col2:
        st.markdown("### 📄 PDF Format")
        st.caption("PDF export is not available on Streamlit Cloud. Download Markdown instead.")
        st.info("ℹ️ PDF generation requires WeasyPrint which is not supported on Streamlit Community Cloud. Use the Markdown export and convert locally if needed.")

    # Preview section
    st.markdown("---")
    st.subheader("📋 Report Preview")

    preview_content = _generate_markdown_preview(advice)
    st.markdown(preview_content)
