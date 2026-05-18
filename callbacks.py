from dash import Input, Output, State, no_update

from constants import (
    CHART_TYPE_BAR,
    CHART_TYPE_BOX,
    CHART_TYPE_LINE,
    CHART_TYPE_SCATTER,
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
    VIEW_ATTEMPTS_VS_ATTENDANCE,
    VIEW_ATTENDANCE_DISTRIBUTION,
    VIEW_ATTENDANCE_EXAM_CORRELATION,
    VIEW_PASS_RATE_BY_BRACKET,
    VIEW_POINTS_VS_ATTENDANCE,
)

from helpers import (
    build_kpis,
    build_operational_figure,
    filter_attendance,
    records_to_dataframe,
)


VIEW_PRESETS = {
    VIEW_ATTENDANCE_EXAM_CORRELATION: {
        "chart_type": CHART_TYPE_BOX,
        "years": "all",
        "attempts": "all",
        "classes": "all",
        "classes_require_column": None,
    },
    VIEW_ATTENDANCE_DISTRIBUTION: {
        "chart_type": CHART_TYPE_LINE,
        "years": "all",
        "attempts": "all",
        "classes": "largest",
        "classes_require_column": None,
    },
    VIEW_ATTEMPTS_VS_ATTENDANCE: {
        "chart_type": CHART_TYPE_BOX,
        "years": "latest",
        "attempts": "non_missing",
        "classes": "all",
        "classes_require_column": None,
    },
    VIEW_PASS_RATE_BY_BRACKET: {
        "chart_type": CHART_TYPE_BAR,
        "years": "all",
        "attempts": "all",
        "classes": "all",
        "classes_require_column": None,
    },
    VIEW_POINTS_VS_ATTENDANCE: {
        "chart_type": CHART_TYPE_SCATTER,
        "years": "latest",
        "attempts": "non_missing",
        "classes": "largest",
        "classes_require_column": "final_points",
    },
}

# region Callbacks

# Callback to update the main graph and KPIs based on filters and view selection/change
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

    # When the user switches view, snap chart type and filters to what makes sense for that view.
    @app.callback(
        Output(ID_CHART_TYPE_SELECTOR, "value"),
        Output(ID_YEAR_FILTER, "value"),
        Output(ID_EXAM_ATTEMPT_FILTER, "value"),
        Output(ID_CLASS_FILTER, "value"),
        Input(ID_VIEW_SELECTOR, "value"),
        State(ID_DATA_STORE, "data"),
        State(ID_YEAR_FILTER, "options"),
        State(ID_EXAM_ATTEMPT_FILTER, "options"),
        State(ID_CLASS_FILTER, "options"),
    )
    def apply_view_presets(view, records, year_options, attempt_options, class_options):
        preset = VIEW_PRESETS.get(view)
        if preset is None:
            return no_update, no_update, no_update, no_update

        year_values = sorted([opt["value"] for opt in (year_options or [])])
        attempt_values = [opt["value"] for opt in (attempt_options or [])]
        class_values = [opt["value"] for opt in (class_options or [])]

        if preset["years"] == "latest" and year_values:
            years_out = [year_values[-1]]
        else:
            years_out = year_values

        if preset["attempts"] == "non_missing":
            attempts_out = [v for v in attempt_values if v != "Missing"]
        else:
            attempts_out = attempt_values

        if preset["classes"] == "largest" and class_values:
            df_all = records_to_dataframe(records)
            require_col = preset.get("classes_require_column")
            if "class" in df_all.columns and not df_all.empty:
                eligible = df_all
                if require_col and require_col in df_all.columns:
                    eligible = df_all[df_all[require_col].notna()]
                if not eligible.empty:
                    classes_out = [str(eligible["class"].value_counts().idxmax())]
                else:
                    classes_out = class_values
            else:
                classes_out = class_values
        else:
            classes_out = class_values

        return preset["chart_type"], years_out, attempts_out, classes_out

# endregion