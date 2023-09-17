from dash import dcc, html, Dash, dash_table, Input, Output, State, MATCH, ALL
from dash.dash_table.Format import Format, Scheme, Sign, Symbol
import dash_bootstrap_components as dbc
import os
import pandas as pd
import numpy as np
from tempfile import mkdtemp
import base64
import io
from app_layout import create_category_tab


fontsize = 18


def load_jogos_config_table(content_str, filename_str, upload_label):
    """
    Loads the jogos config table from the given filepath.
    """

    if content_str is None:
        return html.Div("Nothing Found"), upload_label

    else:
        # set new label
        upload_label = html.Div(
            [
                html.P(
                    "File uploaded: " + filename_str,
                    style={"font-size": fontsize},
                ),
            ]
        )

        # convert file string to data
        data = content_str.encode("utf8").split(b";base64,")[1]
        decoded = base64.decodebytes(data)
        df_dict = pd.read_excel(
            io.BytesIO(decoded),
            sheet_name=None,
            skiprows=1,
        )

        jogos_tabs = dcc.Tabs(
            id="tabs-all-categories",
            children=[
                create_category_tab(sheet_name, df_cat)
                for sheet_name, df_cat in df_dict.items()
            ],
        )

        return jogos_tabs, upload_label


def initialize_chaves_block_settings(n_clicks):
    print(n_clicks)
    return True, True
