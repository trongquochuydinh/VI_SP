from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from constants import (
    CHART_TYPE_BAR,
    CHART_TYPE_BOX,
    CHART_TYPE_LINE,
    CHART_TYPE_SCATTER,
    DEFAULT_DATA_FILE,
    DEFAULT_SHEET_NAME,
    VIEW_ATTEMPTS_VS_ATTENDANCE,
    VIEW_ATTENDANCE_DISTRIBUTION,
    VIEW_ATTENDANCE_EXAM_CORRELATION,
    VIEW_PASS_RATE_BY_BRACKET,
    VIEW_POINTS_VS_ATTENDANCE,
)

PASSING_GRADES = {"1", "2", "3", "4", "S"}
ATTENDANCE_BRACKET_ORDER = ["0-3", "4-6", "7-9", "10-13"]
OUTCOME_ORDER = ["Passed 1st attempt", "Passed (multiple attempts)", "Did not pass"]


@dataclass(frozen=True)
class ChartSpec:
    df: pd.DataFrame
    x: str | None
    y: str | None
    title: str
    labels: dict[str, str]
    color: str | None = None
    size: str | None = None
    hover_data: list[str] | None = None
    markers: bool | None = None
    opacity: float | None = None
    trendline: bool = False
    category_orders: dict | None = None
    barmode: str | None = None


@dataclass(frozen=True)
class ViewSpec:
    by_chart_type: dict[str, ChartSpec]


def load_data(file_path: str | None = None, sheet_name: str = DEFAULT_SHEET_NAME) -> pd.DataFrame:
    target = Path(file_path or DEFAULT_DATA_FILE)
    if target.exists() and target.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(target, sheet_name=sheet_name)
    elif target.exists() and target.suffix.lower() == ".csv":
        df = pd.read_csv(target)
    else:
        # Fallback when file read failed or file is not found
        df = build_demo_data()
    return preprocess_attendance_data(df)


# Fallback function to generate demo data
def build_demo_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "academic_year": ["2024/2025", "2024/2025", "2024/2025"],
            "day": ["Monday", "Wednesday", "Friday"],
            "student_id": ["D001", "D002", "D003"],
            "week_1": [1, 1, 0],
            "week_2": [1, 0, 0],
            "week_3": [1, 1, 1],
            "week_4": [1, 1, 1],
            "week_5": [1, 1, 0],
            "week_6": [1, 0, 1],
            "week_7": [1, 1, 1],
            "week_8": [1, 1, 1],
            "week_9": [1, 1, 1],
            "week_10": [1, 1, 0],
            "week_11": [1, 1, 1],
            "week_12": [1, 0, 1],
            "week_13": [1, 1, 1],
            "total_attendance": [13, 10, 9],
            "exam_attempt": [1, 1, 0],
            "final_grade": ["2", "3", "S"],
            "final_points": [78.0, 61.0, None],
            "class": ["IT1", "IT2", "IT1"],
        }
    )


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    clean.columns = [str(col).strip() for col in clean.columns]
    return clean


def week_columns(df: pd.DataFrame) -> list[str]:
    candidates = [str(c) for c in df.columns if str(c).startswith("week_")]
    return sorted(candidates, key=lambda c: int(c.split("_")[1]))


