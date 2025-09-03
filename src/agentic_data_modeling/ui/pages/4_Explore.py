"""Explore page — interactive SQL queries."""

import streamlit as st

st.header("4. Explore Data")

st.markdown("Run SQL queries against your loaded data using DuckDB.")

query = st.text_area("SQL Query", value="SHOW TABLES;", height=100)

if st.button("Execute"):
    from agentic_data_modeling.tools.duckdb_tools import run_query

    result = run_query.invoke({"sql": query})
    st.code(result, language="text")
