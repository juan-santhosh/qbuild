from pathlib import Path
import sqlite3
import pandas as pd

DB_PATH = Path("data/qbuild.db")
SCHEMA_PATH = Path("sql/views.sql")
DATA_PATH = Path("data/combined_data.csv")

df = pd.read_csv(DATA_PATH)

connection = sqlite3.connect(DB_PATH)

with open(SCHEMA_PATH) as f:
    connection.executescript(f.read())

df.to_sql(
    "work_orders", connection, if_exists="replace", index=False
)

connection.commit()
connection.close()