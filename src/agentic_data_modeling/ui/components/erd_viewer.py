"""ERD viewer component."""

import streamlit as st


def render_erd(mermaid_code: str):
    st.subheader("Entity Relationship Diagram")
    st.code(mermaid_code, language="mermaid")
