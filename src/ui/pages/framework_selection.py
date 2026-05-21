"""Framework Selection page for the AI Governance Framework Helper."""

from datetime import datetime, timezone

import streamlit as st

from src.knowledge_base.loader import get_all_frameworks


def _fetch_frameworks() -> list[dict]:
    """Load frameworks directly from the knowledge base."""
    try:
        return get_all_frameworks()
    except FileNotFoundError:
        st.warning("⚠️ Frameworks data directory not found. Using empty list.")
        return []
    except Exception as e:
        st.warning(f"⚠️ Could not load frameworks: {e}")
        return []


def _is_recently_updated(last_updated: str) -> bool:
    """Check if a framework was updated within the last 30 days."""
    if not last_updated:
        return False
    try:
        updated_date = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
        if updated_date.tzinfo is None:
            updated_date = updated_date.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - updated_date
        return delta.days <= 30
    except (ValueError, TypeError):
        return False


def render():
    """Render the Framework Selection page."""
    st.header("🌍 Framework Selection")
    st.markdown("Select one or more governance frameworks to analyze your project against.")
    st.markdown("---")

    if not st.session_state.project_profile:
        st.warning("⚠️ Please complete the **Project Input** step first.")
        return

    # Fetch frameworks
    frameworks = _fetch_frameworks()

    # Group frameworks by region
    regions: dict[str, list[dict]] = {}
    for fw in frameworks:
        region = fw.get("country_or_region", "Other")
        if region not in regions:
            regions[region] = []
        regions[region].append(fw)

    # Initialize selection state
    if "framework_checkboxes" not in st.session_state:
        st.session_state.framework_checkboxes = {
            fw["framework_id"]: fw["framework_id"] in st.session_state.selected_frameworks
            for fw in frameworks
        }

    st.markdown("### Available Frameworks")

    selected = []

    for region, region_frameworks in sorted(regions.items()):
        st.subheader(f"📍 {region}")

        for fw in region_frameworks:
            fw_id = fw["framework_id"]
            col1, col2 = st.columns([3, 1])

            with col1:
                checked = st.checkbox(
                    f"**{fw['display_name']}**",
                    key=f"fw_{fw_id}",
                    value=fw_id in st.session_state.selected_frameworks,
                )
                st.caption(fw.get("summary", ""))

                if checked:
                    selected.append(fw_id)

            with col2:
                last_updated = fw.get("last_updated", "")
                if last_updated:
                    st.caption(f"📅 Updated: {last_updated}")
                    if _is_recently_updated(last_updated):
                        st.caption("🆕 Recently updated")

                version = fw.get("version", "")
                if version:
                    st.caption(f"v{version}")

        st.markdown("---")

    # Save selection button
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("💾 Save Framework Selection", use_container_width=True):
            if not selected:
                st.error("❌ Please select at least one governance framework.")
            else:
                st.session_state.selected_frameworks = selected
                st.success(
                    f"✅ {len(selected)} framework(s) selected: "
                    f"{', '.join(selected)}"
                )
                st.info("Navigate to **Results** to generate compliance advice.")

    with col2:
        st.metric("Selected", len(selected))

    # Show warning if no selection
    if not selected:
        st.info("ℹ️ Select at least one framework to proceed with analysis.")
