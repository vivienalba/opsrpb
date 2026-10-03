"""OpsClean — run with: python -m streamlit run app.py"""

import csv
import hashlib
import html
import io
import re
import zipfile
from pathlib import Path
from xml.etree.ElementTree import ParseError

import pandas as pd
import streamlit as st
from workbook_cleaner import WorkbookSource, clean_workbook
from ui import CSS, csv_summary, render_steps, workbook_summary


SAMPLE_CSV = 'Customer Name,Email Address,Mobile Number,Booking Status,Service Requested\n  Maria Santos  ,MARIA.SANTOS@EMAIL.COM ,0917-123-4567,Confirmed,Dental Cleaning\nJuan Dela Cruz, juan@email.com,0918 222 3333,Pending,Consultation\n  Maria Santos  ,MARIA.SANTOS@EMAIL.COM ,0917-123-4567,Confirmed,Dental Cleaning\nAna Reyes,,0919-555-0101,Pending,Teeth Whitening\nCarlo Lim ,CARLO@EXAMPLE.COM,,Cancelled,Consultation\n Bianca Cruz,bianca@email.com ,+63 920 111 2222,Confirmed,\n'


RULES = [
    ("headers", "Standardize column names", "Use lowercase names with underscores. Duplicate names get a unique suffix."),
    ("whitespace", "Trim extra spaces", "Remove spaces at the beginning and end of text values."),
    ("emails", "Lowercase email addresses", "Apply to columns whose names contain email or e-mail. This does not validate addresses."),
    ("phones", "Format Philippine mobiles", "Convert recognized 09, 9, or 639 mobile formats to +639. Other numbers are kept as entered."),
    ("duplicates", "Remove duplicate rows", "Keep the first of any rows that match after the selected cleaning rules."),
]




def clean_column_name(name):
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


def unique_column_names(columns):
    """Do not let punctuation-only or colliding headers break a DataFrame."""
    used, names = set(), []
    for index, column in enumerate(columns, start=1):
        base = clean_column_name(column) or f"column_{index}"
        candidate, suffix = base, 2
        while candidate in used:
            candidate = f"{base}_{suffix}"
            suffix += 1
        used.add(candidate)
        names.append(candidate)
    return names


def clean_phone(value):
    if pd.isna(value):
        return value
    text = str(value)
    # Only normalize recognizable mobile numbers; retain extensions/other formats.
    if not re.fullmatch(r"[+\d\s().-]+", text):
        return text
    digits = re.sub(r"\D", "", text)
    if re.fullmatch(r"09\d{9}", digits):
        return "+63" + digits[1:]
    if re.fullmatch(r"639\d{9}", digits):
        return "+" + digits
    if re.fullmatch(r"9\d{9}", digits):
        return "+63" + digits
    return text


def count_changes(before, after):
    return int((before.fillna("") != after.fillna("")).sum().sum())


