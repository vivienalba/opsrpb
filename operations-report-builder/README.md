# Viv’s Operations Cleaner

CSV and TSV data cleaning plus multi-sheet Excel workbook cleaning that retains the original workbook structure and formatting definitions.

The interface keeps OpsClean’s purple and yellow identity, with larger touch controls, visible search and filter labels, a numbered workflow, and a consistent CSV/Excel review panel. The copyright and Terms and Policies button share one footer row on mobile. Sample and export buttons remain off-white, and the upload button remains outside the dashed drop zone.

Cleaning summaries use a brief Anime.js 4.5.0 entrance. Final numbers are visible immediately, unchanged summaries do not replay on search/filter updates, and the device’s **Reduce Motion** setting disables the effect. The animation library is included locally, so no CDN, npm install, or JavaScript build is required to run the app. Only summary counts and labels enter the component; uploaded cell contents do not.

## Run on your Mac

1. Extract this ZIP into a folder.
2. Open Terminal, type `python3` followed by a space, drag `launch.py` into Terminal, and press Enter.
3. The launcher finds its own folder, installs requirements into its own `.venv`, and starts Streamlit. Open the localhost URL printed in Terminal.

Python 3.10 or newer and internet access for the first installation are required. Keep Terminal open while using the app. Press Control+C to stop.

Alternatively, run these commands from the extracted project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

## Excel workflow

1. Upload an ordinary `.xlsx` workbook.
2. Choose one or several worksheet checkboxes, or enable **Clean all sheets**.
3. Check the data range for each selected sheet. Its first row must be the table header. Exclude titles, notes, summary sections, and separate tables.
4. Choose trimming, email casing, and Philippine mobile formatting rules.
5. Click **Clean selected sheets** or **Clean all sheets**.
6. Review each sheet’s original data, cleaned data, change log, missing cells, and duplicate rows.
7. Download **Export cleaned Excel workbook**.

All original worksheets, including unselected and hidden sheets, remain in the workbook. Retaining these sheets protects cross-sheet references. Sheet names and order remain intact. Chart sheets and other package parts are retained without being cleaned.

## What is preserved

The app edits plain-text cell values directly inside a copy of the original Excel package. It does not convert the workbook into a newly formatted spreadsheet or save it through a workbook writer.

Every package part other than selected worksheet XML is copied byte for byte, including styles, themes, shared strings, images, chart definitions, table definitions, comments, relationships, and workbook settings. Within a selected worksheet, only changed text cell value markup is replaced. Cell style references and all other worksheet markup are retained, including row/column dimensions, merged regions, filters, print settings, validation, conditional-formatting rules, and freeze panes.

Headers remain unchanged to protect table and formula references. Formulas and their cached values, numbers, date values and formats, rich text, merged cells, hyperlink cells, and protected worksheets are not edited. Formula results and conditional-formatting appearance can change when Excel recalculates the cleaned values. In a workbook with manual calculation enabled, recalculate in Excel before relying on results. Cleaning changes the text content, so text wrapping or chart labels may look different even though their formatting settings are retained. Universal pixel-identical appearance across Excel versions cannot be guaranteed.

Duplicate rows are identified after cleaning but retained. Removing or shifting rows conflicts with preserving arbitrary workbook layouts and formula references. Missing values are flagged in the app without inserting, filling, or recoloring cells. No extra report worksheet is added.

Mobile formatting applies only to plain text in columns containing phone, mobile, or contact_number. Numeric phone cells are preserved. Emails are identified through email/e-mail column names. Status names and date conventions are not automatically guessed or standardized.

The preview is a value table, not a visual rendering of Excel formatting. Numeric date cells may appear as Excel serial values in previews; their original Excel display formats remain in the workbook. Preview rows retain Excel row numbers. Duplicate detection compares the selected range and compares formulas as expressions rather than calculated results.

Digitally signed, encrypted, or unsupported XML-format workbooks are rejected rather than silently converted. Each chosen range is limited to 1,000,000 cells, and expanded workbooks over 512 MB are rejected. The uploader's existing 200 MB limit is retained.

## CSV and TSV

The existing workflow remains available: standardize column names, trim whitespace, lowercase emails, normalize Philippine mobile text, remove duplicate rows, flag missing cells, and download cleaned CSV. These plain-text files do not contain Excel worksheet formatting.

## Deploy

Upload the complete extracted project to your Ops Cleaner repository. Keep these files and folders together:

- `app.py`, `ui.py`, and `workbook_cleaner.py`
- `assets/` and `components/`, including all summary component and vendor files
- `favicon.png` and `requirements.txt`
- `.streamlit/config.toml`

The entrypoint remains `app.py`. Do not upload `.venv`, `__pycache__`, or real customer files. Replacing only `app.py` is insufficient for this version.

## Customize the interface

Page styles are in `assets/opsclean.css`, rather than pasted into Python code. Summary styles are in `components/summary/summary.css`. The theme file is `.streamlit/config.toml` beside the app’s project files.

## Verification

```bash
python3 -m unittest test_workbooks.py
```

Tests check selected-sheet isolation, shared strings, cell styles, number formats, formulas, merged/hyperlink/rich-text protection, dimensions, freeze panes, worksheet settings, duplicate retention, protected sheets, signed-workbook rejection, ranges, and literal text safety. Streamlit interactions were checked for one, several, and all sheets, the original CSV sample flow, rule resets, search, missing-row filtering, and stale-download prevention. Browser checks covered desktop and 390/320-pixel mobile layouts, the footer baseline, the policy dialog, the summary component, and reduced motion. The tests verify the included fixtures; they cannot certify every possible workbook or browser.
