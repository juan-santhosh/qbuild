import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from query import query

st.set_page_config(
    page_title="QBuild Maintenance Analytics",
    layout="wide",
)

st.title("QBuild Maintenance Analytics")

st.caption(
    "Analysis of Queensland Government QBuild maintenance activity and expenditure. " 
    "Sourced from Queensland Government Open Data. "
    "Written by [Juan Santhosh](https://github.com/juan-santhosh)."
)

st.markdown("""
<style>
    section[data-testid="stSidebar"] .stRadio > div {
        gap: 0.15rem;
    }

    section[data-testid="stSidebar"] .stRadio label {
        padding: 0.2rem 0.4rem;
        font-size: 0.9rem;
    }

    div[data-testid="stCaptionContainer"] p {
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("# Navigation")

page = st.sidebar.radio(
    "",
    [
        "Overview",
        "Operations",
        "Insights",
        "Lookup",
    ],
)

df = query("SELECT * FROM work_orders")

if page == "Overview":
    st.subheader("Overview")

    total_orders = len(df)
    total_expenditure = df["ytd_value"].sum()
    average_order = df["ytd_value"].mean()
    authorities = df["local_authority"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Work Orders",
        f"{total_orders:,}"
    )

    col2.metric(
        "Total Expenditure",
        f"${total_expenditure:,.0f}"
    )

    col3.metric(
        "Average Work Order",
        f"${average_order:,.0f}"
    )

    col4.metric(
        "Local Authorities",
        f"{authorities:,}"
    )

    annual = query("""
        SELECT
            billing_year,
            COUNT(*) AS work_orders,
            SUM(ytd_value) AS expenditure
        FROM work_orders
        GROUP BY billing_year
        ORDER BY billing_year
    """)

    st.subheader("Annual Maintenance Expenditure Over Time")
    
    latest_year = annual["billing_year"].max()
    previous_year = latest_year - 1

    latest = annual[
        annual["billing_year"] == latest_year
    ]["expenditure"].iloc[0]

    previous = annual[
        annual["billing_year"] == previous_year
    ]["expenditure"].iloc[0]

    yoy_change = (latest - previous) / previous

    if len(annual) >= 2:
        x = annual["billing_year"].to_numpy(dtype=float)
        y = annual["expenditure"].to_numpy(dtype=float)

        slope, intercept = np.polyfit(x, y, 1)

        annual["trend"] = slope * x + intercept

        next_year = int(x.max() + 1)
        forecast = slope * next_year + intercept

        forecast_x = np.array([x.max(), next_year])

        forecast_y = np.array([
            slope * x.max() + intercept, forecast
        ])

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=annual["billing_year"], y=annual["expenditure"],
                mode="lines+markers", name="Actual",
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Expenditure: $%{y:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=annual["billing_year"], y=annual["trend"],
                mode="lines", name="Linear trend",
                line=dict(dash="dot"),
                hovertemplate=(
                    "Trend: $%{y:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=forecast_x, y=forecast_y,
                mode="lines+markers", name="Forecast",
                line=dict(dash="dash"),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Forecast: $%{y:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

        fig.update_layout(
            height=550,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title="Billing Year",
            yaxis_title="Expenditure ($)",
            legend_title="",
        )

        st.info(
            f"Maintenance expenditure changed by "
            f"{yoy_change:+.1%} from {previous_year} to {latest_year} "
            f"with a forecasted expenditure of ${forecast:,.0f} for {next_year}."
        )

        st.plotly_chart(fig, width="stretch")

    annual_type = query("""
        SELECT
            billing_year,
            wo_type,
            SUM(ytd_value) AS expenditure
        FROM work_orders
        WHERE wo_type IS NOT NULL
        AND ytd_value IS NOT NULL
        GROUP BY billing_year, wo_type
        ORDER BY billing_year
    """)

    st.subheader("Annual Maintenance Expenditure by Work Type")

    st.info(
        "All work types have increased in expenditure over time except for "
        "Facilities Management which is largely consistent."
    )

    fig = px.area(
        annual_type, x="billing_year", y="expenditure", color="wo_type",
        labels={
            "billing_year": "Billing Year",
            "expenditure": "Expenditure ($)",
            "wo_type": "Work Type",
        },
    )

    fig.update_layout(height=500)
    st.plotly_chart(fig, width="stretch")

elif page == "Operations":
    st.subheader("Maintenance Operations")

    work_types = query("""
        SELECT
            wo_type,
            COUNT(*) AS work_orders,
            SUM(ytd_value) AS expenditure
        FROM work_orders
        WHERE wo_type IS NOT NULL
        GROUP BY wo_type
        ORDER BY expenditure DESC
    """)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            work_types, x="wo_type", y="work_orders", color="wo_type",
            labels={
                "wo_type": "Work Type",
                "work_orders": "Work Orders"
            }
        )

        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.bar(
            work_types, x="wo_type", y="expenditure", color="wo_type",
            labels={
                "wo_type": "Work Type",
                "expenditure": "Expenditure ($)"
            }
        )

        st.plotly_chart(fig, width="stretch")

    authority = query("""
        SELECT
            local_authority,
            COUNT(*) AS work_orders,
            SUM(ytd_value) AS expenditure,
            AVG(ytd_value) AS average_order
        FROM work_orders
        WHERE local_authority IS NOT NULL
        GROUP BY local_authority
        ORDER BY expenditure DESC
    """)

    HEAD = 30

    st.subheader(f"Top {HEAD} local authorities by total expenditure")

    authority_top = authority.head(HEAD).copy()
    other_expenditure = authority.iloc[HEAD:]["expenditure"].sum()

    if other_expenditure > 0:
        authority_top.loc[len(authority_top)] = {
            "local_authority": "Other",
            "work_orders": authority.iloc[HEAD:]["work_orders"].sum(),
            "expenditure": other_expenditure,
            "average_order": None,
        }

    fig = px.pie(
        authority_top, values="expenditure",
        names="local_authority", hole=0.4,
    )

    fig.update_layout(
        height=700, margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(font=dict(size=13)),
    )

    fig.update_traces(
        textposition="inside", textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Expenditure: $%{value:,.0f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
    )

    st.plotly_chart(fig, width="stretch")

    st.subheader("Log Scale Scatter Plot of Local Authorities by Work Orders and Average Order Value")

    median_orders = authority["work_orders"].median()
    median_cost = authority["average_order"].median()

    authority["category"] = "Low Volume / Low Cost"

    authority.loc[
        (authority["work_orders"] >= median_orders)
        & (authority["average_order"] >= median_cost),
        "category"
    ] = "High Volume / High Cost"

    authority.loc[
        (authority["work_orders"] >= median_orders)
        & (authority["average_order"] < median_cost),
        "category"
    ] = "High Volume / Low Cost"

    authority.loc[
        (authority["work_orders"] < median_orders)
        & (authority["average_order"] >= median_cost),
        "category"
    ] = "Low Volume / High Cost"

    fig = px.scatter(
        authority, x="work_orders", y="average_order",
        size="expenditure", color="category", hover_name="local_authority",
        hover_data={
            "work_orders": ":,",
            "average_order": ":$.0f",
            "expenditure": ":$.0f",
        },
        labels={
            "work_orders": "Log Number of Work Orders",
            "average_order": "Log Average Work Order Value",
            "expenditure": "Total Expenditure ($)",
            "category": "Category",
        },
    )

    fig.update_xaxes(type="log")
    fig.update_yaxes(type="log")

    st.plotly_chart(fig, width="stretch")

    display_authority = authority.copy()

    display_authority["expenditure"] = (
        display_authority["expenditure"].map(lambda x: f"${x:,.0f}")
    )

    display_authority["average_order"] = (
        display_authority["average_order"].map(lambda x: f"${x:,.0f}")
    )

    st.dataframe(display_authority, width="stretch", hide_index=True)

else:
    st.subheader("Work Order Lookup")

    search = st.text_input("Search local authority, electorate or work type")

    lookup = df.copy()

    if search:
        mask = (
            lookup["local_authority"].str.contains(
                search, case=False, na=False
            )
            | lookup["electorate"].str.contains(
                search, case=False, na=False
            )
            | lookup["wo_type"].str.contains(
                search, case=False, na=False
            )
        )

        lookup = lookup[mask]

    st.dataframe(lookup, width="stretch", hide_index=True)