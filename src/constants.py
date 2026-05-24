APP_TITLE = "Attendance Operational Dashboard"

ID_DATA_STORE = "data-store"

ID_YEAR_FILTER = "year-filter"
ID_CLASS_FILTER = "class-filter"
ID_DAY_FILTER = "day-filter"
ID_EXAM_ATTEMPT_FILTER = "exam-attempt-filter"
ID_ATTENDANCE_RANGE = "attendance-range"
ID_VIEW_SELECTOR = "view-selector"
ID_CHART_TYPE_SELECTOR = "chart-type-selector"

ID_KPI_STUDENTS = "kpi-students"
ID_KPI_ATTENDANCE = "kpi-attendance"
ID_KPI_PARTICIPATION = "kpi-participation"
ID_KPI_DISPLAYED = "kpi-displayed"

ID_MAIN_GRAPH = "main-graph"

# Define view constants
VIEW_ATTENDANCE_BY_DAY = "Attendance by Day"
VIEW_ATTENDANCE_DISTRIBUTION = "attendance_distribution"
VIEW_ATTENDANCE_EXAM_CORRELATION = "attendance_exam_correlation"
VIEW_ATTEMPTS_VS_ATTENDANCE = "attempts_vs_attendance"
VIEW_PASS_RATE_BY_BRACKET = "pass_rate_by_bracket"
VIEW_POINTS_VS_ATTENDANCE = "points_vs_attendance"
VIEW_SANKEY_FLOW = "sankey_flow"

# Define view options for the dropdown
VIEW_OPTIONS = [
    {"label": "Attendance vs Final Grade", "value": VIEW_ATTENDANCE_EXAM_CORRELATION},
    {"label": "Attendance Distribution", "value": VIEW_ATTENDANCE_DISTRIBUTION},
    {"label": "Exam Attempts vs Attendance", "value": VIEW_ATTEMPTS_VS_ATTENDANCE},
    {"label": "Pass Rate by Attendance Bracket", "value": VIEW_PASS_RATE_BY_BRACKET},
    {"label": "Final Points vs Attendance (trendline)", "value": VIEW_POINTS_VS_ATTENDANCE},
    {"label": "Attendance vs Grade Flow", "value": VIEW_SANKEY_FLOW},
    {"label": "Attendance by Day", "value": VIEW_ATTENDANCE_BY_DAY},
]

# Define chart type constants
CHART_TYPE_SCATTER = "scatter"
CHART_TYPE_BOX = "box"
CHART_TYPE_LINE = "line"
CHART_TYPE_BAR = "bar"
CHART_TYPE_SANKEY = "sankey"

# Define chart type options for the dropdown
CHART_TYPE_OPTIONS = [
    {"label": "Scatter", "value": CHART_TYPE_SCATTER},
    {"label": "Box", "value": CHART_TYPE_BOX},
    {"label": "Line", "value": CHART_TYPE_LINE},
    {"label": "Bar", "value": CHART_TYPE_BAR},
    {"label": "Sankey Diagram", "value": CHART_TYPE_SANKEY},
]

# Define default data file and sheet name
DEFAULT_DATA_FILE = "bin/attendance_merged_evaluated_only.xlsx"
DEFAULT_SHEET_NAME = "attendance"

# Define layout constant
LAYOUT_MAX_WIDTH = "1200px"