def clean_dataframe(original, options=None):
    options = options or {key: True for key, _, _ in RULES}
    data = original.astype("string").copy()
    old_columns = list(data.columns)
    log = []
    blank_mask = data.apply(lambda column: column.str.fullmatch(r"\s*", na=False))
    data = data.mask(blank_mask, pd.NA)
    baseline = data.copy()

    def record(rule, count, unit, key):
        log.append({"Cleaning rule": rule, "Status": "Applied" if options[key] else "Off", "Affected": f"{count:,} {unit}" if options[key] else "—"})

    renamed = unique_column_names(old_columns) if options["headers"] else old_columns
    rename_count = sum(str(old) != str(new) for old, new in zip(old_columns, renamed))
    record("Column names", rename_count, "columns", "headers")

    before = data.copy()
    if options["whitespace"]:
        data = data.apply(lambda column: column.str.strip())
    record("Extra spaces", count_changes(before, data), "cells", "whitespace")

    before = data.copy()
    if options["emails"]:
        for column in old_columns:
            if "email" in clean_column_name(column).replace("_", ""):
                data[column] = data[column].str.lower().str.strip()
    record("Email casing", count_changes(before, data), "cells", "emails")

    before = data.copy()
    if options["phones"]:
        for column in old_columns:
            field = clean_column_name(column)
            if any(token in field for token in ("phone", "mobile", "contact_number")):
                data[column] = data[column].apply(clean_phone).astype("string")
    record("Philippine mobile format", count_changes(before, data), "cells", "phones")

    # Count individual cells only once, even if several rules changed them.
    edited_cells = count_changes(baseline, data)
    candidates = int(data.duplicated().sum())
    removed = candidates if options["duplicates"] else 0
    if options["duplicates"]:
        data = data.drop_duplicates()
    record("Duplicate rows", removed, "rows", "duplicates")
    data.columns = renamed
    # Preserve source row indexes for comparing original and cleaned previews.
    missing = data.isna().sum()
    missing = missing[missing > 0]
    missing_table = pd.DataFrame({"Column": missing.index, "Missing cells": missing.values})
    missing_table["Share of rows"] = missing.values / len(data) * 100 if len(data) else 0
    report = {
        "original_rows": len(original),
        "cleaned_rows": len(data),
        "duplicates_removed": removed,
        "duplicates_remaining": candidates if not options["duplicates"] else 0,
        "edited_cells": edited_cells,
        "columns_standardized": rename_count,
        "missing_cells": int(missing.sum()),
        "missing_rows": int(data.isna().any(axis=1).sum()),
        "missing_table": missing_table,
        "log": pd.DataFrame(log),
        "column_map": pd.DataFrame({"Original name": old_columns, "Current name": renamed}),
    }
    return data, report


def read_csv(raw, encoding="utf-8-sig", separator="Auto-detect", filename="data.csv"):
    extension = Path(filename).suffix.lower()
    if extension == ".xlsx":
        return pd.read_excel(io.BytesIO(raw), sheet_name=0, dtype="string",
                             keep_default_na=False, engine="openpyxl")
    text = raw.decode(encoding)
    separators = {"Comma": ",", "Semicolon": ";", "Tab": "\t", "Pipe": "|"}
    if separator == "Auto-detect":
        if extension == ".tsv":
            delimiter = "\t"
        else:
            try:
                delimiter = csv.Sniffer().sniff(text[:65536], delimiters=",;\t|").delimiter
            except csv.Error:
                delimiter = ","
    else:
        delimiter = separators[separator]
    return pd.read_csv(io.StringIO(text), sep=delimiter, dtype="string", keep_default_na=False)


def set_source(source):
    st.session_state["source"] = source


def reset_rules():
    for key, _, _ in RULES:
        st.session_state[f"rule_{key}"] = True


def display_table(data, key, query="", only_missing=False, row_limit=250):
    preview = data
    if only_missing:
        preview = preview.loc[preview.isna().any(axis=1)]
    if query.strip():
        term = query.strip()
        match = preview.apply(lambda column: column.str.contains(term, case=False, regex=False, na=False)).any(axis=1)
        preview = preview.loc[match]
    total = len(preview)
    shown = preview.head(row_limit).copy()
    shown.index = shown.index + 1
    shown.index.name = "Source row"
    if not total:
        st.info("No rows match this view. Clear the search or select All rows to see your data.")
        return
    st.dataframe(
        shown,
        key=key,
        width="stretch",
        height=min(535, max(210, len(shown) * 36 + 40)),
        row_height=36,
        column_config={"_index": st.column_config.NumberColumn("Row", width="small")},
    )
    st.caption(f"Showing {len(shown):,} of {total:,} rows in this view. Row numbers refer to the source data. Export includes the complete cleaned dataset.")


