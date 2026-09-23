"""ShopSmart Sales Dashboard.

Run locally with:  streamlit run app.py
"""

from pathlib import Path

import plotly.express as px
import streamlit as st

import analytics

# Build the path from this file's folder, so the app works no matter
# which directory `streamlit run` is started from.
DATA_PATH = Path(__file__).parent / "data" / "sales-data.csv"

# One color for every chart, so the page looks consistent.
CHART_COLOR = "#2563EB"


@st.cache_data
def get_data():
    """Load the sales data once and reuse it on every page refresh."""
    return analytics.load_data(DATA_PATH)


def bar_chart(data, label_column, axis_title):
    """Horizontal bar chart of sales, with the largest bar at the top."""
    chart = px.bar(
        data,
        x="sales",
        y=label_column,
        orientation="h",
        labels={"sales": "Sales ($)", label_column: axis_title},
        color_discrete_sequence=[CHART_COLOR],
    )
    chart.update_traces(hovertemplate="%{y}: $%{x:,.2f}<extra></extra>")
    # Plotly draws the first row at the bottom; this puts the biggest at the top.
    chart.update_yaxes(categoryorder="total ascending")
    chart.update_xaxes(tickprefix="$", tickformat=",")
    return chart


st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

# --- Load data ---------------------------------------------------------------
try:
    df = get_data()
except (FileNotFoundError, ValueError) as error:
    st.error(f"Could not load sales data: {error}")
    st.stop()

if df.empty:
    st.warning("The sales data file has no rows yet, so there is nothing to show.")
    st.stop()

# --- KPI cards ---------------------------------------------------------------
sales_column, orders_column = st.columns(2)
sales_column.metric("Total Sales", f"${analytics.total_sales(df):,.0f}")
orders_column.metric("Total Orders", f"{analytics.total_orders(df):,}")

# --- Sales trend -------------------------------------------------------------
st.subheader("Sales Trend Over Time")
monthly = analytics.monthly_sales(df)
trend_chart = px.line(
    monthly,
    x="month",
    y="sales",
    markers=True,
    labels={"month": "Month", "sales": "Sales ($)"},
    color_discrete_sequence=[CHART_COLOR],
)
trend_chart.update_traces(hovertemplate="%{x|%b %Y}: $%{y:,.2f}<extra></extra>")
trend_chart.update_xaxes(tickformat="%b %Y", dtick="M1")
trend_chart.update_yaxes(tickprefix="$", tickformat=",")
st.plotly_chart(trend_chart)

# --- Category and region breakdowns ------------------------------------------
category_column, region_column = st.columns(2)

with category_column:
    st.subheader("Sales by Category")
    st.plotly_chart(bar_chart(analytics.sales_by_category(df), "category", "Category"))

with region_column:
    st.subheader("Sales by Region")
    st.plotly_chart(bar_chart(analytics.sales_by_region(df), "region", "Region"))
