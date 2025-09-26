#!/usr/bin/env python3
"""
ipl_analysis_report.py

Purpose:
    - Read an IPL team-aggregated CSV (one row per team: columns such as 'team','played','won','losses','no_results').
    - Compute derived metrics (win_pct, points, rank), create charts, and write an Excel report with a Dashboard.
    - Uses pandas + XlsxWriter for Excel output and charts.

Usage:
    1. Install dependencies:
       pip install pandas xlsxwriter matplotlib openpyxl

    2. Configure the `input_csv` and `output_xlsx` paths below.

    3. Run:
       python ipl_analysis_report.py
"""

import pathlib
import pandas as pd
import numpy as np

# ---------- Utility functions ----------
def num_to_col(n: int) -> str:
    """Convert 1-indexed column number to Excel column letters (e.g. 1 -> 'A', 27 -> 'AA')."""
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

# ---------- Main processing ----------
def run(input_csv: str, output_xlsx: str):
    input_path = pathlib.Path(input_csv)
    output_path = pathlib.Path(output_xlsx)

    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    # 1) Read CSV
    df = pd.read_csv(input_path)
    df.columns = [c.strip() for c in df.columns]

    # 2) Convert numeric columns
    for col in ["played", "won", "losses", "no_results"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 3) Derived metrics
    if ("played" in df.columns) and ("won" in df.columns):
        df["win_pct"] = df["won"] / df["played"]
    else:
        df["win_pct"] = np.nan

    df["points"] = df["won"] * 2 + df.get("no_results", 0).fillna(0).astype(int)
    df["rank_by_wins"] = df["won"].rank(method="min", ascending=False).astype(int)
    summary = df.sort_values(["won", "win_pct"], ascending=[False, False]).reset_index(drop=True)

    # 4) Write Excel + Dashboard
    with pd.ExcelWriter(output_path, engine="xlsxwriter", date_format="yyyy-mm-dd", datetime_format="yyyy-mm-dd") as writer:
        df.to_excel(writer, sheet_name="Raw_Data", index=False)
        summary.to_excel(writer, sheet_name="Summary", index=False)

        workbook = writer.book

        # Hidden sheet for dropdown list
        lists = workbook.add_worksheet("Lists")
        lists.hide()
        teams = summary["team"].tolist() if "team" in summary.columns else []
        lists.write_column(0, 0, teams)
        workbook.define_name("TeamList", f"=Lists!$A$1:$A${len(teams) if teams else 1}")

        # Dashboard sheet
        dash = workbook.add_worksheet("Dashboard")
        dash.write(0, 0, "IPL Team Analysis Dashboard")

        dash.write(2, 0, "Select Team:")
        dash.data_validation(2, 1, 2, 1, {"validate": "list", "source": "=TeamList"})
        dash.write(4, 0, "Selected team:")
        dash.write_formula(4, 1, "=$B$3")

        # KPIs
        cols = list(summary.columns)
        col_letters = {c: num_to_col(i + 1) for i, c in enumerate(cols)}
        raw_sheet = "Summary"

        kpi_start_row = 6
        dash.write(kpi_start_row, 0, "KPI")
        dash.write(kpi_start_row, 1, "Value")
        kpis = [
            ("Wins", "won"),
            ("Losses", "losses"),
            ("No Results", "no_results" if "no_results" in summary.columns else None),
            ("Win %", "win_pct"),
            ("Points", "points"),
        ]

        for i, (label, col) in enumerate(kpis):
            dash.write(kpi_start_row + 1 + i, 0, label)
            if col is None:
                dash.write(kpi_start_row + 1 + i, 1, "N/A")
            else:
                excel_col = col_letters[col]
                formula = f"=IFERROR(INDEX(Summary!${excel_col}:${excel_col}, MATCH($B$3, Summary!$A:$A, 0)), \"\")"
                dash.write_formula(kpi_start_row + 1 + i, 1, formula)

        # Charts
        n = len(summary)
        if n > 0:
            # Wins by Team
            chart1 = workbook.add_chart({"type": "column"})
            chart1.add_series({
                "name": "Wins",
                "categories": f"=Summary!$A$2:$A${n+1}",
                "values": f"=Summary!$C$2:$C${n+1}"
            })
            chart1.set_title({"name": "Wins by Team"})
            dash.insert_chart(12, 0, chart1, {"x_scale": 1.2, "y_scale": 1.0})

            # Win % by Team
            if "win_pct" in col_letters:
                chart2 = workbook.add_chart({"type": "column"})
                chart2.add_series({
                    "name": "Win %",
                    "categories": f"=Summary!$A$2:$A${n+1}",
                    "values": f"=Summary!${col_letters['win_pct']}$2:${col_letters['win_pct']}${n+1}"
                })
                chart2.set_title({"name": "Win Percentage by Team"})
                dash.insert_chart(12, 8, chart2, {"x_scale": 1.2, "y_scale": 1.0})

    print(f"Excel report written to: {output_path.resolve()}")

# ---------- Configure paths here ----------
if __name__ == "__main__":
    input_csv = "ipl_win_lose.csv"
    output_xlsx = "ipl_analysis_dashboard_new.xlsx"
    run(input_csv, output_xlsx)
