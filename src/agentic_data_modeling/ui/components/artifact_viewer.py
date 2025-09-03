"""Artifact viewer component."""

import streamlit as st


def render_artifact(title: str, content: str, language: str = "text"):
    st.subheader(title)
    st.code(content, language=language)
    st.download_button(
        label=f"Download {title}",
        data=content,
        file_name=f"{title.lower().replace(' ', '_')}.txt",
    )
