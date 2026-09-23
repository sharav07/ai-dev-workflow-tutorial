# ShopSmart Sales Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page Streamlit dashboard that shows ShopSmart's 2024 sales: two KPI cards, a monthly trend line, and sales by category and by region.

**Architecture:** `analytics.py` holds all loading and calculation logic as plain Pandas functions, with no Streamlit and no Plotly, and is built test-first with pytest. `app.py` is a thin Streamlit page that reads top to bottom in the same order as the page: load data, KPIs, trend chart, breakdown charts.

**Tech Stack:** Python 3.14 (local), Streamlit, Pandas, Plotly Express, pytest. Plain `venv/` + `requirements.txt`.

**Spec:** `docs/superpowers/specs/2026-09-22-sales-dashboard-design.md`

## Numbering: plan tasks vs. milestones

This plan's tasks are numbered **Plan Task 1, Plan Task 2, …**. Each one is labeled with the `TASKS.md` milestone it belongs to, for example **[Milestone TASK-3]**. The two sets of numbers happen to line up one-to-one here, but they are separate: "Plan Task" refers to this document, and "TASK-N" refers to the board.

| Plan Task | Milestone | What it delivers | Who executes |
|---|---|---|---|
| Plan Task 1 | TASK-1 | venv, pinned requirements, pytest config, app skeleton | Claude |
| Plan Task 2 | TASK-2 | `load_data` + validation; app loads data safely | Claude |
| Plan Task 3 | TASK-3 | `total_sales`, `total_orders`; KPI cards | Claude |
| Plan Task 4 | TASK-4 | `monthly_sales`; trend chart | Claude |
| Plan Task 5 | TASK-5 | `sales_by_category`, `sales_by_region`; bar charts | Claude |
| Plan Task 6 | TASK-6 | Full verification against the PRD | Claude + owner check |
| Plan Task 7 | TASK-7 | Merge, deploy, record URL | **Owner only (the plan stops before this)** |

## Global Constraints

- Work on the current branch `feature/sales-dashboard`. Do **not** create a git worktree.
- Use a plain Python virtual environment in `venv/` (`python3 -m venv venv`). No uv, no conda.
- Dependencies live in `requirements.txt` with **exact pins** (`==`) for `streamlit`, `pandas`, `plotly`, `pytest`, using the versions installed and tested locally.
- All calculations live in `analytics.py`. `analytics.py` must not import Streamlit or Plotly.
- Tests live in `tests/test_analytics.py` and run with `pytest` from the project root.
- Keep code simple and readable, with short docstrings and no clever tricks. The owner must be able to follow it.
- Page title: "ShopSmart Sales Dashboard". Total Sales is formatted `$116,500` (whole dollars). Total Orders is formatted `482`.
- Category and region charts are horizontal bars with the largest at the top. All charts use one color (`CHART_COLOR = "#2563EB"`).
- Out of scope (PRD Phase 2): filters, date ranges, export, auth, database, drill-down.
- Every milestone ends with a commit whose message starts with its ID (`TASK-N: …`) and moves that item on `TASKS.md` to **Done**, with its checkboxes ticked. Leave the `Commit:` line blank: the owner fills it in.
- Every commit ends with the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- The `venv` must be active for every `pytest`, `pip`, and `streamlit` command (`source venv/bin/activate`).

## Review Focus

Five inputs or conditions the spec implies but doesn't spell out, most likely first. Each one has a test or check in the task that owns the code:

1. **A month with no sales.** The trend line should show that month as $0, not silently skip it and join its neighbors. This is pinned in Plan Task 4 by `test_monthly_sales_fills_missing_months_with_zero`.
2. **A malformed date in the CSV** (for example `2024-13-45`). The app should show a clear "could not load" message, not crash later inside a chart. This is pinned in Plan Task 2 by `test_load_data_rejects_bad_date`.
3. **A non-numeric `total_amount`** (for example `abc`). As with bad dates, this should fail at load time with a clear message, not produce a wrong total. This is pinned in Plan Task 2 by `test_load_data_rejects_non_numeric_amount`.
4. **A CSV with headers but no rows.** Totals should be 0 without crashing, and the page should say there is no data instead of drawing empty charts. This is pinned in Plan Task 3 by `test_totals_are_zero_for_empty_data`, plus the empty-data warning in `app.py`.
5. **Running the app from a different directory** (`streamlit run /full/path/app.py`). The data file should still be found. `app.py` builds the path from `Path(__file__).parent`, and Plan Task 2 Step 8 checks this.