def preprocess_attendance_data(df: pd.DataFrame) -> pd.DataFrame:
    clean = normalize_columns(df)
    for col in ["academic_year", "day", "student_id", "class"]:
        if col in clean.columns:
            clean[col] = clean[col].astype(str).str.strip()

    if "final_grade" in clean.columns:
        clean["final_grade"] = clean["final_grade"].astype(str).str.strip().str.upper()

    if "exam_attempt" in clean.columns:
        numeric_attempt = pd.to_numeric(clean["exam_attempt"], errors="coerce")
        clean["exam_attempt"] = numeric_attempt.astype("Int64")
        clean["exam_attempt_label"] = clean["exam_attempt"].astype(str).replace("<NA>", "Missing")
    else:
        clean["exam_attempt"] = pd.Series([pd.NA] * len(clean), dtype="Int64")
        clean["exam_attempt_label"] = "Missing"

    weeks = week_columns(clean)
    if weeks:
        clean[weeks] = clean[weeks].apply(pd.to_numeric, errors="coerce").fillna(0).astype(int)
        clean["attendance_from_weeks"] = clean[weeks].sum(axis=1)
        if "total_attendance" in clean.columns:
            clean["total_attendance"] = pd.to_numeric(clean["total_attendance"], errors="coerce").fillna(0).astype(int)
        else:
            clean["total_attendance"] = clean["attendance_from_weeks"]
        clean["attendance_total_mismatch"] = clean["attendance_from_weeks"] != clean["total_attendance"]
        clean["attendance_rate"] = clean["total_attendance"] / len(weeks)
    else:
        clean["attendance_from_weeks"] = 0
        clean["total_attendance"] = pd.to_numeric(clean.get("total_attendance", 0), errors="coerce").fillna(0).astype(int)
        clean["attendance_total_mismatch"] = False
        clean["attendance_rate"] = 0.0

    if "final_points" in clean.columns:
        clean["final_points"] = pd.to_numeric(clean["final_points"], errors="coerce")

    clean["took_exam"] = clean["exam_attempt"].fillna(0) > 0
    return clean


def dataframe_to_records(df: pd.DataFrame) -> list[dict]:
    return df.to_dict("records")


def records_to_dataframe(records: list[dict] | None) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


def filter_attendance(
    df: pd.DataFrame,
    years: list[str] | None,
    classes: list[str] | None,
    days: list[str] | None,
    exam_attempts: list[str] | None,
    attendance_range: list[int] | None,
) -> pd.DataFrame:
    if df.empty:
        return df

    filtered = df.copy()
    if years:
        filtered = filtered[filtered["academic_year"].isin(years)]
    if classes:
        filtered = filtered[filtered["class"].isin(classes)]
    if days:
        filtered = filtered[filtered["day"].isin(days)]
    if exam_attempts:
        filtered = filtered[filtered["exam_attempt_label"].isin(exam_attempts)]

    if attendance_range and len(attendance_range) == 2:
        lo, hi = attendance_range
        filtered = filtered[filtered["total_attendance"].between(lo, hi)]

    return filtered


def unique_options(df: pd.DataFrame, column: str) -> list[dict]:
    if column not in df.columns:
        return []
    values = sorted([str(v) for v in df[column].dropna().unique()])
    return [{"label": v, "value": v} for v in values]


def build_kpis(df_filtered: pd.DataFrame, df_all: pd.DataFrame) -> tuple[str, str, str, str]:
    total_rows = len(df_all)
    shown_rows = len(df_filtered)
    avg_attendance = df_filtered["total_attendance"].mean() if shown_rows else 0
    participation = df_filtered["took_exam"].mean() * 100 if shown_rows else 0

    students_text = f"{df_filtered['student_id'].nunique():,} students"
    attendance_text = f"{avg_attendance:.2f} / 13 avg attendance"
    participation_text = f"{participation:.1f}% exam participation"
    displayed_text = f"{shown_rows:,} / {total_rows:,} rows shown"
    return students_text, attendance_text, participation_text, displayed_text


def _empty_figure(message: str):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 16},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(template="plotly_white", margin={"l": 24, "r": 24, "t": 60, "b": 24})
    return fig


def _final_grade_frame(df: pd.DataFrame) -> pd.DataFrame:
    if "final_grade" not in df.columns:
        return pd.DataFrame()
    graded = df.copy()
    graded["final_grade"] = graded["final_grade"].astype(str).str.strip().str.upper()
    graded = graded[~graded["final_grade"].isin(["", "NAN", "NONE"])]
    if graded.empty:
        return graded
    order = ["1", "2", "3", "4", "N", "S"]
    existing_order = [g for g in order if g in set(graded["final_grade"])]
    if existing_order:
        graded["final_grade"] = pd.Categorical(graded["final_grade"], categories=existing_order, ordered=True)
        graded = graded.sort_values("final_grade")
    return graded


