"""Generate page; produce artifacts."""

import streamlit as st

st.header("3. Generate Artifacts")

if not st.session_state.get("model_json"):
    st.warning("No dimensional model available. Run the Modeler first.")
    st.stop()

st.info("Dimensional model ready for code generation.")

col1, col2, col3 = st.columns(3)

with col1:
    gen_dbt = st.button("Generate dbt Models")
with col2:
    gen_erd = st.button("Generate ERD")
with col3:
    gen_ddl = st.button("Generate DDL")

gen_all = st.button("Generate All Artifacts")

model_json = st.session_state.model_json

if gen_erd or gen_all:
    with st.spinner("Generating ERD..."):
        from agentic_data_modeling.tools.codegen_tools import render_mermaid_erd

        erd = render_mermaid_erd.invoke({"model_json": model_json})
        st.subheader("ERD Diagram")
        st.code(erd, language="mermaid")

if gen_ddl or gen_all:
    with st.spinner("Generating DDL..."):
        from agentic_data_modeling.tools.codegen_tools import render_ddl

        ddl = render_ddl.invoke({"model_json": model_json})
        st.subheader("DDL Statements")
        st.code(ddl, language="sql")

if gen_dbt or gen_all:
    with st.spinner("Running dbt generator agent..."):
        from agentic_data_modeling.agents.dbt_generator import dbt_generator_node

        result = dbt_generator_node(
            {
                "messages": [],
                "model_json": model_json,
                "output_dir": "/tmp/adm_output",
                "source_dir": "",
                "requirements": "",
                "next_agent": "",
                "profiles_json": "",
                "dbt_project_json": "",
                "quality_config_json": "",
                "artifacts": {},
                "completed_agents": [],
            }
        )
        st.session_state.dbt_project_json = result.get("dbt_project_json", "")
        st.subheader("dbt Output")
        st.code(result.get("dbt_project_json", ""), language="json")
