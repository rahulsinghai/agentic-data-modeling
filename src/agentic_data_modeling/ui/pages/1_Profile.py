"""Profile page; upload and profile source data."""

import tempfile
from pathlib import Path

import streamlit as st

st.header("1. Profile Source Data")

uploaded_files = st.file_uploader(
    "Upload CSV/JSON files", type=["csv", "json"], accept_multiple_files=True
)

if uploaded_files:
    with tempfile.TemporaryDirectory() as tmp_dir:
        for f in uploaded_files:
            path = Path(tmp_dir) / f.name
            path.write_bytes(f.getvalue())
            st.success(f"Uploaded: {f.name}")

        st.session_state.source_dir = tmp_dir

        if st.button("Run Profiler Agent"):
            with st.spinner("Profiling data..."):
                from agentic_data_modeling.agents.profiler import profiler_node

                result = profiler_node(
                    {
                        "messages": [],
                        "source_dir": tmp_dir,
                        "output_dir": "/tmp/adm_output",
                        "requirements": "",
                        "next_agent": "",
                        "profiles_json": "",
                        "model_json": "",
                        "dbt_project_json": "",
                        "quality_config_json": "",
                        "artifacts": {},
                        "completed_agents": [],
                    }
                )
                st.session_state.profiles_json = result.get("profiles_json", "")
                st.success("Profiling complete!")

if st.session_state.get("profiles_json"):
    st.subheader("Profile Results")
    st.code(st.session_state.profiles_json, language="json")
