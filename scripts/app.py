import plotly.express as px
import streamlit as st

from query import query

st.set_page_config(
    page_title="QBuild Maintenance Analytics",
    layout="wide",
)

st.title("QBuild Maintenance Analytics")

st.caption(
    "Analysis of Queensland Government QBuild maintenance work. " 
    "Sourced from Queensland Government Open Data. "
    "Written by [Juan Santhosh](https://github.com/juan-santhosh)."
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Operations",
        "Work Orders",
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

    st.subheader("Annual Maintenance Expenditure")

    fig = px.line(
        annual, x="billing_year", y="expenditure", markers=True,
        labels={
            "billing_year": "Billing Year",
            "expenditure": "Expenditure ($)"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

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
            work_types, x="wo_type", y="work_orders",
            labels={
                "wo_type": "Work Type",
                "work_orders": "Work Orders"
            }
        )

        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.bar(
            work_types, x="wo_type", y="expenditure",
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

    st.subheader("Maintenance by Local Authority")

    fig = px.bar(
        authority.head(15), x="expenditure", y="local_authority", orientation="h",
        labels={
            "expenditure": "Expenditure ($)",
            "local_authority": "Local Authority",
        },
    )

    st.plotly_chart(fig, width="stretch")
    st.dataframe(authority, width="stretch", hide_index=True)

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