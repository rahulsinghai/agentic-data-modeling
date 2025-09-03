"""Streamlit app entry point."""

import streamlit as st

st.set_page_config(
    page_title="Agentic Data Modeling",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Agentic Data Modeling")
st.markdown(
    """
    AI-powered dimensional data modeling pipeline. Upload source data,
    describe your requirements, and let AI agents design your star schema,
    generate dbt models, ERDs, DDL, and data quality rules.

    **Navigate using the sidebar pages:**
    1. **Profile** — Upload and profile source data
    2. **Model** — Design dimensional model from requirements
    3. **Generate** — Produce dbt models, ERD, DDL, quality rules
    4. **Explore** — Run interactive SQL queries on your data
    """
)

# Initialize session state
if "profiles_json" not in st.session_state:
    st.session_state.profiles_json = ""
if "model_json" not in st.session_state:
    st.session_state.model_json = ""
if "dbt_project_json" not in st.session_state:
    st.session_state.dbt_project_json = ""
if "source_dir" not in st.session_state:
    st.session_state.source_dir = ""
