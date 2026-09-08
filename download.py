import os

import pandas as pd
from ckanapi import RemoteCKAN
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_TOKEN")
remote = RemoteCKAN("https://www.data.qld.gov.au/", apikey=API_KEY)

OUTPUT_DIR = "data/"

RESOURCE_IDS = {
    2026: "126ed6f0-c3e1-4c97-b8a2-6be14032033d",
    2025: "c0857064-43f0-43db-940e-bd951ce2c3e2",
    2024: "b98f87db-b65b-4769-a557-96a8c4a624ba",
    2023: "1243c65b-6e0a-46d0-a834-5c39193c5c75",
    2022: "67def1a7-434e-41d1-b213-349bf8c49cf5"
}

COLUMN_RENAME_MAP = {
    "Postcode": "postcode",
    "POST_CODE": "postcode",
    "ELECTORATE": "electorate",
    "LOCAL_AUTHORITY": "local_authority",
    "EQUIPMENT_CLASSIFCATION": "equipment_classification", # source typo
    "WO_TYPE": "wo_type",
    "Total_YTD": "ytd_value",
    "YTD_BILLED": "ytd_value",
    "Total_LTD": "ltd_value",
    "BILLING_YEAR": "billing_year",
    "TYPE": "type",
}

CURRENCY_COLUMNS = ["ytd_value", "ltd_value"]

CANONICAL_COLUMNS = [
    "postcode", "electorate", "local_authority", 
    "equipment_classification", "wo_type", "type", 
    "ytd_value", "ltd_value", "billing_year",
]

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
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r"[\$,]", "", regex=True),
                errors="coerce",
            )

    for col in CANONICAL_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

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