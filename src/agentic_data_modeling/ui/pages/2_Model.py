"""Model page; design dimensional model."""

import streamlit as st

st.header("2. Design Dimensional Model")

requirements = st.text_area(
    "Business Requirements",
    placeholder="Describe your analytics needs...",
    height=200,
)

if st.session_state.get("profiles_json"):
    st.info("Source profiles available from profiling step.")
else:
    st.warning("No profiles available. Run the Profiler first or provide requirements only.")

if st.button("Run Modeler Agent") and requirements:
    with st.spinner("Designing dimensional model..."):
        from agentic_data_modeling.agents.modeler import modeler_node

        result = modeler_node(
            {
                "messages": [],
                "source_dir": "",
                "output_dir": "/tmp/adm_output",
                "requirements": requirements,
                "next_agent": "",
                "profiles_json": st.session_state.get("profiles_json", ""),
                "model_json": "",
                "dbt_project_json": "",
                "quality_config_json": "",
                "artifacts": {},
                "completed_agents": [],
            }
        )
        st.session_state.model_json = result.get("model_json", "")
        st.success("Modeling complete!")

if st.session_state.get("model_json"):
    st.subheader("Dimensional Model")
    st.code(st.session_state.model_json, language="json")
