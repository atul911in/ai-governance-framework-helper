"""Project Input form page for the AI Governance Framework Helper."""

import streamlit as st

# Predefined options for multi-selects
AI_TECHNIQUES = [
    "Machine Learning",
    "Deep Learning",
    "Natural Language Processing",
    "Computer Vision",
    "Reinforcement Learning",
    "Generative AI",
    "Robotics",
    "Expert Systems",
]

DATA_TYPES = [
    "Personal Data",
    "Biometric Data",
    "Health Data",
    "Financial Data",
    "Location Data",
    "Behavioral Data",
    "Text",
    "Images",
    "Audio",
    "Video",
]

DEPLOYMENT_REGIONS = [
    "European Union",
    "United Kingdom",
    "United States",
    "Canada",
    "Australia",
    "Singapore",
    "Global",
]

INDUSTRY_SECTORS = [
    "banking",
    "insurance",
    "health",
    "retail",
    "technology",
    "government",
    "education",
    "manufacturing",
    "telecommunications",
]


def _validate_form(
    name: str,
    description: str,
    ai_techniques: list[str],
    data_types: list[str],
    deployment_region: str,
    target_users: str,
    intended_purpose: str,
    industry_sector: str,
) -> list[str]:
    """Validate form inputs and return list of error messages."""
    errors = []

    if not name or not name.strip():
        errors.append("Project name is required.")
    elif len(name) > 200:
        errors.append("Project name must be 200 characters or fewer.")

    if not description or not description.strip():
        errors.append("Project description is required.")
    elif len(description) < 50:
        errors.append("Project description must be at least 50 characters.")
    elif len(description) > 5000:
        errors.append("Project description must be 5000 characters or fewer.")

    if not ai_techniques:
        errors.append("Select at least one AI technique.")

    if not data_types:
        errors.append("Select at least one data type.")

    if not deployment_region:
        errors.append("Deployment region is required.")

    if not target_users or not target_users.strip():
        errors.append("Target users is required.")

    if not intended_purpose or not intended_purpose.strip():
        errors.append("Intended purpose is required.")

    if not industry_sector:
        errors.append("Industry sector is required.")

    return errors


def render():
    """Render the Project Input form page."""
    st.header("📋 Project Input")
    st.markdown("Provide details about your AI project to receive tailored governance advice.")
    st.markdown("---")

    with st.form("project_input_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Project Name *",
                max_chars=200,
                value=st.session_state.get("_form_name", ""),
                help="Name of your AI project (1-200 characters)",
            )

            description = st.text_area(
                "Project Description *",
                height=150,
                max_chars=5000,
                value=st.session_state.get("_form_description", ""),
                help="Describe your AI project (50-5000 characters)",
            )
            # Character count display
            desc_len = len(description) if description else 0
            if desc_len < 50:
                st.caption(f"📝 {desc_len}/5000 characters (minimum 50 required)")
            else:
                st.caption(f"📝 {desc_len}/5000 characters")

            target_users = st.text_input(
                "Target Users *",
                value=st.session_state.get("_form_target_users", ""),
                help="Who will use this AI system?",
            )

            intended_purpose = st.text_input(
                "Intended Purpose *",
                value=st.session_state.get("_form_intended_purpose", ""),
                help="What is the primary purpose of this AI system?",
            )

        with col2:
            ai_techniques = st.multiselect(
                "AI Techniques *",
                options=AI_TECHNIQUES,
                default=st.session_state.get("_form_ai_techniques", []),
                help="Select all AI techniques used in your project",
            )

            data_types = st.multiselect(
                "Data Types *",
                options=DATA_TYPES,
                default=st.session_state.get("_form_data_types", []),
                help="Select all data types processed by your system",
            )

            deployment_region = st.selectbox(
                "Deployment Region *",
                options=[""] + DEPLOYMENT_REGIONS,
                index=0,
                help="Primary deployment region for your AI system",
            )

            industry_sector = st.selectbox(
                "Industry Sector *",
                options=[""] + [s.replace("_", " ").title() for s in INDUSTRY_SECTORS],
                index=0,
                help="Industry sector of your AI project",
            )

        st.markdown("---")
        submitted = st.form_submit_button("💾 Save Project Profile", use_container_width=True)

    if submitted:
        # Map display name back to enum value
        sector_value = ""
        if industry_sector:
            sector_value = industry_sector.lower().replace(" ", "_")

        errors = _validate_form(
            name=name,
            description=description,
            ai_techniques=ai_techniques,
            data_types=data_types,
            deployment_region=deployment_region,
            target_users=target_users,
            intended_purpose=intended_purpose,
            industry_sector=sector_value,
        )

        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Store project profile in session state
            st.session_state.project_profile = {
                "name": name.strip(),
                "description": description.strip(),
                "ai_techniques": ai_techniques,
                "data_types": data_types,
                "deployment_region": deployment_region,
                "target_users": target_users.strip(),
                "intended_purpose": intended_purpose.strip(),
                "industry_sector": sector_value,
            }
            # Persist form values
            st.session_state._form_name = name
            st.session_state._form_description = description
            st.session_state._form_ai_techniques = ai_techniques
            st.session_state._form_data_types = data_types
            st.session_state._form_target_users = target_users
            st.session_state._form_intended_purpose = intended_purpose

            st.success("✅ Project profile saved successfully!")
            st.info("Navigate to **Framework Selection** to choose governance frameworks.")

    # Show current profile if exists
    if st.session_state.project_profile and not submitted:
        st.markdown("---")
        st.subheader("Current Project Profile")
        profile = st.session_state.project_profile
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Name:** {profile['name']}")
            st.markdown(f"**Region:** {profile['deployment_region']}")
            st.markdown(f"**Industry:** {profile['industry_sector'].replace('_', ' ').title()}")
        with col2:
            st.markdown(f"**AI Techniques:** {', '.join(profile['ai_techniques'])}")
            st.markdown(f"**Data Types:** {', '.join(profile['data_types'])}")
