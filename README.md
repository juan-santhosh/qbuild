# QBuild Maintenance Analytics

An interactive maintenance analytics dashboard built using publicly available Queensland Government QBuild work-register data.

The project takes raw government data, cleans and validates it, stores it in a SQLite database, and provides an interactive Streamlit dashboard for exploring maintenance activity and expenditure.

## Demo

[qbuild_demo.webm](https://github.com/user-attachments/assets/420d4c5a-d8e5-4d97-bd41-1e1a04f8e4e3)

## Features

* Automated extraction of QBuild work-register data.
* Data cleaning and standardisation using Python and pandas.
* SQLite database with indexed analytical data.
* SQL-based aggregation and reporting.
* Interactive Streamlit dashboard featuring:
    * Automatically generated operational insights.
    * Annual maintenance expenditure trends with linear forecast.
    * Expenditure analysis by work type and local authority.
    * Maintenance work-order lookup table.

## Tech Stack

* **Python:** data processing and application logic
* **Pandas:** data cleaning and analysis
* **SQLite:** relational data storage
* **Plotly:** interactive visualisations
* **Streamlit:** dashboard interface

## Setup

### 1. Prerequisites

Ensure you have Python 3.14+ installed. Clone this repository and navigate to the project folder.

### 2. Install dependencies
Create a virtual environment and install the required Python packages using the uv package manager:
```bash
uv init
uv venv --version 3.14
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. Data Pipeline
Run download.py to download necessary data and load.py to load the SQLite schema before hosting the app:
```bash
uv run scripts/download.py
uv run scripts/load.py
streamlit run scripts/app.py
```
