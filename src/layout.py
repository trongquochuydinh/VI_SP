from dash import dcc, html

from constants import (
    APP_TITLE,
    ID_ATTENDANCE_RANGE,
    ID_CHART_TYPE_SELECTOR,
    ID_CLASS_FILTER,
    ID_DATA_STORE,
    ID_DAY_FILTER,
    ID_EXAM_ATTEMPT_FILTER,
    ID_KPI_ATTENDANCE,
    ID_KPI_DISPLAYED,
    ID_KPI_PARTICIPATION,
    ID_KPI_STUDENTS,
    ID_MAIN_GRAPH,
    ID_VIEW_SELECTOR,
    ID_YEAR_FILTER,
    LAYOUT_MAX_WIDTH,
    CHART_TYPE_OPTIONS,
    VIEW_OPTIONS,
)
from helpers import (
    build_kpis,
    dataframe_to_records,
    load_data,
    unique_options,
)


def _kpi_card(title: str, value_id: str, value_text: str):
    return html.Div(
        [
            html.Div(title, style={"fontSize": "12px", "opacity": "0.75", "marginBottom": "4px"}),
            html.Div(value_text, id=value_id, style={"fontSize": "22px", "fontWeight": "700"}),
        ],
        style={
            "flex": "1",
            "minWidth": "200px",
            "border": "1px solid #D9DDE5",
            "borderRadius": "8px",
            "padding": "12px",
            "background": "#F8FAFD",
        },
    )


def build_layout():
    df = load_data()
    students_text, attendance_text, participation_text, displayed_text = build_kpis(df, df)

    return html.Div(
        [
            dcc.Store(id=ID_DATA_STORE, data=dataframe_to_records(df)),
            html.H1(APP_TITLE),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Academic year"),
                            dcc.Dropdown(
                                id=ID_YEAR_FILTER,
                                options=unique_options(df, "academic_year"),
                                value=sorted(df["academic_year"].dropna().astype(str).unique().tolist()),
                                multi=True,
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Div(
                        [
                            html.Label("Class"),
                            dcc.Dropdown(
                                id=ID_CLASS_FILTER,
                                options=unique_options(df, "class"),
                                value=sorted(df["class"].dropna().astype(str).unique().tolist()),
                                multi=True,
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Div(
                        [
                            html.Label("Day"),
                            dcc.Dropdown(
                                id=ID_DAY_FILTER,
                                options=unique_options(df, "day"),
                                value=sorted(df["day"].dropna().astype(str).unique().tolist()),
                                multi=True,
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Div(
                        [
                            html.Label("Exam attempt"),
                            dcc.Dropdown(
                                id=ID_EXAM_ATTEMPT_FILTER,
                                options=unique_options(df, "exam_attempt_label"),
                                value=sorted(df["exam_attempt_label"].dropna().astype(str).unique().tolist()),
                                multi=True,
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                ],
                style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "12px"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Attendance range"),
                            dcc.RangeSlider(
                                id=ID_ATTENDANCE_RANGE,
                                min=0,
                                max=13,
                                value=[0, 13],
                                marks={i: str(i) for i in range(0, 14)},
                                step=1,
                            ),
                        ],
                        style={"flex": "2", "padding": "6px 10px"},
                    ),
                    html.Div(
                        [
                            html.Label("View"),
                            dcc.Dropdown(
                                id=ID_VIEW_SELECTOR,
                                options=VIEW_OPTIONS,
                                value=VIEW_OPTIONS[0]["value"],
                                clearable=False,
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Div(
                        [
                            html.Label("Chart type"),
                            dcc.Dropdown(
                                id=ID_CHART_TYPE_SELECTOR,
                                options=CHART_TYPE_OPTIONS,
                                value=CHART_TYPE_OPTIONS[0]["value"],
                                clearable=False,
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                ],
                style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "16px"},
            ),
            html.Div(
                [
                    _kpi_card("Students", ID_KPI_STUDENTS, students_text),
                    _kpi_card("Average Attendance", ID_KPI_ATTENDANCE, attendance_text),
                    _kpi_card("Exam Participation", ID_KPI_PARTICIPATION, participation_text),
                    _kpi_card("Rows Displayed", ID_KPI_DISPLAYED, displayed_text),
                ],
                style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "16px"},
            ),
            dcc.Graph(id=ID_MAIN_GRAPH),
        ],
        style={"maxWidth": LAYOUT_MAX_WIDTH, "margin": "24px auto", "padding": "0 16px"},
    )
