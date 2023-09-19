from dash import dcc, html, Dash, dash_table, Input, Output, State, MATCH, ALL
from dash.dash_table.Format import Format, Scheme, Sign, Symbol
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from tempfile import mkdtemp
import base64
import io
from app_layout import create_category_tab
import random
import itertools
from collections import defaultdict

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

        for key in df_dict.keys():
            # remove whitespaces from column names
            df_dict[key].rename(columns=lambda x: x.strip(), inplace=True)
            # fill empty appelido with first or last name
            df_dict[key].fillna(0, inplace=True)
            df_dict[key].loc[df_dict[key]["Apelido"] == 0, "Apelido"] = df_dict[key][
                "Vorname"
            ]
            df_dict[key].loc[df_dict[key]["Apelido"] == 0, "Apelido"] = df_dict[key][
                "Name"
            ]

        jogos_tabs = dcc.Tabs(
            id="tabs-all-categories",
            children=[
                create_category_tab(sheet_name, df_cat)
                for sheet_name, df_cat in df_dict.items()
            ],
        )

        return jogos_tabs, upload_label


def collect_and_update_points(current_, current_cat_table):
    print(test)
    print()
    print(test2)