---

### Plan Task 1: Environment and app skeleton — [Milestone TASK-1]

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `app.py`
- Create: `analytics.py` (docstring only)
- Modify: `TASKS.md` (move TASK-1 to Done)

**Interfaces:**
- Consumes: nothing
- Produces: an active `venv/` with streamlit, pandas, plotly, and pytest installed; `pytest.ini` with `pythonpath = .` so tests can `import analytics`; an `analytics.py` module that later tasks add functions to

- [ ] **Step 1: Move TASK-1 to In Progress on the board**

In `TASKS.md`, cut the whole `### TASK-1: …` block (heading through its `Commit:` line) from `## To Do` and paste it under `## In Progress`. Don't commit yet.

- [ ] **Step 2: Create and activate the virtual environment**

Run from the project root:

```bash
python3 -m venv venv
source venv/bin/activate
python --version
```

Expected: `Python 3.14.x`. `venv/` is already listed in `.gitignore`, so it won't be committed.

- [ ] **Step 3: Install the four packages**

```bash
pip install --upgrade pip
pip install streamlit pandas plotly pytest
```

Expected: the install finishes without errors. If a package has no wheel for Python 3.14, stop and tell the owner. The fallback is to recreate the venv with `python3.13 -m venv venv`.

- [ ] **Step 4: Write exact pins to `requirements.txt`**

```bash
pip freeze | grep -iE '^(streamlit|pandas|plotly|pytest)==' > requirements.txt
cat requirements.txt
```

Expected: exactly four lines in the form `name==version`, for example `pandas==2.x.y`. Only direct dependencies are pinned. pip resolves their sub-dependencies at install time.

- [ ] **Step 5: Create `pytest.ini`**

```ini
[pytest]
pythonpath = .
testpaths = tests
```

- [ ] **Step 6: Create `analytics.py` with just a docstring**

```python
"""Data loading and sales calculations for the ShopSmart dashboard.

Every function here takes plain inputs (a file path or a DataFrame) and
returns plain outputs. Nothing in this module knows about Streamlit or
Plotly, which keeps it easy to test with pytest.
"""
```

- [ ] **Step 7: Create a minimal `app.py`**

```python
"""ShopSmart Sales Dashboard.

Run locally with:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")
```

- [ ] **Step 8: Check that the app runs**

Streamlit's `AppTest` runs `app.py` the way a browser visit would, without opening one, and lets us read back what the page shows:

```bash
python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py').run()
print('exceptions:', list(at.exception))
print('title:', at.title[0].value)
"
```

Expected:
```
exceptions: []
title: ShopSmart Sales Dashboard
```

The owner can also run `streamlit run app.py` and see the title in the browser.

- [ ] **Step 9: Move TASK-1 to Done and commit**

In `TASKS.md`, move the TASK-1 block from `## In Progress` to `## Done` and tick both of its checkboxes (`- [x]`). Leave `Commit:` blank.

```bash
git add requirements.txt pytest.ini analytics.py app.py TASKS.md
git commit -m "TASK-1: set up venv requirements and app skeleton" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Plan Task 2: Load and validate the sales data — [Milestone TASK-2]

**Files:**
- Modify: `analytics.py`
- Create: `tests/test_analytics.py`
- Modify: `app.py`
- Modify: `TASKS.md`

**Interfaces:**
- Consumes: `analytics.py` module from Plan Task 1
- Produces:
  - `analytics.EXPECTED_COLUMNS: list[str]`
  - `analytics.load_data(path) -> pandas.DataFrame`, where `date` is `datetime64` and `total_amount` is numeric. It raises `ValueError` (with a readable message) for missing columns, bad dates, or non-numeric amounts, and `FileNotFoundError` for a missing file.
  - In `tests/test_analytics.py`: `DATA_PATH` (path to the real CSV), a `write_csv(tmp_path, text)` helper, and a `real_df` fixture that later tasks reuse
  - In `app.py`: `DATA_PATH` and a cached `get_data()`. After the load block, a DataFrame `df` is available to later sections.

- [ ] **Step 1: Move TASK-2 to In Progress on the board**

In `TASKS.md`, move the `### TASK-2: …` block from `## To Do` to `## In Progress`.

