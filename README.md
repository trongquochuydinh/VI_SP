# Attendance Operational Dashboard

This project is a Dash + Plotly dashboard tailored to your prepared attendance dataset.

## Data Source

Place your prepared workbook in the **bin subdirectory** and use the default name below (the path is resolved relative to the shell's current working directory, so run `python src/run.py` from the repo root after you add the file). If the file is missing or not a readable Excel workbook, the dashboard still starts using a **small built-in demo dataset**—replace the file with your real export to see your cohort.

- **Default file:** `attendance_merged_evaluated_only.xlsx` (not tracked in git; add it locally)
- **Default sheet:** `attendance`
- Main columns used:
  - grouping/filtering: `academic_year`, `class`, `day`, `exam_attempt`
  - attendance signal: `week_1` ... `week_13`, `total_attendance`
  - outcomes/qa context: `final_grade`, `final_points`

## What the app shows

- Filters for academic year, class, day, exam attempt, and attendance range.
- KPI cards for:
  - unique students in current slice
  - average attendance
  - exam participation rate
  - displayed rows vs total rows
- Available views (selectable from the **View** dropdown):
  - **Attendance vs Final Grade** — distribution of attendance per grade category (`total_attendance` vs `final_grade`).
  - **Attendance Distribution** — how attendance counts are spread across students.
  - **Exam Attempts vs Attendance** — attendance broken down by number of exam attempts; direct test of the hypothesis that attendees need fewer attempts.
  - **Pass Rate by Attendance Bracket** — students bucketed into attendance brackets (0-3, 4-6, 7-9, 10-13) and split into *Passed 1st attempt / Passed (multiple attempts) / Did not pass*. Aggregated per `student_id`.
  - **Final Points vs Attendance (trendline)** — scatter of `final_points` against attendance with an OLS regression line (slope + R² in the legend, computed via `numpy.polyfit`, no extra dependency).
- Chart type selector: **scatter**, **box**, **line**, **bar**. Each view declares which chart types it supports; unsupported selections fall back to the view's preferred type.
- Passing-grade definition (used by the Pass Rate view): `{1, 2, 3, 4, S}` — `S` ("Splnené") is treated as a pass for pass/fail-style records; `N` is treated as failing.

### Per-view defaults (auto-applied on view change)

When the view is switched, the chart type, academic year, exam-attempt, and class filters are snapped to defaults that make each view immediately readable. The user can still override them afterward.

| View | Chart type | Years | Exam attempts | Classes |
|---|---|---|---|---|
| Attendance vs Final Grade | box | all | all | all |
| Attendance Distribution | line | all | all | largest class |
| Exam Attempts vs Attendance | box | latest only | exclude `Missing` | all |
| Pass Rate by Attendance Bracket | bar | all | all | all |
| Final Points vs Attendance | scatter | latest only | exclude `Missing` | largest class with non-null `final_points` |

"Largest class" is recomputed from the loaded data, so it adapts to whatever dataset is dropped in.

## Architecture in `src`

- `run.py`: entry point for local run.
- `app.py`: creates Dash app and wires layout + callbacks.
- `layout.py`: dashboard UI and default filter state.
- `callbacks.py`: reactive filtering and chart/KPI updates.
- `helpers.py`: data loading, preprocessing, filtering, metrics, and figure builders.
- `constants.py`: shared component IDs, view keys, and defaults.

## Run locally

1. Check python version (>=3.9):
```bash
python --version
```

2. Make a virtual environment:
```bash
python -m venv venv
source venv/bin/activate (for Unix)
venv\Scripts\activate (for Windows)
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the app (ensure `attendance_merged_evaluated_only.xlsx` is in the `bin` subdirectory if you want live data; see **Data Source** above):

```bash
python src/run.py
```

Then open the local Dash URL shown in your terminal.
