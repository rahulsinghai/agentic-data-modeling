"""Sidebar component."""

import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.title("ADM Pipeline")
        st.markdown("---")

        st.markdown("**Pipeline Status:**")
        profiled = bool(st.session_state.get("profiles_json"))
        modeled = bool(st.session_state.get("model_json"))
        generated = bool(st.session_state.get("dbt_project_json"))

        st.checkbox("Profiled", value=profiled, disabled=True)
        st.checkbox("Modeled", value=modeled, disabled=True)
        st.checkbox("Generated", value=generated, disabled=True)

        st.markdown("---")
        st.markdown("Built with LangGraph + Claude")