def prepare_attendance_vs_grade(df: pd.DataFrame) -> ViewSpec:
    graded = _final_grade_frame(df)
    if graded.empty:
        raise ValueError("No final_grade data available for selected filters")

    grouped = (
        graded.groupby("final_grade", as_index=False)
        .agg(avg_attendance=("total_attendance", "mean"), rows=("student_id", "count"))
    )

    return ViewSpec(
        by_chart_type={
            CHART_TYPE_BOX: ChartSpec(
                df=graded,
                x="final_grade",
                y="total_attendance",
                title="Attendance vs Final Grade",
                labels={
                    "total_attendance": "Total attendance (0-13)",
                    "final_grade": "Final grade",
                },
            ),
            CHART_TYPE_LINE: ChartSpec(
                df=grouped,
                x="final_grade",
                y="avg_attendance",
                title="Attendance vs Final Grade",
                labels={
                    "final_grade": "Final grade",
                    "avg_attendance": "Average attendance",
                },
                markers=True,
                hover_data=["rows"],
            ),
            CHART_TYPE_SCATTER: ChartSpec(
                df=graded,
                x="total_attendance",
                y="final_grade",
                title="Attendance vs Final Grade",
                labels={
                    "total_attendance": "Total attendance (0-13)",
                    "final_grade": "Final grade",
                    "class": "Class",
                },
                color="class",
                opacity=0.7,
            ),
        }
    )


def prepare_attendance_distribution(df: pd.DataFrame) -> ViewSpec:
    grouped = (
        df.groupby("total_attendance", as_index=False)
        .agg(rows=("student_id", "count"))
        .sort_values("total_attendance")
    )

    return ViewSpec(
        by_chart_type={
            CHART_TYPE_BOX: ChartSpec(
                df=df,
                x=None,
                y="total_attendance",
                title="Attendance Distribution",
                labels={"total_attendance": "Total attendance (0-13)"},
            ),
            CHART_TYPE_LINE: ChartSpec(
                df=grouped,
                x="total_attendance",
                y="rows",
                title="Attendance Distribution",
                labels={
                    "total_attendance": "Total attendance (0-13)",
                    "rows": "Students",
                },
                markers=True,
            ),
            CHART_TYPE_SCATTER: ChartSpec(
                df=grouped,
                x="total_attendance",
                y="rows",
                title="Attendance Distribution",
                labels={
                    "total_attendance": "Total attendance (0-13)",
                    "rows": "Students",
                },
                size="rows",
            ),
        }
    )


def _attendance_bracket(attendance: int) -> str:
    if attendance <= 3:
        return "0-3"
    if attendance <= 6:
        return "4-6"
    if attendance <= 9:
        return "7-9"
    return "10-13"


def _student_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    if "student_id" not in df.columns or "final_grade" not in df.columns:
        return pd.DataFrame()

    work = df.copy()
    work["final_grade"] = work["final_grade"].astype(str).str.strip().str.upper()
    work["is_pass"] = work["final_grade"].isin(PASSING_GRADES)
    work["attempt_num"] = pd.to_numeric(work["exam_attempt"], errors="coerce")

    rows = []
    for student_id, group in work.groupby("student_id"):
        attendance = int(group["total_attendance"].max())
        passed = group[group["is_pass"]]
        if passed.empty:
            outcome = "Did not pass"
        else:
            min_attempt = passed["attempt_num"].min()
            if pd.isna(min_attempt) or int(min_attempt) != 1:
                outcome = "Passed (multiple attempts)"
            else:
                outcome = "Passed 1st attempt"
        rows.append({"student_id": student_id, "total_attendance": attendance, "outcome": outcome})

    return pd.DataFrame(rows)


