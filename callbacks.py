from dash import Input, Output

from constants import (
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
)
from helpers import (
    build_kpis,
    build_operational_figure,
    filter_attendance,
    records_to_dataframe,
)


def register_callbacks(app):
    @app.callback(
        Output(ID_MAIN_GRAPH, "figure"),
        Output(ID_KPI_STUDENTS, "children"),
        Output(ID_KPI_ATTENDANCE, "children"),
        Output(ID_KPI_PARTICIPATION, "children"),
        Output(ID_KPI_DISPLAYED, "children"),
        Input(ID_DATA_STORE, "data"),
        Input(ID_YEAR_FILTER, "value"),
        Input(ID_CLASS_FILTER, "value"),
        Input(ID_DAY_FILTER, "value"),
        Input(ID_EXAM_ATTEMPT_FILTER, "value"),
        Input(ID_ATTENDANCE_RANGE, "value"),
        Input(ID_VIEW_SELECTOR, "value"),
        Input(ID_CHART_TYPE_SELECTOR, "value"),
    )
    def update_dashboard(records, years, classes, days, attempts, attendance_range, view, chart_type):
        df_all = records_to_dataframe(records)
        df_filtered = filter_attendance(df_all, years, classes, days, attempts, attendance_range)

        fig = build_operational_figure(df_filtered, view, chart_type)
        students_text, attendance_text, participation_text, displayed_text = build_kpis(df_filtered, df_all)
        return fig, students_text, attendance_text, participation_text, displayed_text
