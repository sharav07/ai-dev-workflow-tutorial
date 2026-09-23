"""Tests for analytics.py.

Most tests use tiny hand-built data, so you can check the expected answer
by eye. The "real CSV" tests check the numbers the PRD expects.
"""

from pathlib import Path

import pandas as pd
import pytest

import analytics

DATA_PATH = Path(__file__).parent.parent / "data" / "sales-data.csv"

HEADER = "date,order_id,product,category,region,quantity,unit_price,total_amount\n"


def write_csv(tmp_path, text):
    """Write text to a temporary CSV file and return its path."""
    path = tmp_path / "sales.csv"
    path.write_text(text)
    return path


@pytest.fixture(scope="module")
def real_df():
    """The real sales data, loaded once for all real-CSV tests."""
    return analytics.load_data(DATA_PATH)


@pytest.fixture
def sample_df():
    """Four rows, small enough to check every answer by hand.

    ORD-3 appears twice: one order that contains two different products.

        date        order_id  category     region  total_amount
        2024-01-05  ORD-1     Audio        North   100.00
        2024-01-20  ORD-2     Electronics  South   250.00
        2024-03-02  ORD-3     Electronics  North    50.00
        2024-03-15  ORD-3     Audio        East     25.00
    """
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-05", "2024-01-20", "2024-03-02", "2024-03-15"]),
            "order_id": ["ORD-1", "ORD-2", "ORD-3", "ORD-3"],
            "category": ["Audio", "Electronics", "Electronics", "Audio"],
            "region": ["North", "South", "North", "East"],
            "total_amount": [100.00, 250.00, 50.00, 25.00],
        }
    )


# --- load_data -------------------------------------------------------------


def test_load_data_parses_dates(tmp_path):
    path = write_csv(
        tmp_path,
        HEADER + "2024-01-15,ORD-1,Headphones,Audio,North,2,49.99,99.98\n",
    )
    df = analytics.load_data(path)
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert df["date"].iloc[0] == pd.Timestamp("2024-01-15")


def test_load_data_reads_numbers_as_numbers(tmp_path):
    path = write_csv(
        tmp_path,
        HEADER + "2024-01-15,ORD-1,Headphones,Audio,North,2,49.99,99.98\n",
    )
    df = analytics.load_data(path)
    for column in ["quantity", "unit_price", "total_amount"]:
        assert pd.api.types.is_numeric_dtype(df[column]), column
    assert df["total_amount"].iloc[0] == pytest.approx(99.98)


def test_load_data_rejects_missing_column(tmp_path):
    path = write_csv(
        tmp_path,
        "date,order_id,product,category,quantity,unit_price,total_amount\n"
        "2024-01-15,ORD-1,Headphones,Audio,2,49.99,99.98\n",
    )
    with pytest.raises(ValueError, match="region"):
        analytics.load_data(path)


def test_load_data_rejects_bad_date(tmp_path):
    path = write_csv(
        tmp_path,
        HEADER + "2024-13-45,ORD-1,Headphones,Audio,North,2,49.99,99.98\n",
    )
    with pytest.raises(ValueError, match="date"):
        analytics.load_data(path)


def test_load_data_rejects_non_numeric_amount(tmp_path):
    path = write_csv(
        tmp_path,
        HEADER + "2024-01-15,ORD-1,Headphones,Audio,North,2,49.99,abc\n",
    )
    with pytest.raises(ValueError, match="total_amount"):
        analytics.load_data(path)


def test_load_data_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        analytics.load_data(tmp_path / "does-not-exist.csv")


def test_real_csv_has_expected_shape(real_df):
    assert len(real_df) == 482
    assert real_df["category"].nunique() == 5
    assert real_df["region"].nunique() == 4


# --- KPIs ------------------------------------------------------------------


def test_total_sales_sums_amounts(sample_df):
    # 100 + 250 + 50 + 25
    assert analytics.total_sales(sample_df) == pytest.approx(425.00)


def test_total_orders_counts_each_order_once(sample_df):
    # ORD-1, ORD-2, ORD-3 (ORD-3 has two rows but is one order)
    assert analytics.total_orders(sample_df) == 3


def test_totals_are_zero_for_empty_data(tmp_path):
    df = analytics.load_data(write_csv(tmp_path, HEADER))
    assert analytics.total_sales(df) == 0.0
    assert analytics.total_orders(df) == 0


def test_real_csv_totals_match_prd(real_df):
    assert analytics.total_orders(real_df) == 482
    assert analytics.total_sales(real_df) == pytest.approx(116500.21, abs=0.005)


# --- Monthly trend ---------------------------------------------------------


def test_monthly_sales_groups_by_month(sample_df):
    monthly = analytics.monthly_sales(sample_df)
    assert list(monthly.columns) == ["month", "sales"]
    # January: 100 + 250
    assert monthly["month"].iloc[0] == pd.Timestamp("2024-01-01")
    assert monthly["sales"].iloc[0] == pytest.approx(350.00)


def test_monthly_sales_fills_missing_months_with_zero(sample_df):
    # sample_df has orders in January and March, none in February.
    monthly = analytics.monthly_sales(sample_df)
    assert list(monthly["month"]) == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-02-01"),
        pd.Timestamp("2024-03-01"),
    ]
    assert list(monthly["sales"]) == pytest.approx([350.00, 0.00, 75.00])


def test_real_csv_has_twelve_months(real_df):
    monthly = analytics.monthly_sales(real_df)
    assert len(monthly) == 12
    assert monthly["sales"].sum() == pytest.approx(116500.21, abs=0.005)


# --- Category and region breakdowns ----------------------------------------


def test_sales_by_category_sums_and_sorts(sample_df):
    by_category = analytics.sales_by_category(sample_df)
    assert list(by_category.columns) == ["category", "sales"]
    # Electronics: 250 + 50 = 300; Audio: 100 + 25 = 125
    assert list(by_category["category"]) == ["Electronics", "Audio"]
    assert list(by_category["sales"]) == pytest.approx([300.00, 125.00])


def test_sales_by_region_sums_and_sorts(sample_df):
    by_region = analytics.sales_by_region(sample_df)
    assert list(by_region.columns) == ["region", "sales"]
    # South: 250; North: 100 + 50 = 150; East: 25
    assert list(by_region["region"]) == ["South", "North", "East"]
    assert list(by_region["sales"]) == pytest.approx([250.00, 150.00, 25.00])


def test_real_csv_top_category_is_electronics(real_df):
    by_category = analytics.sales_by_category(real_df)
    assert len(by_category) == 5
    assert by_category["category"].iloc[0] == "Electronics"


def test_real_csv_has_all_four_regions(real_df):
    by_region = analytics.sales_by_region(real_df)
    assert set(by_region["region"]) == {"North", "South", "East", "West"}