def prepare_attempts_vs_attendance(df: pd.DataFrame) -> ViewSpec:
    work = df.copy()
    work["exam_attempt_num"] = pd.to_numeric(work["exam_attempt"], errors="coerce")
    work = work[work["exam_attempt_num"] > 0].copy()
    if work.empty:
        raise ValueError("No exam-attempt data for selected filters")
    work["exam_attempt_num"] = work["exam_attempt_num"].astype(int)
    work["attempt_label"] = work["exam_attempt_num"].astype(str)

    grouped = (
        work.groupby("exam_attempt_num", as_index=False)
        .agg(avg_attendance=("total_attendance", "mean"), rows=("student_id", "count"))
        .sort_values("exam_attempt_num")
    )

    attempt_order = sorted(work["attempt_label"].unique(), key=int)

    return ViewSpec(
        by_chart_type={
            CHART_TYPE_BOX: ChartSpec(
                df=work,
                x="attempt_label",
                y="total_attendance",
                title="Attendance by number of exam attempts",
                labels={
                    "attempt_label": "Exam attempt #",
                    "total_attendance": "Total attendance (0-13)",
                },
                category_orders={"attempt_label": attempt_order},
            ),
            CHART_TYPE_LINE: ChartSpec(
                df=grouped,
                x="exam_attempt_num",
                y="avg_attendance",
                title="Average attendance by number of exam attempts",
                labels={
                    "exam_attempt_num": "Exam attempt #",
                    "avg_attendance": "Average attendance",
                },
                markers=True,
                hover_data=["rows"],
            ),
            CHART_TYPE_SCATTER: ChartSpec(
                df=work,
                x="exam_attempt_num",
                y="total_attendance",
                title="Attendance by number of exam attempts",
                labels={
                    "exam_attempt_num": "Exam attempt #",
                    "total_attendance": "Total attendance (0-13)",
                    "class": "Class",
                },
                color="class",
                opacity=0.7,
            ),
        }
    )


def prepare_pass_rate_by_bracket(df: pd.DataFrame) -> ViewSpec:
    students = _student_outcomes(df)
    if students.empty:
        raise ValueError("No student outcome data for selected filters")

    students["bracket"] = students["total_attendance"].apply(_attendance_bracket)

    counts = students.groupby(["bracket", "outcome"]).size().reset_index(name="count")
    totals = students.groupby("bracket").size().reset_index(name="total")
    merged = counts.merge(totals, on="bracket")
    merged["percent"] = merged["count"] / merged["total"] * 100

    full_index = pd.MultiIndex.from_product(
        [ATTENDANCE_BRACKET_ORDER, OUTCOME_ORDER], names=["bracket", "outcome"]
    )
    merged = (
        merged.set_index(["bracket", "outcome"])
        .reindex(full_index, fill_value=0)
        .reset_index()
    )
    merged["bracket"] = pd.Categorical(merged["bracket"], categories=ATTENDANCE_BRACKET_ORDER, ordered=True)
    merged["outcome"] = pd.Categorical(merged["outcome"], categories=OUTCOME_ORDER, ordered=True)
    merged = merged.sort_values(["bracket", "outcome"])

    common_labels = {
        "bracket": "Attendance bracket (weeks attended)",
        "percent": "Students (%)",
        "outcome": "Outcome",
    }
    category_orders = {"bracket": ATTENDANCE_BRACKET_ORDER, "outcome": OUTCOME_ORDER}

    return ViewSpec(
        by_chart_type={
            CHART_TYPE_BAR: ChartSpec(
                df=merged,
                x="bracket",
                y="percent",
                color="outcome",
                title="Pass rate by attendance bracket",
                labels=common_labels,
                hover_data=["count", "total"],
                category_orders=category_orders,
                barmode="group",
            ),
            CHART_TYPE_LINE: ChartSpec(
                df=merged,
                x="bracket",
                y="percent",
                color="outcome",
                title="Pass rate by attendance bracket",
                labels=common_labels,
                hover_data=["count", "total"],
                markers=True,
                category_orders=category_orders,
            ),
        }
    )


def prepare_points_vs_attendance(df: pd.DataFrame) -> ViewSpec:
    if "final_points" not in df.columns:
        raise ValueError("No final_points column available")

    work = df.dropna(subset=["final_points"]).copy()
    if work.empty:
        raise ValueError("No final_points data for selected filters")

    grouped = (
        work.groupby("total_attendance", as_index=False)
        .agg(avg_points=("final_points", "mean"), rows=("student_id", "count"))
        .sort_values("total_attendance")
    )

    return ViewSpec(
        by_chart_type={
            CHART_TYPE_SCATTER: ChartSpec(
                df=work,
                x="total_attendance",
                y="final_points",
                title="Final points vs attendance (with OLS trendline)",
                labels={
                    "total_attendance": "Total attendance (0-13)",
                    "final_points": "Final points",
                    "class": "Class",
                },
                color="class",
                opacity=0.7,
                trendline=True,
            ),
            CHART_TYPE_BOX: ChartSpec(
                df=work,
                x="total_attendance",
                y="final_points",
                title="Final points distribution by attendance",
                labels={
                    "total_attendance": "Total attendance (0-13)",
                    "final_points": "Final points",
                },
            ),
            CHART_TYPE_LINE: ChartSpec(
                df=grouped,
                x="total_attendance",
                y="avg_points",
                title="Average final points by attendance",
                labels={
                    "total_attendance": "Total attendance (0-13)",
                    "avg_points": "Average final points",
                },
                markers=True,
                hover_data=["rows"],
            ),
        }
    )


