"""OpsClean presentation helpers; cleaning and exports stay in their own modules."""

import html
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


ROOT = Path(__file__).resolve().parent
CSS = "<style>" + (ROOT / "assets" / "opsclean.css").read_text(encoding="utf-8") + "</style>"
_summary = components.declare_component("opsclean_summary", path=str(ROOT / "components" / "summary"))


def render_steps(stage):
    """A non-interactive orientation cue; the controls remain native Streamlit widgets."""
    names = ["Import", "Choose rules", "Review & export"]
    items = []
    for index, name in enumerate(names):
        state = "current" if index == stage else "complete" if index < stage else "waiting"
        current = ' aria-current="step"' if index == stage else ""
        items.append(f'<li class="{state}"{current}><span class="step-number" aria-hidden="true">{index + 1}</span>{html.escape(name)}</li>')
    st.markdown('<nav class="workflow" aria-label="Cleaning steps"><ol>' + "".join(items) + "</ol></nav>", unsafe_allow_html=True)


def render_summary(stats, key):
    """Only aggregate counts enter this component, never uploaded cell contents.

    The vendored Anime.js bundle needs no CDN or JavaScript build step. The
    iframe resizes to its content and follows the device's reduced-motion setting.
    """
    items = [dict(value=f"{int(value):,}", label=label, detail=detail, warning=warning)
             for value, label, detail, warning in stats]
    _summary(items=items, key=key, default=None)


def csv_summary(report):
    render_summary([
        (report["cleaned_rows"], "Rows to export", f'from {report["original_rows"]:,} source rows', False),
        (report["edited_cells"], "Values updated", "each changed cell counted once", False),
        (report["duplicates_removed"], "Duplicates removed", "first occurrence kept", False),
        (report["missing_cells"], "Missing cells", f'in {report["missing_rows"]:,} cleaned rows', report["missing_cells"] > 0),
    ], key="csv_summary")


def workbook_summary(reports):
    changed = sum(report["changed"] for report in reports.values())
    duplicates = sum(len(report["duplicates"]) for report in reports.values())
    missing = sum(len(report["missing"]) for report in reports.values())
    render_summary([
        (len(reports), "Sheets reviewed", "all original sheets in the export", False),
        (changed, "Text cells updated", "within your selected ranges", False),
        (duplicates, "Duplicates flagged", "rows kept in their original places", duplicates > 0),
        (missing, "Missing cells", "left blank for your review", missing > 0),
    ], key="workbook_summary")