- [ ] **Step 2: Write the failing tests**

Create `tests/test_analytics.py`:

```python
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
```

- [ ] **Step 3: Run the tests to confirm they fail**

Run: `pytest -v`
Expected: every test fails or errors with `AttributeError: module 'analytics' has no attribute 'load_data'`.

- [ ] **Step 4: Implement `load_data`**

Append to `analytics.py`:

```python
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
```

Put the `import pandas as pd` line directly under the module docstring, not in the middle of the file.

- [ ] **Step 5: Run the tests to confirm they pass**

Run: `pytest -v`
Expected: 6 passed.

- [ ] **Step 6: Load the data in `app.py`**

Replace the whole of `app.py` with:

```python
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
```

(`pd.errors.EmptyDataError`, raised for a completely empty file, is a subclass of `ValueError`, so the same `except` catches it.)

- [ ] **Step 7: Check the app loads the data, and shows a clear error when the file is missing**

First, the normal case:

```bash
python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py').run()
print('exceptions:', list(at.exception))
print('errors:', [e.value for e in at.error])
"
```

Expected: `exceptions: []` and `errors: []`.

Then temporarily hide the data file:

```bash
mv data/sales-data.csv data/sales-data.csv.bak
python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py').run()
print('exceptions:', list(at.exception))
print('errors:', [e.value for e in at.error])
"
mv data/sales-data.csv.bak data/sales-data.csv
ls data/
```

Expected: `exceptions: []`, and `errors:` holds one message starting `Could not load sales data: `. The final `ls` shows `sales-data.csv`. **Always restore the file**, even if the middle command fails.

- [ ] **Step 8: Check that the app finds the data from a different directory**

```bash
PROJECT_DIR="$(pwd)"
(cd /tmp && PYTHONPATH="$PROJECT_DIR" python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('$PROJECT_DIR/app.py').run()
print('exceptions:', list(at.exception))
print('errors:', [e.value for e in at.error])
")
```

Expected: `exceptions: []` and `errors: []`. (`PYTHONPATH` only stands in for what `streamlit run` does itself, which is making `import analytics` work. What's being checked is that `DATA_PATH` doesn't depend on the current directory.)

- [ ] **Step 9: Move TASK-2 to Done and commit**

In `TASKS.md`, move TASK-2 to `## Done` and tick its three checkboxes. Leave `Commit:` blank.

```bash
git add analytics.py tests/test_analytics.py app.py TASKS.md
git commit -m "TASK-2: load and validate sales data" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Plan Task 3: KPI cards — [Milestone TASK-3]

**Files:**
- Modify: `analytics.py`
- Modify: `tests/test_analytics.py`
- Modify: `app.py`
- Modify: `TASKS.md`

**Interfaces:**
- Consumes: `analytics.load_data`, `real_df` fixture, `write_csv` helper, `HEADER` constant, and `df` in `app.py` (from Plan Task 2)
- Produces:
  - `analytics.total_sales(df) -> float`
  - `analytics.total_orders(df) -> int`
  - `sample_df` fixture in `tests/test_analytics.py` (4 rows; later tasks reuse it)

- [ ] **Step 1: Move TASK-3 to In Progress on the board**

In `TASKS.md`, move the `### TASK-3: …` block from `## To Do` to `## In Progress`.

- [ ] **Step 2: Write the failing tests**

Add this fixture to `tests/test_analytics.py`, directly below the `real_df` fixture:

```python
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
```

Append these tests to the end of the file:

```python
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
```

