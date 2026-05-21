"""Main Streamlit application entry point for the AI Governance Framework Helper."""

import os

import streamlit as st

# Load from Streamlit secrets if available (for Streamlit Cloud deployment)
if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
    os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

from src.ui.pages import export, framework_selection, project_input, results

# Page configuration
st.set_page_config(
    page_title="AI Governance Framework Helper",
    page_icon="🏛️",
    layout="wide",
)

# Define pages
PAGES = {
    "Project Input": project_input,
    "Framework Selection": framework_selection,
    "Results": results,
    "Export": export,
}


def init_session_state():
    """Initialize session state with default values."""
    defaults = {
        "current_page": "Project Input",
        "project_profile": None,
        "selected_frameworks": [],
        "detail_level": "standard",
        "advice_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main():
    """Main application entry point."""
    init_session_state()

    # Sidebar navigation
    st.sidebar.title("🏛️ AI Governance Helper")
    st.sidebar.markdown("---")

    selected_page = st.sidebar.radio(
        "Navigation",
        list(PAGES.keys()),
        index=list(PAGES.keys()).index(st.session_state.current_page),
    )
    st.session_state.current_page = selected_page

    # Display status indicators in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Progress")
    if st.session_state.project_profile:
        st.sidebar.success("✅ Project defined")
    else:
        st.sidebar.info("⬜ Project not defined")

    if st.session_state.selected_frameworks:
        st.sidebar.success(f"✅ {len(st.session_state.selected_frameworks)} framework(s) selected")
    else:
        st.sidebar.info("⬜ No frameworks selected")

    if st.session_state.advice_result:
        st.sidebar.success("✅ Results generated")
    else:
        st.sidebar.info("⬜ No results yet")

    # Render selected page
    PAGES[selected_page].render()


if __name__ == "__main__":
    main()