def render_masthead():
    st.markdown("""
    <div class="masthead">
      <svg class="loop-art" viewBox="0 0 130 190" aria-hidden="true" fill="none" stroke="#171219" stroke-width="1.8">
        <path d="M8 0 V116 a57 57 0 0 0 114 0 V0"/><path d="M18 0 V116 a47 47 0 0 0 94 0 V0"/>
        <path d="M28 0 V116 a37 37 0 0 0 74 0 V0"/><path d="M38 0 V116 a27 27 0 0 0 54 0 V0"/>
        <path d="M48 0 V116 a17 17 0 0 0 34 0 V0"/>
      </svg>
      <span class="brand-dot" aria-hidden="true"></span>
      <div class="brand">OpsClean</div>
      <svg class="burst" viewBox="0 0 100 100" aria-hidden="true"><path d="M50 0 64 16 86 14 84 36 100 50 84 64 86 86 64 84 50 100 36 84 14 86 16 64 0 50 16 36 14 14 36 16Z"/></svg>
    </div>
    """, unsafe_allow_html=True)


def render_intro():
    st.markdown("""
    <div class="hero-copy">
      <p class="hero-intro">A clearer starting point for your next report.</p>
      <div class="hero-title" role="heading" aria-level="1">Operational<br>data.<br>Made clear.</div>
      <div class="hero-detail">
        <h3 class="welcome-heading">Welcome to Viv’s Operations Cleaner</h3>
        <p>A Python powered tool that helps operations teams, small businesses, and freelancers turn messy CSV, TSV, and Excel data into clean, organized records ready for Excel, CRM imports, and reporting.</p>
        <p>Simply upload your file, choose your cleaning options, review the results, and download your cleaned file. Always review your data before using it in a live business system.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_import(compact=False):
    if not compact:
        st.markdown('<h2 class="import-heading">Import Dataset</h2>', unsafe_allow_html=True)
        st.caption("Start with a CSV, TSV, or Excel workbook.")
    with st.container(key="upload_controls"):
        uploaded = st.file_uploader("Upload CSV, TSV, or Excel", type=["csv", "tsv", "xlsx"], key="uploaded_csv", on_change=set_source, args=("upload",), label_visibility="collapsed")
    if st.session_state["source"] == "sample":
        st.button("Close sample", key="close_sample", width="stretch", on_click=set_source, args=("upload",), icon=":material/close:")
    else:
        st.button("Try the sample dataset", key="load_sample", width="stretch", on_click=set_source, args=("sample",), icon=":material/table_view:", type="primary")
    encoding_label, separator = "UTF-8", "Auto-detect"
    if uploaded is not None and uploaded.name.lower().endswith('.xlsx'):
        st.caption("Excel sheets and data ranges can be selected below.")
    else:
        with st.expander("Import settings"):
            encoding_label = st.selectbox("File encoding", ["UTF-8", "Windows-1252", "UTF-16"], key="import_encoding")
            separator = st.selectbox("Column separator", ["Auto-detect", "Comma", "Semicolon", "Tab", "Pipe"], key="import_separator")
            st.caption("If characters or columns look wrong, adjust these settings.")
    if not compact:
        st.caption("Your original stays unchanged. Review every change before exporting.")
    return uploaded, encoding_label, separator



@st.dialog("Terms and Policies", width="large")
def show_policies():
    with st.expander('Privacy Policy'):
        st.markdown('Viv’s Ops Cleaner is designed to process files for the purpose of cleaning and reviewing data. Please avoid uploading passwords, financial account information, government identification numbers, medical information, or other highly sensitive or confidential data unless the application has been appropriately secured for that use.\n\nIf this application is publicly hosted, its hosting provider may process technical information necessary to operate the service. Before using Viv’s Ops Cleaner with real business or customer information, users are responsible for confirming that they have permission to process that information and that their use complies with applicable privacy and data-protection requirements.')
    with st.expander('Terms & Conditions'):
        st.markdown('Viv’s Ops Cleaner is provided as a data-cleaning and productivity tool. While the application is designed to improve common formatting and data-quality issues, automated processing may not identify or correct every error.\n\nUsers remain responsible for reviewing cleaned data before importing, publishing, sharing, or using it for business decisions. By using the application, you agree not to upload data you do not have authorization to process or use the service for unlawful purposes.\n\nThe application is provided without a guarantee that its output will be error-free or suitable for every business system.')
    with st.expander('Cookie Policy'):
        st.markdown('Viv’s Ops Cleaner does not intentionally use advertising or marketing cookies in its current portfolio version. However, the hosting platform or integrated third-party services may use technically necessary cookies or similar technologies to provide their services.\n\nIf analytics, embedded third-party services, authentication, or advertising technologies are added in the future, this policy and the application’s consent mechanisms should be updated accordingly.')
    with st.expander('Data Upload Consent'):
        st.markdown('By uploading a file, you confirm that you are authorized to use and process the information contained within it and consent to the file being processed for the functionality you request.\n\nDo not upload sensitive or confidential information unless you understand how the deployed version of the application stores, transmits, and processes uploaded files.')
    with st.expander('Accessibility'):
        st.markdown('Viv’s Ops Cleaner aims to provide a clear and accessible experience through readable text, descriptive labels, appropriate color contrast, keyboard-friendly controls, and meaningful interface elements. Accessibility improvements will continue as the project develops.')
    with st.expander('Important Notice'):
        st.markdown('Viv’s Ops Cleaner assists with data preparation; it does not replace human review. Always verify cleaned information before using it in a CRM, reporting system, customer database, or other production environment.')



def render_policies():
    with st.container(key="policy_footer"):
        st.markdown('<p class="footer-copyright">© 2026 FVA</p>', unsafe_allow_html=True)
        if st.button("Terms and Policies", key="open_policies", type="tertiary"):
            show_policies()


def render_workbook(raw, filename):
    """A separate Excel workflow keeps CSV duplicate removal from shifting Excel rows."""
    digest = hashlib.sha256(raw).hexdigest()
    try:
        source = WorkbookSource(raw)
        sheets = list(source.sheets)
        st.title("Clean your workbook")
        st.markdown(f'<div class="file-line"><span class="file-name">{html.escape(filename)}</span><span> {len(sheets):,} sheets detected</span></div>', unsafe_allow_html=True)
        progress = st.empty()
        st.caption("Choose your sheets and ranges. The Excel export keeps all original sheets and their formatting definitions.")
        chosen = []
        sheet_controls, rule_controls = st.columns([1.1, 1], gap="large")
        with sheet_controls:
            with st.expander(f"Choose sheets {len(sheets):,} detected", expanded=True):
                all_sheets = st.checkbox("Clean all sheets", key=f"all_sheets_{digest}")
                for i, name in enumerate(sheets):
                    checked = st.checkbox(name, value=i == 0, disabled=all_sheets, key=f"sheet_{digest}_{i}")
                    if all_sheets or checked:
                        chosen.append(name)
                st.caption(f"{len(chosen):,} of {len(sheets):,} sheets selected")
        options = {}
        with rule_controls:
            with st.expander("Workbook cleaning rules", expanded=True):
                for key, label, help_text in RULES:
                    if key in ("headers", "duplicates"):
                        continue
                    options[key] = st.checkbox(label, value=True, key=f"workbook_rule_{key}", help=help_text)
                st.caption("Headers stay as entered. Duplicate rows are flagged and kept in place to preserve the workbook layout.")
        if not chosen:
            with progress.container():
                render_steps(1)
            st.info("Choose at least one sheet to clean.")
            render_policies()
            return
        ranges = {}
        with st.expander("Data ranges", expanded=True):
            st.caption("Start each range with its header row. Exclude titles, summaries, notes, and separate tables.")
            for name in chosen:
                sheet = source.sheet(name)
                ranges[name] = st.text_input(f"{name} · data range including header", value=sheet['extent'], key=f"range_{digest}_{name}")
                if sheet['protected']:
                    st.caption(f"{name} is protected. Its values will be reviewed but not edited.")
        with st.expander("How Excel formatting is preserved"):
            st.write("Only plain text in your selected ranges is cleaned. Formulas, numbers, date values, rich text, merged cells, hyperlinks, and protected sheets stay intact. Status labels and dates are not guessed or standardized.")
            st.write("Formatting definitions, images, charts, tables, and print settings are retained. Excel may recalculate formulas; changed values can affect conditional formatting, chart results, or text wrapping.")
        signature = (digest, tuple(ranges.items()), tuple(options.items()))
        if st.button("Clean all sheets" if all_sheets else "Clean selected sheets", type="primary", width="stretch", key="clean_workbook", icon=":material/auto_fix_high:"):
            with st.spinner("Cleaning workbook values…"):
                export, reports = clean_workbook(source, ranges, options, clean_phone)
                st.session_state['_workbook_result'] = (signature, export, reports)
        saved = st.session_state.get('_workbook_result')
        with progress.container():
            render_steps(2 if saved is not None and saved[0] == signature else 1)
        if saved is None or saved[0] != signature:
            if saved is not None:
                st.info("Your selection or rules changed. Clean the workbook again to update the preview and download.")
            render_policies()
            return
        _, export, reports = saved
        heading, action = st.columns([2, 1.5], vertical_alignment="center")
        with heading:
            st.markdown('<h2>Review your workbook</h2>', unsafe_allow_html=True)
            st.caption("Check the cleaned values before using them in a business system.")
        with action:
            st.download_button("Export cleaned Excel workbook", data=export, file_name=f"{Path(filename).stem}_cleaned.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", width="stretch", on_click="ignore", icon=":material/download:")
        workbook_summary(reports)
        summary = pd.DataFrame([{'Sheet': name, 'Text cells changed': r['changed'], 'Duplicate rows flagged': len(r['duplicates']), 'Blank cells flagged': len(r['missing'])} for name, r in reports.items()])
        with st.expander("Summary by sheet"):
            st.dataframe(summary, width="stretch", hide_index=True)
        with st.container(key="review_surface"):
            current = st.selectbox("Sheet to review", chosen, key=f"review_sheet_{digest}")
            report = reports[current]
            cleaned, original, changes, gaps, duplicates = st.tabs(["Cleaned data", "Original data", "Change log", f"Missing values ({len(report['missing']):,})", f"Duplicate rows ({len(report['duplicates']):,})"])
            with original:
                st.dataframe(report['original'].head(250), width="stretch")
                st.caption("The values before cleaning. Excel row numbers match the original workbook.")
            with cleaned:
                st.dataframe(report['cleaned'].head(250), width="stretch")
                st.caption("Showing up to 250 rows. This value preview does not display Excel styles. Numeric dates may appear as serial values here; the download keeps their original date formats.")
            with changes:
                if report['log'].empty:
                    st.success("No text changes were needed with the selected rules.")
                else:
                    st.dataframe(report['log'].head(500), width="stretch", hide_index=True)
                st.caption(f"{report['changed']:,} text cells changed · {report['skipped']:,} nonempty cells retained as protected or non-plain-text content. Showing up to 500 changes.")
            with gaps:
                if report['missing'].empty:
                    st.success("No missing values in this range.")
                else:
                    st.dataframe(report['missing'].head(500), width="stretch", hide_index=True)
                    st.caption("Missing cells are left blank. Showing up to 500 gaps.")
            with duplicates:
                if report['duplicates'].empty:
                    st.success("No duplicate rows in this range.")
                else:
                    st.dataframe(report['duplicates'].head(500), width="stretch", hide_index=True)
                st.caption("Duplicates match all values in the selected range after cleaning. Formula expressions are compared as text. Rows stay in their original positions in the export.")
        st.markdown('<div class="workspace-footer"><span>Original workbook preserved</span><span>Export includes every original sheet</span></div>', unsafe_allow_html=True)
        render_policies()
    except (ValueError, KeyError, IndexError, zipfile.BadZipFile, ParseError) as exc:
        st.error(f"The workbook could not be safely processed: {exc}")
        st.caption("Use an ordinary, unencrypted .xlsx workbook and check the selected data ranges.")
        render_policies()


def main():
    st.set_page_config(page_title="OpsClean · Viv’s Operations Cleaner", page_icon=str(Path(__file__).parent / "favicon.png"), layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.session_state.setdefault("source", "upload")
    render_masthead()
    has_source = st.session_state["source"] == "sample" or st.session_state.get("uploaded_csv") is not None
    if not has_source:
        render_steps(0)
        intro, source = st.columns([1.05, 1.15], gap="large", vertical_alignment="center")
        with intro:
            render_intro()
        with source:
            with st.container(key="source_panel"):
                uploaded, encoding_label, separator = render_import()
        st.markdown("""
        <div class="empty-footer">
          <div> <strong>Bring your operations data</strong><p>Upload a CSV, TSV, or Excel workbook from your spreadsheet, form, or CRM.</p></div>
          <div> <strong>Choose what changes</strong><p>Set your cleaning rules. For Excel, choose the sheets and data ranges to review.</p></div>
          <div> <strong>Review, then export</strong><p>Compare the original and cleaned data, check missing values, and download your file.</p></div>
        </div>
        """, unsafe_allow_html=True)
        render_policies()
        return
    with st.expander("Source & import settings", icon=":material/upload_file:"):
        uploaded, encoding_label, separator = render_import(compact=True)
    options = {key: st.session_state.get(f"rule_{key}", True) for key, _, _ in RULES}

    sample = st.session_state["source"] == "sample"
    if not sample and uploaded is None:
        st.rerun()
        return

    raw = SAMPLE_CSV.encode("utf-8") if sample else uploaded.getvalue()
    filename = "sample_operations_data.csv" if sample else uploaded.name
    if Path(filename).suffix.lower() == ".xlsx":
        render_workbook(raw, filename)
        return
    encoding = "utf-8-sig" if sample else {"UTF-8": "utf-8-sig", "Windows-1252": "cp1252", "UTF-16": "utf-16"}[encoding_label]
    delimiter_choice = "Comma" if sample else separator
    signature = (hashlib.sha256(raw).hexdigest(), Path(filename).suffix.lower(), encoding, delimiter_choice)

    try:
        if st.session_state.get("_source_signature") != signature:
            original = read_csv(raw, encoding, delimiter_choice, filename)
            st.session_state["_original"] = original
            st.session_state["_source_signature"] = signature
        original = st.session_state["_original"]
    except UnicodeError:
        st.title("Check the file encoding")
        st.error("This file could not be read using the selected encoding. Open Source & import settings, then try Windows-1252 or UTF-16, or save your file as CSV UTF-8.")
        render_policies()
        return
    except pd.errors.EmptyDataError:
        st.title("This file is empty")
        st.error("Upload a CSV or TSV with a header row and at least one data row, or try the sample dataset.")
        render_policies()
        return
    except (pd.errors.ParserError, ValueError):
        st.title("Check the file format")
        st.error("Some rows could not be read. Check the column separator in Source & import settings, or export the source file again. No rows were skipped.")
        render_policies()
        return

    if original.empty:
        st.title("No data rows found")
        st.info("This file contains column names but no data. Upload a file with at least one data row, or use the sample.")
        render_policies()
        return

    result_key = (signature, tuple(options.items()))
    if st.session_state.get("_result_key") != result_key:
        with st.spinner("Preparing your dataset…"):
            cleaned, report = clean_dataframe(original, options)
            st.session_state["_result"] = (cleaned, report, cleaned.to_csv(index=False).encode("utf-8-sig"))
            st.session_state["_result_key"] = result_key
    cleaned, report, export = st.session_state["_result"]

    render_steps(2)
    heading, action = st.columns([3, 1.4], vertical_alignment="center")
    with heading:
        st.title("Review Dataset")
        tag = '<span class="sample-label">Sample data</span>' if sample else ""
        st.markdown(f'<div class="file-line"><span class="file-name">{html.escape(filename)}</span>{tag}<span> {len(original.columns):,} columns</span></div>', unsafe_allow_html=True)
    with action:
        st.download_button("Export cleaned CSV", data=export, file_name=f"{Path(filename).stem}_cleaned.csv", mime="text/csv", type="primary", width="stretch", icon=":material/download:", on_click="ignore")

    csv_summary(report)

    if report["missing_cells"]:
        st.markdown('<div class="review-note"><b>A few gaps to review</b><span>Missing values are left blank. Check the Missing values tab before you export.</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="review-note clear"><b>No missing values</b><span>Review the cleaned data before exporting. Values have not been validated for accuracy.</span></div>', unsafe_allow_html=True)
    if report["duplicates_remaining"]:
        st.caption(f"{report['duplicates_remaining']:,} duplicate rows remain because duplicate removal is off.")

    with st.expander(f"Cleaning rules {sum(options.values())} active", icon=":material/tune:"):
        st.button("Reset to recommended rules", key="reset_rules", type="tertiary", on_click=reset_rules)
        st.caption("Updates apply immediately. Blank cells are always treated as missing.")
        rule_columns = st.columns(2)
        for index, (key, label, help_text) in enumerate(RULES):
            with rule_columns[index % 2]:
                st.checkbox(label, value=None if f"rule_{key}" in st.session_state else True, key=f"rule_{key}", help=help_text)
    with st.container(key="review_surface"):
        cleaned_tab, original_tab, changes_tab, missing_tab = st.tabs(["Cleaned data", "Original data", "Change log", f"Missing values ({report['missing_cells']:,})"])

        with cleaned_tab:
            search_col, filter_col = st.columns([2.3, 1])
            with search_col:
                query = st.text_input("Search cleaned data", placeholder="Search any value…", key="cleaned_search", icon=":material/search:")
            with filter_col:
                row_view = st.selectbox("Rows to show", ["All rows", "Rows with missing values"], key="cleaned_filter")
            display_table(cleaned, "cleaned_preview", query=query, only_missing=row_view != "All rows")

        with original_tab:
            st.caption("The imported data before cleaning. Identifiers, leading zeros, and text formatting are preserved.")
            display_table(original, "original_preview")

        with changes_tab:
            st.caption("Counts show changes made by each rule. One value can be affected by more than one rule; Values updated counts each cell once before removing duplicates.")
            st.dataframe(report["log"], width="stretch", hide_index=True, row_height=42)
            st.caption("Duplicates are compared after cleaning. Blank and whitespace-only cells are treated as missing.")
            with st.expander(f"Column names · {report['columns_standardized']:,} changed"):
                st.dataframe(report["column_map"], width="stretch", hide_index=True)

        with missing_tab:
            if report["missing_table"].empty:
                st.success("No missing values in the cleaned dataset.")
            else:
                st.caption(f"{report['missing_cells']:,} empty cells across {len(report['missing_table']):,} columns. These values are not filled automatically.")
                st.dataframe(report["missing_table"], width="stretch", hide_index=True, row_height=42, column_config={"Missing cells": st.column_config.NumberColumn(format="%d"), "Share of rows": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%")})
                st.caption("To inspect the affected rows, choose Rows with missing values in the Cleaned data tab.")
    st.markdown(f'<div class="workspace-footer"><span>{sum(options.values())} of {len(RULES)} cleaning rules enabled</span><span>Original preserved · Export contains all cleaned rows</span></div>', unsafe_allow_html=True)
    render_policies()


if __name__ == "__main__":
    main()
