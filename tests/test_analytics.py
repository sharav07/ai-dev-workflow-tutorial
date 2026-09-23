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
