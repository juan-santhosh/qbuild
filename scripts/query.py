import sqlite3

import pandas as pd
import streamlit as st

DB_PATH = "data/qbuild.db"

@st.cache_data(ttl=3600)
def query(sql: str, params=None) -> pd.DataFrame:
    connection = sqlite3.connect(DB_PATH)

    try:
        return pd.read_sql_query(sql, connection, params=params)
    
    finally:
        connection.close()