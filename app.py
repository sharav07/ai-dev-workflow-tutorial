"""ShopSmart Sales Dashboard.

Run locally with:  streamlit run app.py
"""

from pathlib import Path

import streamlit as st

import analytics

# Build the path from this file's folder, so the app works no matter
# which directory `streamlit run` is started from.
DATA_PATH = Path(__file__).parent / "data" / "sales-data.csv"


@st.cache_data
def get_data():
    """Load the sales data once and reuse it on every page refresh."""
    return analytics.load_data(DATA_PATH)


st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

# --- Load data ---------------------------------------------------------------
try:
    df = get_data()
except (FileNotFoundError, ValueError) as error:
    st.error(f"Could not load sales data: {error}")
    st.stop()
