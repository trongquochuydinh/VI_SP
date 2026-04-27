from dash import Dash

from callbacks import register_callbacks
from constants import APP_TITLE
from layout import build_layout

app = Dash(__name__, title=APP_TITLE)
server = app.server

app.layout = build_layout()
register_callbacks(app)
