from dash import Dash

from callbacks import register_callbacks
from constants import APP_TITLE
from layout import build_layout

# Initialize the Dash app
app = Dash(__name__, title=APP_TITLE)

# Expose the Flask server instance for deployment
server = app.server

# Define the app layout and register callbacks
app.layout = build_layout()
register_callbacks(app)