- [ ] **Step 3: Run the tests to confirm they fail**

Run: `pytest -v`
Expected: the 4 new tests fail with `AttributeError: module 'analytics' has no attribute 'total_sales'` (or `total_orders`). The 6 earlier tests still pass.

- [ ] **Step 4: Implement the two KPI functions**

Append to `analytics.py`:

```python
def total_sales(df):
    """Sum of all order amounts, in dollars."""
    return float(df["total_amount"].sum())


def total_orders(df):
    """Number of distinct orders (an order can span several rows)."""
    return int(df["order_id"].nunique())
```

- [ ] **Step 5: Run the tests to confirm they pass**

Run: `pytest -v`
Expected: 10 passed.

- [ ] **Step 6: Add the empty-data check and KPI row to `app.py`**

Append to the end of `app.py`:

```python
if df.empty:
    st.warning("The sales data file has no rows yet, so there is nothing to show.")
    st.stop()

# --- KPI cards ---------------------------------------------------------------
sales_column, orders_column = st.columns(2)
sales_column.metric("Total Sales", f"${analytics.total_sales(df):,.0f}")
orders_column.metric("Total Orders", f"{analytics.total_orders(df):,}")
```

- [ ] **Step 7: Check the app**

```bash
python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py').run()
print('exceptions:', list(at.exception))
print('metrics:', [(m.label, m.value) for m in at.metric])
"
```

Expected:
```
exceptions: []
metrics: [('Total Sales', '$116,500'), ('Total Orders', '482')]
```

In a browser, the owner should see the same two cards.

- [ ] **Step 8: Move TASK-3 to Done and commit**

In `TASKS.md`, move TASK-3 to `## Done` and tick its two checkboxes. Leave `Commit:` blank.

```bash
git add analytics.py tests/test_analytics.py app.py TASKS.md
git commit -m "TASK-3: add total sales and total orders KPI cards" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Plan Task 4: Monthly sales trend chart — [Milestone TASK-4]

**Files:**
- Modify: `analytics.py`
- Modify: `tests/test_analytics.py`
- Modify: `app.py`
- Modify: `TASKS.md`

**Interfaces:**
- Consumes: `sample_df` and `real_df` fixtures; `df` in `app.py`
- Produces:
  - `analytics.monthly_sales(df) -> pandas.DataFrame` with columns `month` (Timestamp, first day of the month) and `sales` (float), one row per calendar month from the first to the last month in the data, oldest first. Months with no orders have `sales == 0`.
  - `CHART_COLOR` constant in `app.py`

- [ ] **Step 1: Move TASK-4 to In Progress on the board**

In `TASKS.md`, move the `### TASK-4: …` block from `## To Do` to `## In Progress`.

- [ ] **Step 2: Write the failing tests**

Append to `tests/test_analytics.py`:

```python
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
```

- [ ] **Step 3: Run the tests to confirm they fail**

Run: `pytest -v`
Expected: the 3 new tests fail with `AttributeError: module 'analytics' has no attribute 'monthly_sales'`. The other 10 pass.

- [ ] **Step 4: Implement `monthly_sales`**

Append to `analytics.py`:

```python
def monthly_sales(df):
    """Total sales for each calendar month, oldest first.

    Months with no orders are included with sales of 0, so the trend
    line never silently skips a month.
    """
    # resample("MS") groups by "Month Start" and fills in any empty months.
    monthly = df.set_index("date").resample("MS")["total_amount"].sum().reset_index()
    return monthly.rename(columns={"date": "month", "total_amount": "sales"})
```

- [ ] **Step 5: Run the tests to confirm they pass**

Run: `pytest -v`
Expected: 13 passed.

- [ ] **Step 6: Add the trend chart to `app.py`**

Add `import plotly.express as px` to the imports so they read:

```python
from pathlib import Path

import plotly.express as px
import streamlit as st

import analytics
```

Add this constant directly below `DATA_PATH`:

```python
# One color for every chart, so the page looks consistent.
CHART_COLOR = "#2563EB"
```

Append to the end of `app.py`:

```python
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
```

- [ ] **Step 7: Check the app**

