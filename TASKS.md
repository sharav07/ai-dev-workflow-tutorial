# Tasks

This file tracks all work for the ShopSmart Sales Dashboard (see `prd/ecommerce-analytics.md`).

## Definition of Done

A milestone moves to Done only when:

- All of its acceptance criteria are met
- The app runs locally with `streamlit run app.py`
- Changes are committed with the milestone ID in the commit message (e.g. `TASK-3: add KPI cards`)

## To Do

### TASK-7: Deploy to Streamlit Community Cloud
Publish the dashboard at a public, shareable URL (NFR-5).
- [ ] App is deployed to Streamlit Community Cloud and loads without errors
- [ ] Public URL is recorded in the README

Commit:

## In Progress

## Done

### TASK-6: Testing and refinement
Verify numbers against the CSV and polish the dashboard for executive use.
- [x] All displayed values match calculations from the CSV
- [x] Dashboard loads in under 5 seconds with no errors or warnings
- [x] Layout matches the PRD's expected dashboard layout

Commit:

### TASK-5: Category and region breakdowns
Add side-by-side bar charts for sales by category and by region (FR-3, FR-4).
- [x] Category chart shows all 5 categories, sorted highest to lowest (Electronics first)
- [x] Region chart shows all 4 regions, sorted highest to lowest
- [x] Both charts have clear labels and tooltips with exact values

Commit: 61a9d95

### TASK-4: Sales trend chart
Add an interactive Plotly line chart of sales over time (FR-2).
- [x] Line chart shows sales by month across the 12-month range
- [x] Axes are labeled and tooltips show exact values

Commit: 6f09536

### TASK-3: KPI cards
Display Total Sales and Total Orders prominently at the top of the dashboard (FR-1).
- [x] Total Sales is shown formatted as currency (~$116,500)
- [x] Total Orders is shown with thousands separators (482)

Commit: 6750f48

### TASK-2: Data loading and basic structure
Load `data/sales-data.csv` with Pandas and set up the dashboard's layout sections.
- [x] CSV loads with `date` parsed as a date and numeric columns as numbers
- [x] Loaded data has 482 rows, 5 categories, and 4 regions
- [x] A clear error message is shown if the CSV is missing or has unexpected columns

Commit: bde3315

### TASK-1: Environment setup and project initialization
Set up the Python 3.11+ environment and project skeleton for the Streamlit app.
- [x] `requirements.txt` lists streamlit, pandas, and plotly, and installs cleanly
- [x] `app.py` exists and shows a dashboard title when run with `streamlit run app.py`

Commit: 17eaaa7
