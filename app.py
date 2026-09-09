import plotly.express as px
import streamlit as st

from load import query

st.set_page_config(
    page_title="QBuild Maintenance Analytics",
    layout="wide",
)

st.title("QBuild Maintenance Analytics")
st.caption("Sourced from Queensland Government Open Data. Written by [Juan Santhosh](https://juansanthosh.com).")

summary = query("""
SELECT
    COUNT(*) AS work_orders,
    SUM(ytd_value) AS expenditure,
    AVG(ytd_value) AS average_order
FROM work_orders
""")

col1, col2 = st.columns(2)

col1.metric("Total Maintenance Requests", len(df))
col2.metric("Total Value", f"${df['ytd_value'].sum():,.2f}")

st.subheader("Raw Data")
st.dataframe(df, use_container_width=True)