```bash
python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py').run()
print('exceptions:', list(at.exception))
print('subheaders:', [s.value for s in at.subheader])
print('charts:', len(at.get('plotly_chart')))
"
```

Expected:
```
exceptions: []
subheaders: ['Sales Trend Over Time']
charts: 1
```

In a browser, the owner should see a line with 12 points from Jan 2024 to Dec 2024. Hovering over a point shows, for example, `Mar 2024: $9,812.40` (the format; the real value will differ).

- [ ] **Step 8: Move TASK-4 to Done and commit**

In `TASKS.md`, move TASK-4 to `## Done` and tick its two checkboxes. Leave `Commit:` blank.

```bash
git add analytics.py tests/test_analytics.py app.py TASKS.md
git commit -m "TASK-4: add monthly sales trend chart" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Plan Task 5: Category and region bar charts — [Milestone TASK-5]

**Files:**
- Modify: `analytics.py`
- Modify: `tests/test_analytics.py`
- Modify: `app.py`
- Modify: `TASKS.md`

**Interfaces:**
- Consumes: `sample_df` and `real_df` fixtures; `df`, `px`, and `CHART_COLOR` in `app.py`
- Produces:
  - `analytics.sales_by_category(df) -> pandas.DataFrame` with columns `category`, `sales`, sorted by `sales` descending, index 0..n-1
  - `analytics.sales_by_region(df) -> pandas.DataFrame` with columns `region`, `sales`, sorted by `sales` descending, index 0..n-1
  - `analytics._sales_by(df, column)`: private helper used by both
  - `bar_chart(data, label_column, axis_title)` helper in `app.py`

- [ ] **Step 1: Move TASK-5 to In Progress on the board**

In `TASKS.md`, move the `### TASK-5: …` block from `## To Do` to `## In Progress`.

- [ ] **Step 2: Write the failing tests**

Append to `tests/test_analytics.py`:

```python
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
```

- [ ] **Step 3: Run the tests to confirm they fail**

Run: `pytest -v`
Expected: the 4 new tests fail with `AttributeError: module 'analytics' has no attribute 'sales_by_category'` (or `sales_by_region`). The other 13 pass.

- [ ] **Step 4: Implement the breakdown functions**

Append to `analytics.py`:

```python
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
```

- [ ] **Step 5: Run the tests to confirm they pass**

Run: `pytest -v`
Expected: 17 passed.

- [ ] **Step 6: Add the two bar charts to `app.py`**

Add this helper function directly below the `get_data()` function (above `st.set_page_config`):

```python
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
```

Append to the end of `app.py`:

```python
# --- Category and region breakdowns ------------------------------------------
category_column, region_column = st.columns(2)

with category_column:
    st.subheader("Sales by Category")
    st.plotly_chart(bar_chart(analytics.sales_by_category(df), "category", "Category"))

with region_column:
    st.subheader("Sales by Region")
    st.plotly_chart(bar_chart(analytics.sales_by_region(df), "region", "Region"))
```

- [ ] **Step 7: Check the app**

```bash
python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py').run()
print('exceptions:', list(at.exception))
print('subheaders:', [s.value for s in at.subheader])
print('charts:', len(at.get('plotly_chart')))
"
```

Expected:
```
exceptions: []
subheaders: ['Sales Trend Over Time', 'Sales by Category', 'Sales by Region']
charts: 3
```

In a browser, the owner should see two charts side by side:
- Category, top to bottom: Electronics, Wearables, Audio, Smart Home, Accessories
- Region, top to bottom: North, West, East, South

- [ ] **Step 8: Move TASK-5 to Done and commit**

In `TASKS.md`, move TASK-5 to `## Done` and tick its three checkboxes. Leave `Commit:` blank.