def _add_ols_trendline(fig: go.Figure, spec: ChartSpec) -> None:
    if not (spec.x and spec.y):
        return
    x_vals = pd.to_numeric(spec.df[spec.x], errors="coerce")
    y_vals = pd.to_numeric(spec.df[spec.y], errors="coerce")
    mask = x_vals.notna() & y_vals.notna()
    if mask.sum() < 2:
        return
    x = x_vals[mask].to_numpy(dtype=float)
    y = y_vals[mask].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    x_line = np.array([x.min(), x.max()])
    y_line = slope * x_line + intercept
    y_pred = slope * x + intercept
    ss_res = float(((y - y_pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            name=f"OLS (slope={slope:.2f}, R²={r2:.2f})",
            line={"color": "black", "dash": "dash"},
        )
    )


def build_chart(spec: ChartSpec, chart_type: str) -> go.Figure:
    renderer = {
        CHART_TYPE_SCATTER: px.scatter,
        CHART_TYPE_BOX: px.box,
        CHART_TYPE_LINE: px.line,
        CHART_TYPE_BAR: px.bar,
    }.get(chart_type, px.scatter)

    kwargs: dict[str, object] = {
        "data_frame": spec.df,
        "title": spec.title,
        "labels": spec.labels,
    }
    if spec.x is not None:
        kwargs["x"] = spec.x
    if spec.y is not None:
        kwargs["y"] = spec.y
    if spec.color is not None:
        kwargs["color"] = spec.color
    if spec.size is not None:
        kwargs["size"] = spec.size
    if spec.hover_data is not None:
        kwargs["hover_data"] = spec.hover_data
    if spec.markers is not None:
        kwargs["markers"] = spec.markers
    if spec.opacity is not None:
        kwargs["opacity"] = spec.opacity
    if spec.category_orders is not None:
        kwargs["category_orders"] = spec.category_orders
    if spec.barmode is not None and chart_type == CHART_TYPE_BAR:
        kwargs["barmode"] = spec.barmode

    fig = renderer(**kwargs)

    if spec.trendline and chart_type == CHART_TYPE_SCATTER:
        _add_ols_trendline(fig, spec)

    return fig


VIEW_PREPARERS: dict[str, Callable[[pd.DataFrame], ViewSpec]] = {
    VIEW_ATTENDANCE_EXAM_CORRELATION: prepare_attendance_vs_grade,
    VIEW_ATTENDANCE_DISTRIBUTION: prepare_attendance_distribution,
    VIEW_ATTEMPTS_VS_ATTENDANCE: prepare_attempts_vs_attendance,
    VIEW_PASS_RATE_BY_BRACKET: prepare_pass_rate_by_bracket,
    VIEW_POINTS_VS_ATTENDANCE: prepare_points_vs_attendance,
}


def build_operational_figure(df: pd.DataFrame, view: str, chart_type: str):
    if df.empty:
        return _empty_figure("No data for selected filters")

    preparer = VIEW_PREPARERS.get(view)
    if preparer is None:
        return _empty_figure("Unsupported view selected")

    try:
        view_spec = preparer(df)
    except ValueError as exc:
        return _empty_figure(str(exc))

    if chart_type in view_spec.by_chart_type:
        selected_chart_type = chart_type
    elif CHART_TYPE_SCATTER in view_spec.by_chart_type:
        selected_chart_type = CHART_TYPE_SCATTER
    else:
        selected_chart_type = next(iter(view_spec.by_chart_type))
    spec = view_spec.by_chart_type[selected_chart_type]

    fig = build_chart(spec, selected_chart_type)

    fig.update_layout(template="plotly_white", margin={"l": 24, "r": 24, "t": 60, "b": 24})
    return fig
