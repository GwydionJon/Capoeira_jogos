from dash import dcc, html, Dash, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import os
import pandas as pd
import numpy as np


# Create the app class
class jogosApp:
    """_summary_"""

    def __init__(self):
        external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
        self.app = Dash(
            __name__,
            external_stylesheets=external_stylesheets,
            suppress_callback_exceptions=False,
        )
        self._create_first_page()

    def _create_first_page(self):

        self.app.layout = html.Div(
            [
                html.H5("Jogos:"),
                html.H5("Something:"),
            ]
        )

    def run_server(self):
        self.app.run_server(debug=True, use_reloader=True, port=8051)
