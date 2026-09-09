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
        "Insights",
        "Trends",
        "Operations",
        "Lookup",
    ],
)

df = query("SELECT * FROM work_orders")

annual = query("""
    SELECT
        billing_year,
        COUNT(*) AS work_orders,
        SUM(ytd_value) AS expenditure,
        AVG(ytd_value) AS average_order
    FROM work_orders
    GROUP BY billing_year
    ORDER BY billing_year
""")

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

work_types = query("""
    SELECT
        wo_type,
        COUNT(*) AS work_orders,
        SUM(ytd_value) AS expenditure,
        AVG(ytd_value) AS average_order
    FROM work_orders
    WHERE wo_type IS NOT NULL
    GROUP BY wo_type
    ORDER BY expenditure DESC
""")

if page == "Trends":
    st.subheader("Maintenance Trends")

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

elif page == "Insights":
    st.subheader("Operational Insights")

    st.caption(
        "Summary of maintenance activity, expenditure concentration, "
        "and unusual operational patterns."
    )

    costs = query("""
        SELECT ytd_value
        FROM work_orders
        WHERE ytd_value IS NOT NULL AND ytd_value > 0
    """)

    total_expenditure = costs["ytd_value"].sum()

    median_order = costs["ytd_value"].median()
    p90_order = costs["ytd_value"].quantile(0.90)
    p95_order = costs["ytd_value"].quantile(0.95)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Median Work Order",
        f"${median_order:,.0f}",
    )

    col2.metric(
        "90th Percentile",
        f"${p90_order:,.0f}",
    )

    col3.metric(
        "95th Percentile",
        f"${p95_order:,.0f}",
    )

    top_work_type = work_types.iloc[0]

    col4.metric(
        "Largest Work Type",
        top_work_type["wo_type"],
    )

    st.subheader("Year-over-Year Change")

    if len(annual) >= 2:
        latest = annual.iloc[-1]
        previous = annual.iloc[-2]

        expenditure_change = (
            (latest["expenditure"] - previous["expenditure"])
            / previous["expenditure"]
        )

        orders_change = (
            (latest["work_orders"] - previous["work_orders"])
            / previous["work_orders"]
        )

        average_change = (
            (latest["average_order"] - previous["average_order"])
            / previous["average_order"]
        )

        col1, col2, col3, _ = st.columns(4)

        col1.metric(
            "Expenditure",
            f"${latest['expenditure']:,.0f}",
            f"{expenditure_change:+.1%}",
        )

        col2.metric(
            "Work Orders",
            f"{latest['work_orders']:,}",
            f"{orders_change:+.1%}",
        )

        col3.metric(
            "Average Order",
            f"${latest['average_order']:,.0f}",
            f"{average_change:+.1%}",
        )

    st.subheader("Expenditure Concentration")

    work_types["share"] = (
        work_types["expenditure"]
        / work_types["expenditure"].sum()
    )

    work_types["cumulative_share"] = (
        work_types["share"].cumsum()
    )

    pareto = work_types.copy()

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=pareto["wo_type"], y=pareto["expenditure"], name="Expenditure",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Expenditure: $%{y:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=pareto["wo_type"], y=pareto["cumulative_share"] * 100,
            name="Cumulative share", mode="lines+markers", yaxis="y2",
            hovertemplate=(
                "Cumulative: %{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        height=550, xaxis_title="Work Type", yaxis_title="Expenditure ($)",
        yaxis2=dict(
            title="Cumulative Share (%)", overlaying="y",
            side="right", range=[0, 105],
        ),
        margin=dict(l=20, r=20, t=40, b=20),
    )

    st.plotly_chart(fig, width="stretch")

    st.subheader("Maintenance Hotspots")
    st.caption("Top 10 authorities by maintenance expenditure.")

    authority["expenditure_share"] = (
        authority["expenditure"]
        / authority["expenditure"].sum()
    )

    top_authorities = authority.sort_values(
        "expenditure", ascending=False,
    ).head(10)

    st.dataframe(
        top_authorities[[
            "local_authority",
            "work_orders",
            "expenditure",
            "average_order",
            "expenditure_share",
        ]].rename(
            columns={
                "local_authority": "Local Authority",
                "work_orders": "Work Orders",
                "expenditure": "Expenditure",
                "average_order": "Average Order",
                "expenditure_share": "Expenditure Share",
            }
        ).style.format({
            "Work Orders": "{:,}",
            "Expenditure": "${:,.0f}",
            "Average Order": "${:,.0f}",
            "Expenditure Share": "{:.1%}",
        }),
        width="stretch", hide_index=True,
    )

    st.subheader("High-Cost Authorities")

    cost_threshold = authority["average_order"].quantile(0.90)

    high_cost = authority[
        authority["average_order"] >= cost_threshold
    ].sort_values(
        "average_order",
        ascending=False,
    )

    st.caption(
        f"Authorities in the top 10% by average work-order value "
        f"(≥ ${cost_threshold:,.0f})."
    )

    st.dataframe(
        high_cost[
            [
                "local_authority",
                "work_orders",
                "average_order",
                "expenditure",
            ]
        ].rename(
            columns={
                "local_authority": "Local Authority",
                "work_orders": "Work Orders",
                "average_order": "Average Order",
                "expenditure": "Total Expenditure",
            }
        ).style.format(
            {
                "Work Orders": "{:,}",
                "Average Order": "${:,.0f}",
                "Total Expenditure": "${:,.0f}",
            }
        ),
        width="stretch",
        hide_index=True,
    )

    st.subheader("Work Order Cost Distribution")

    col1, col2 = st.columns([4, 1])

    with col1:
        fig = px.histogram(
            costs, x="ytd_value", nbins=50,
            labels={
                "ytd_value": "Work Order Value ($)",
            },
        )

        fig.update_layout(
            height=500, margin=dict(l=20, r=20, t=40, b=20),
        )

        st.plotly_chart(fig, width="stretch")

    with col2:
        st.metric(
            "Median",
            f"${median_order:,.0f}",
        )

        st.metric(
            "90th Percentile",
            f"${p90_order:,.0f}",
        )

        st.metric(
            "95th Percentile",
            f"${p95_order:,.0f}",
        )

        if median_order > 0:
            skew_ratio = (
                costs["ytd_value"].mean()
                / median_order
            )

            st.metric(
                "Mean / Median",
                f"{skew_ratio:.2f}×",
            )

    st.subheader("Key Observations")

    if len(annual) >= 2:
        latest = annual.iloc[-1]
        previous = annual.iloc[-2]

        expenditure_change = (
            latest["expenditure"] - previous["expenditure"]
        ) / previous["expenditure"]

        if expenditure_change > 0:
            st.info(
                "Maintenance expenditure increased by "
                f"{expenditure_change:.1%} between "
                f"{int(previous['billing_year'])} and "
                f"{int(latest['billing_year'])}."
            )
        else:
            st.info(
                "Maintenance expenditure decreased by "
                f"{abs(expenditure_change):.1%} between "
                f"{int(previous['billing_year'])} and "
                f"{int(latest['billing_year'])}."
            )

    st.info(
        f"{top_work_type['wo_type']} is the largest expenditure "
        "category, accounting for "
        f"{top_work_type['expenditure'] / total_expenditure:.1%} "
        "of total expenditure."
    )

    top_authority = authority.sort_values("expenditure", ascending=False).iloc[0]

    st.info(
        f"{top_authority['local_authority']} has the highest total "
        "maintenance expenditure at "
        f"${top_authority['expenditure']:,.0f}, across "
        f"{top_authority['work_orders']:,} work orders."
    )

    if skew_ratio > 1.5:
        st.info(
            f"The average work-order value is {skew_ratio:.1f}× "
            "the median, suggesting that expenditure is "
            "concentrated among a smaller number of higher-cost jobs."
        )

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