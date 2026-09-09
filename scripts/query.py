import sqlite3
import pandas as pd

DB_PATH = "data/qbuild.db"

def query(sql: str, params=None) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn, params=params)