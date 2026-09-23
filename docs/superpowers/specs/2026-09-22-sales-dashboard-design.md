# ShopSmart Sales Dashboard — Design

**Date:** 2026-09-22
**Source requirements:** `prd/ecommerce-analytics.md` (Phase 1 only)
**Milestones:** tracked in `TASKS.md` (TASK-1 … TASK-7)
**Branch:** `feature/sales-dashboard`

## Goal

A single-page Streamlit dashboard that shows ShopSmart's 2024 sales at a glance:
two KPIs, a monthly sales trend, and sales broken down by category and by region.
The code should be simple enough for its owner to read top to bottom and explain.
When simplicity and cleverness conflict, choose simplicity.

## Scope

**In scope (PRD FR-1 to FR-5):** KPI cards, trend line chart, category bar chart,
region bar chart, loading from `data/sales-data.csv`.

**Out of scope (PRD Phase 2):** filters and date ranges, export, authentication,
database integration, drill-down, mobile-specific layout.

## Data facts (verified against the CSV)

- 482 rows, 482 unique `order_id`s
- Total sales: $116,500.21
- Dates: 2024-01-03 to 2024-12-31 (12 months)
- Categories: Accessories, Audio, Electronics, Smart Home, Wearables
- Regions: East, North, South, West
- Columns: `date, order_id, product, category, region, quantity, unit_price, total_amount`

## Architecture

```
app.py                  Streamlit page: layout, KPI cards, Plotly charts
analytics.py            Pure Pandas: loading + all calculations (no Streamlit)
tests/test_analytics.py pytest tests for analytics.py
pytest.ini              sets pythonpath = . so tests can import analytics
requirements.txt        exact pins: streamlit, pandas, plotly, pytest
data/sales-data.csv     source data (already present)
```

Data flows one way: `CSV → analytics.load_data → analytics calculation functions → app.py → browser`.

`analytics.py` never imports Streamlit or Plotly, so every calculation can be
tested with plain pytest.

## `analytics.py`

| Function | Input | Output |
|---|---|---|
| `load_data(path)` | path to CSV | DataFrame with `date` parsed as datetime |
| `total_sales(df)` | DataFrame | `float`, sum of `total_amount` |
| `total_orders(df)` | DataFrame | `int`, number of unique `order_id` |
| `monthly_sales(df)` | DataFrame | DataFrame with columns `month` (Timestamp, first day of month) and `sales`, one row per month, oldest first |
| `sales_by_category(df)` | DataFrame | DataFrame with columns `category`, `sales`, sorted by `sales` descending |
| `sales_by_region(df)` | DataFrame | DataFrame with columns `region`, `sales`, sorted by `sales` descending |

`sales_by_category` and `sales_by_region` both call a private helper
`_sales_by(df, column)` that does the group, sum, and sort.

### Error handling

- `load_data` checks that all 8 expected columns are present. If any are missing,
  it raises `ValueError` naming the missing columns.
- A missing file raises the normal `FileNotFoundError`.
- `app.py` catches both around its load call and shows
  `st.error("Could not load sales data: <message>")`, then `st.stop()`.
  The user never sees a traceback.

## `app.py`

The file reads in the same order as the page appears:

1. **Setup:** `st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")`
   and the page title "ShopSmart Sales Dashboard".
2. **Load:** `get_data()` in `app.py`, decorated with `@st.cache_data`, calls
   `analytics.load_data("data/sales-data.csv")`. Caching lives here so
   `analytics.py` stays Streamlit-free.
3. **KPI row:** two columns, each with an `st.metric`:
   - Total Sales, formatted `$116,500` (whole dollars, thousands separators)
   - Total Orders, formatted `482` (thousands separators)
4. **Sales trend:** full-width Plotly line chart of `monthly_sales`, with markers.
   The x-axis shows month labels (Jan 2024 … Dec 2024) and the y-axis shows sales in dollars.
   Hover shows the month and exact dollar value (e.g. `$9,812.40`).
5. **Breakdowns:** two columns.
   - Left: "Sales by Category", a horizontal bar chart with the largest bar at the top.
   - Right: "Sales by Region", a horizontal bar chart with the largest bar at the top.
   - Hover shows exact dollar values.

**Styling:** all charts use one consistent color, and every chart and axis has a
clear title. Streamlit defaults otherwise, with no custom CSS.

## Testing

`tests/test_analytics.py`, run with `pytest` from the project root.

**Small hand-built DataFrames** (3–5 rows, answers checkable by eye):
- `total_sales` sums `total_amount`
- `total_orders` counts unique order IDs (duplicate IDs are counted once)
- `monthly_sales` groups by calendar month and returns months oldest first
- `sales_by_category` / `sales_by_region` sum correctly and sort highest first
- `load_data` parses `date` as datetime (via a small CSV written to `tmp_path`)
- `load_data` raises `ValueError` naming a missing column (via `tmp_path`)

**Real CSV checks** (`data/sales-data.csv`):
- `total_orders` == 482
- `total_sales` == 116,500.21 (to the cent)
- `monthly_sales` has 12 rows
- Top category is Electronics
- All 4 regions are present

`analytics.py` is built test-first: write a failing test, watch it fail, then make it pass.

`app.py` is checked manually by running `streamlit run app.py` and comparing
against the PRD's expected output and layout.

## Environment

- `python3 -m venv venv`, then `source venv/bin/activate`, then `pip install -r requirements.txt`
- `requirements.txt` pins exact versions of `streamlit`, `pandas`, `plotly`, and `pytest`,
  using the versions installed and tested locally
- `venv/` is already ignored by `.gitignore`
- No uv, no conda, no git worktree

## Workflow and milestones

- All work happens on `feature/sales-dashboard`.
- Each milestone ends with a commit whose message starts with its ID (e.g. `TASK-3: add KPI cards`)
  and moves the item across the `TASKS.md` board (To Do → In Progress → Done).
  The owner fills in the `Commit:` line.
- The implementation plan labels each of its tasks with the milestone it belongs to,
  and keeps its own step numbering separate from the TASK IDs.

| Milestone | Covered by |
|---|---|
| TASK-1 | venv, `requirements.txt`, `pytest.ini`, minimal `app.py` showing the title |
| TASK-2 | `load_data` + tests; `app.py` loads data with the error handling above |
| TASK-3 | `total_sales`, `total_orders` + tests; KPI row |
| TASK-4 | `monthly_sales` + tests; trend chart |
| TASK-5 | `_sales_by`, `sales_by_category`, `sales_by_region` + tests; bar charts |
| TASK-6 | full test run, manual check against PRD numbers and layout, load time under 5 s, no errors or warnings |
| TASK-7 | **Owner executes:** merge to `main`, deploy to Streamlit Community Cloud, record the URL in the README |

## Deployment handoff (TASK-7)

The plan stops at the end of TASK-6. The owner then:

1. Merges `feature/sales-dashboard` into `main`.
2. Deploys from `main` on Streamlit Community Cloud with `app.py` as the entry point.
3. In Cloud's Advanced settings, selects the same Python version used locally
   (3.14), or the closest available, so the pinned packages match what was tested.
4. Records the public URL in the README.
