import plotly.express as px
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

    HEAD = 50

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