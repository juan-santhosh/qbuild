import os

import pandas as pd
from ckanapi import RemoteCKAN
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_TOKEN")
remote = RemoteCKAN("https://www.data.qld.gov.au/", apikey=API_KEY)

OUTPUT_DIR = "data/"

resource_ids = {
    2026: "126ed6f0-c3e1-4c97-b8a2-6be14032033d",
    2025: "c0857064-43f0-43db-940e-bd951ce2c3e2",
    2024: "b98f87db-b65b-4769-a557-96a8c4a624ba",
    2023: "1243c65b-6e0a-46d0-a834-5c39193c5c75",
    2022: "67def1a7-434e-41d1-b213-349bf8c49cf5"
}

for year, resource_id in resource_ids.items():
    result = remote.action.datastore_search(
        resource_id=resource_id, limit=10_000
    )

    df = pd.DataFrame(result["records"])

    filepath = OUTPUT_DIR + f"{year}_data.csv"

    ytd = "Total_YTD" if "Total_YTD" in df.columns else "YTD_BILLED"
    df[ytd] = pd.to_numeric(df[ytd].str.replace(r"[\$,]", "", regex=True))

    if "Total_LTD" in df.columns: 
        df["Total_LTD"] = pd.to_numeric(
            df["Total_LTD"].str.replace(r"[\$,]", "", regex=True)
        )

    df.to_csv(filepath)

df = pd.concat([
    pd.read_csv(OUTPUT_DIR + f"{year}_data.csv") 
    for year in resource_ids.keys()
])

df.to_csv(OUTPUT_DIR + "combined_data.csv", index=False)