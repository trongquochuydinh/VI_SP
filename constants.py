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
VIEW_ATTENDANCE_DISTRIBUTION = "attendance_distribution"
VIEW_ATTENDANCE_EXAM_CORRELATION = "attendance_exam_correlation"

# Define view options for the dropdown
VIEW_OPTIONS = [
    {"label": "Attendance vs Final Grade", "value": VIEW_ATTENDANCE_EXAM_CORRELATION},
    {"label": "Attendance Distribution", "value": VIEW_ATTENDANCE_DISTRIBUTION},
]

# Define chart type constants
CHART_TYPE_SCATTER = "scatter"
CHART_TYPE_BOX = "box"
CHART_TYPE_LINE = "line"

# Define chart type options for the dropdown
CHART_TYPE_OPTIONS = [
    {"label": "Scatter", "value": CHART_TYPE_SCATTER},
    {"label": "Box", "value": CHART_TYPE_BOX},
    {"label": "Line", "value": CHART_TYPE_LINE},
]

# Define default data file and sheet name
DEFAULT_DATA_FILE = "attendance_merged_evaluated_only.xlsx"
DEFAULT_SHEET_NAME = "attendance"

# Define layout constant
LAYOUT_MAX_WIDTH = "1200px"
