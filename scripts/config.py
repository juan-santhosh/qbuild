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

AUTHORITY_RENAME_MAP = {
    "Cherbourg Aboriginal Sc": "Cherbourg Aboriginal Shire Cou",
    "Doomadgee Aboriginal Sc": "Doomadgee Aboriginal Shire Cou",
    "Hope Value Aboriginal Sc": "Doomadgee Aboriginal Shire Cnc",
    "Kowanyama Aboriginal Sc": "Kowanyama Aboriginal Shire Cou",
    "Lockhart River Aboriginal Sc": "Lockhart River Aboriginal Shir",
    "Mapoon Aboriginal Sc": "Mapoon Aboriginal Council",
    "Napranum Aboriginal Sc": "Napranum Aboriginal Shire Coun",
    "North Peninsula Area Rc": "Nthn Peninsula Area Reg Council",
    "Nthn Peninsula Area Reg Counci": "Nthn Peninsula Area Reg Council",
    "Palm Island Aboriginal Sc": "Palm Island Aboriginal Council",
    "Pormpuraaw Aboriginal Sc": "Pormpuraaw Aboriginal Shire Co",
    "Torres Strait Is Reg Council": "Torres Strait Island Reg Counc",
    "Woorabinda Aboriginal Sc": "Woorabinda Aboriginal Council",
    "Wujal Wujal Aboriginal Sc": "Wujal Wujal Aboriginal Council",
    "Yarrabah Aboriginal Sc": "Yarrabah Aboriginal Shire Coun",
}

CURRENCY_COLUMNS = ["ytd_value", "ltd_value"]

NAME_COLUMNS = [
    "electorate", "local_authority", 
    "equipment_classification", "wo_type", "type"
]

CANONICAL_COLUMNS = [
    "postcode", "electorate", "local_authority", 
    "equipment_classification", "wo_type", "type", 
    "ytd_value", "ltd_value", "billing_year",
]