```bash
git add analytics.py tests/test_analytics.py app.py TASKS.md
git commit -m "TASK-5: add category and region bar charts" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Plan Task 6: Verify against the PRD — [Milestone TASK-6]

**Files:**
- Modify: `TASKS.md`
- Modify: `app.py` / `analytics.py` only if a check below fails (fix, re-run `pytest`, re-check)

**Interfaces:**
- Consumes: everything from Plan Tasks 1–5
- Produces: a verified, committed dashboard on `feature/sales-dashboard`, ready for the owner to merge

- [ ] **Step 1: Move TASK-6 to In Progress on the board**

In `TASKS.md`, move the `### TASK-6: …` block from `## To Do` to `## In Progress`.

- [ ] **Step 2: Run the full test suite**

Run: `pytest -v`
Expected: 17 passed, 0 failed, and no warnings in the summary line.

- [ ] **Step 3: Confirm `analytics.py` stays free of Streamlit and Plotly**

Run: `grep -nE "import (streamlit|plotly)|from (streamlit|plotly)" analytics.py`
Expected: no output.

- [ ] **Step 4: Run the whole page once and check for errors, warnings, and speed**

```bash
time python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py').run()
print('exceptions:', list(at.exception))
print('errors:', [e.value for e in at.error])
print('warnings:', [w.value for w in at.warning])
print('metrics:', [(m.label, m.value) for m in at.metric])
print('charts:', len(at.get('plotly_chart')))
"
```

Expected:
```
exceptions: []
errors: []
warnings: []
metrics: [('Total Sales', '$116,500'), ('Total Orders', '482')]
charts: 3
```

The `real` time should be well under 5 seconds. Streamlit shows its own deprecation notices as page warnings, so `warnings: []` also confirms we aren't using a deprecated option.

- [ ] **Step 5: Owner checks the page in the browser**

Ask the owner to run `streamlit run app.py`, open the page, and confirm each item against the PRD's "Expected Output" and "Dashboard Layout":

| Check | Expected |
|---|---|
| Page loads | in under 5 seconds, with no red error boxes |
| Total Sales | `$116,500` |
| Total Orders | `482` |
| Trend chart | 12 monthly points, Jan 2024 – Dec 2024, dollar values on hover |
| Category chart | Electronics at the top, 5 bars, dollar values on hover |
| Region chart | North, West, East, South (top to bottom), dollar values on hover |
| Layout | KPIs on top, trend in the middle, the two bar charts side by side at the bottom |

Wait for the owner to confirm. If something is off, fix it, re-run `pytest -v`, and repeat this step.

- [ ] **Step 6: Move TASK-6 to Done and commit**

In `TASKS.md`, move TASK-6 to `## Done` and tick its three checkboxes. Leave `Commit:` blank.

```bash
git add TASKS.md
git commit -m "TASK-6: verify dashboard against PRD" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

(If Step 5 led to fixes, include those files in the same `git add`.)

- [ ] **Step 7: Stop and hand off to the owner**

The plan's automated work ends here. Report to the owner:
- the branch name (`feature/sales-dashboard`) and `git log --oneline main..HEAD`
- that all tests pass
- that TASK-7 is theirs, with the checklist in Plan Task 7 below

Do **not** merge, push, or deploy.

---

### Plan Task 7: Deploy to Streamlit Community Cloud — [Milestone TASK-7] — OWNER EXECUTES

> **Not for agentic workers.** This task is done by the owner. An executing agent must stop at the end of Plan Task 6.

**Files:**
- Modify: `README.md` (public URL)
- Modify: `TASKS.md` (move TASK-7 to Done)

- [ ] **Step 1: Merge the feature branch into `main`**, by pull request or locally, whichever you prefer.
- [ ] **Step 2: Push `main` to GitHub.**
- [ ] **Step 3: Create the app on Streamlit Community Cloud.** Use your repo, branch `main`, and main file path `app.py`.
- [ ] **Step 4: Choose the Python version.** Under **Advanced settings**, pick the same Python version you used locally (3.14), or the closest available one, so the pinned packages in `requirements.txt` install the versions you tested.
- [ ] **Step 5: Check the deployed app.** Open the public URL and confirm it matches the table in Plan Task 6, Step 5, with no errors.
- [ ] **Step 6: Record the public URL in `README.md`**, then move TASK-7 to Done in `TASKS.md` and commit on `main` with a message starting `TASK-7:`.
