from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

FILEPATH = Path("data/combined_data.csv")

st.set_page_config(page_title="QBuild Maintenance")

st.title("QBuild Maintenance Analytics")

if not FILEPATH.exists():
    st.error(f"'{FILEPATH}' not found. Run `uv run download.py` first.")
    st.stop()

df = pd.read_csv(FILEPATH)

col1, col2 = st.columns(2)

col1.metric("Total Maintenance Requests", len(df))
col2.metric("Total Value", f"${df['ytd_value'].sum():,.2f}")

st.subheader("Raw Data")
st.dataframe(df, use_container_width=True)

