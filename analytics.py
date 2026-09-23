"""Data loading and sales calculations for the ShopSmart dashboard.

Every function here takes plain inputs (a file path or a DataFrame) and
returns plain outputs. Nothing in this module knows about Streamlit or
Plotly, which keeps it easy to test with pytest.
"""

import pandas as pd

# The columns the dashboard relies on, in the order they appear in the CSV.
EXPECTED_COLUMNS = [
    "date",
    "order_id",
    "product",
    "category",
    "region",
    "quantity",
    "unit_price",
    "total_amount",
]


def load_data(path):
    """Read the sales CSV and return it as a DataFrame.

    Raises ValueError with a readable message if a column is missing,
    a date is not in YYYY-MM-DD form, or total_amount is not a number.
    """
    df = pd.read_csv(path)

    missing = [column for column in EXPECTED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing columns: {', '.join(missing)}")

    try:
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    except ValueError as error:
        raise ValueError(f"Column 'date' has a value that is not a YYYY-MM-DD date ({error})") from error

    try:
        df["total_amount"] = pd.to_numeric(df["total_amount"])
    except ValueError as error:
        raise ValueError(f"Column 'total_amount' has a value that is not a number ({error})") from error

    return df


def total_sales(df):
    """Sum of all order amounts, in dollars."""
    return float(df["total_amount"].sum())


def total_orders(df):
    """Number of distinct orders (an order can span several rows)."""
    return int(df["order_id"].nunique())


def monthly_sales(df):
    """Total sales for each calendar month, oldest first.

    Months with no orders are included with sales of 0, so the trend
    line never silently skips a month.
    """
    # resample("MS") groups by "Month Start" and fills in any empty months.
    monthly = df.set_index("date").resample("MS")["total_amount"].sum().reset_index()
    return monthly.rename(columns={"date": "month", "total_amount": "sales"})


def _sales_by(df, column):
    """Total sales for each value in `column`, highest first."""
    totals = df.groupby(column, as_index=False)["total_amount"].sum()
    totals = totals.rename(columns={"total_amount": "sales"})
    return totals.sort_values("sales", ascending=False, ignore_index=True)


def sales_by_category(df):
    """Total sales for each product category, highest first."""
    return _sales_by(df, "category")


def sales_by_region(df):
    """Total sales for each region, highest first."""
    return _sales_by(df, "region")
