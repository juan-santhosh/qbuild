import os

import pandas as pd
from ckanapi import RemoteCKAN
from dotenv import load_dotenv

from config import (
    AUTHORITY_RENAME_MAP, CANONICAL_COLUMNS, COLUMN_RENAME_MAP, 
    CURRENCY_COLUMNS, NAME_COLUMNS, RESOURCE_IDS
)

load_dotenv()

API_KEY = os.getenv("API_TOKEN")
remote = RemoteCKAN("https://www.data.qld.gov.au/", apikey=API_KEY)

OUTPUT_DIR = "data/"

def clean_currencies(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(r"[\$,]", "", regex=True),
        errors="coerce",
    ).round(2)

def clean_name(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
            .str.replace("\u00A0", " ", regex=False)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
            .str.title()
    )

def apply_authority_mapping(df: pd.DataFrame) -> pd.Series:
    df = df.copy()

    for old, new in AUTHORITY_RENAME_MAP.items():
        df["local_authority"] = df["local_authority"].replace(old, new)

    return df["local_authority"]

def fetch_year(resource_id: str) -> pd.DataFrame:
    records = []

    result = remote.action.datastore_search(
        resource_id=resource_id, limit=10_000
    )

    records = result["records"]

    df = pd.DataFrame(records)
    df = df.drop(columns=[c for c in ("_id") if c in df.columns])
    df = df.rename(columns=COLUMN_RENAME_MAP)

    for col in CURRENCY_COLUMNS:
        if col in df.columns:
            df[col] = clean_currencies(df[col])

    for col in NAME_COLUMNS:
        if col in df.columns:
            df[col] = clean_name(df[col])

    for col in CANONICAL_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    df["local_authority"] = apply_authority_mapping(df)

    return df[CANONICAL_COLUMNS]

frames: list[pd.DataFrame] = []

for year, resource_id in RESOURCE_IDS.items():
    df = fetch_year(resource_id)
    print(f"{year}: {len(df)} rows")

    df.to_csv(os.path.join(OUTPUT_DIR, f"{year}_data.csv"), index=False)
    frames.append(df)

combined = pd.concat(frames, ignore_index=True, sort=False)
combined.to_csv(os.path.join(OUTPUT_DIR, "combined_data.csv"), index=False)

print(f"\nCombined: {len(combined)} rows across {len(RESOURCE_IDS)} years")