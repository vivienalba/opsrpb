# Viv’s Operations Report Builder

A Python portfolio app that turns activity records into weekly, monthly, quarterly, and annual operations reports. The landing screen follows the supplied design reference: green grid, bold white headline, a desktop spreadsheet illustration, and a yellow processing button.

## Start on your Mac

1. Extract the ZIP.
2. Open Terminal. Type `python3` followed by a space.
3. Drag **launch.py** from the extracted folder into Terminal, then press Enter.
4. The launcher installs the requirements in its own virtual environment and starts the app. Open the local URL printed in Terminal (usually http://localhost:8501). Keep Terminal open. Press Control+C to stop.

Python 3.10 or newer and internet access for the initial dependency installation are required. If you already have another app using port 8501, Streamlit may choose the next port.

Alternatively, from this project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

## Try it

Click **PROCESS YOUR DATA HERE**, keep **Sample dataset**, choose a reporting frequency and any date within the period, then click **GENERATE OPERATIONS REPORT**. The example is fictional and spans 2025–2026. The default date is September 15, 2026, within a completed historical reporting period.

## Use your data

- CSV, TSV, and XLSX uploads, up to 20 MB; select a worksheet for Excel.
- One row per activity; header row required.
- Required mappings: activity date and status.
- Optional mappings: activity name, owner, due date, completed date, category, numeric value.
- Choose YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY for text dates. Genuine Excel datetime cells are recognized directly. Mixed text-date formats should be standardized before upload.
- Choose which statuses mean completed and which are excluded (for example Cancelled).
- Numeric values must be plain numbers; currency symbols and thousands separators are not guessed.
- Review data quality and methodology before export.

## What reports mean

Calendar weeks run Monday–Sunday. Quarters begin in January, April, July, and October. Annual periods are calendar years, not rolling 12-month periods or fiscal years.

The mapped activity date defines the period cohort. Each row counts once; duplicate rows are retained. This is an activity report, not a unique-task or event-history system.

Completed counts use the selected statuses. If a completion date is mapped, it must be valid and at/before the cutoff. Completed-status rows with unusable completion dates are counted as open and flagged in the notes. If completion dates are not mapped, status is a current uploaded snapshot and cannot establish historical completion timing.

The cutoff is the earlier of period end or today's date in Asia/Manila. Overdue means an open, non-excluded activity with a due date before the cutoff. A task due on the cutoff date is not overdue. Only the period cohort is included, not the full historical backlog.

Completion rate = completed eligible activities / (all period activities minus excluded statuses). Future periods may include planned activities. Missing/invalid activity dates are excluded and listed. Missing periods do not establish that no business activity occurred. Previous-period comparison concerns activity counts only.

The summary is calculated from these rules; no AI-generated claims or external AI calls are used.

## Exports

**Excel:** summary, complete period activities, owner workload, status breakdown, trend, data issues, methodology, settings, and a status chart. Source text is written as text, not executable Excel formulas.

**PDF:** report title, summary, metrics, workload, status breakdown, up to 30 overdue activities, and methodology. The complete activity list is in Excel.

Reports are generated in session memory. Uploads are not intentionally written to disk, externally shared, or placed in a shared cross-user cache. Host-level logging and memory retention depend on the deployed service; avoid confidential information on a public portfolio demo.

## Deploy from GitHub

Create a separate repository for this project. Upload app.py, core.py, exports.py, design.py, favicon.png, requirements.txt, and .streamlit/config.toml at the repository root. Other included files are optional. Do not upload your .venv folder or real customer data.

In Streamlit Community Cloud, choose that repository and branch and set the entrypoint to **app.py**. Keep the full source folder together; app.py imports the other three Python modules. No API keys are required.

## Checks

From this folder, run:

```bash
python3 -m unittest test_reporting.py
```

Tests cover calendar boundaries (including leap years), counted/excluded statuses, missing dates, empty reports, upload formats, and export integrity.

## Portfolio description

A Python operations reporting application that converts CSV, TSV, and Excel records into weekly, monthly, quarterly, and annual reports. Includes configurable column mapping, workload analysis, completion and overdue metrics, data-quality checks, and downloadable Excel and PDF reports.
