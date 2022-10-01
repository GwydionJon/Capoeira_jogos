from cProfile import label
from dash import dcc, html, Dash, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import os
import pandas as pd
import numpy as np
from tempfile import mkdtemp
import base64
import random


working_dir = mkdtemp()


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
        # self._create_jogos_tabs()

    def _create_group_overview(self, dict_df):
        list_group_tabs = []
        for key, df in dict_df.items():

            # add point column as first entry
            df["Points"] = 0
            first_column = df.pop("Points")
            df.insert(0, "Points", first_column)

            tab = dcc.Tab(
                label=key,
                children=[
                    html.Div(
                        [
                            dash_table.DataTable(
                                data=df.to_dict("records"),
                                columns=[{"name": i, "id": i} for i in df.columns],
                                style_cell_conditional=[
                                    {"if": {"column_id": c}, "textAlign": "left"}
                                    for c in [
                                        "Apelido",
                                        "Name",
                                        "Vorname",
                                        "Kordel",
                                        "Land",
                                        "Stadt",
                                    ]
                                ],
                                style_as_list_view=False,
                                id={"type": "cat_names_point_list", "category": key},
                            ),
                        ]
                    )
                ],
            )
            tab.children.append(html.H5("Shavis:"))
            tab.children.append(self._create_shavi_tab(df, cat_key=key))

            list_group_tabs.append(tab)

            tabs = dcc.Tabs(list_group_tabs)
        return tabs

    def _create_shavi_table(self, names, round, cat_key, index):
        A, B, C, D = names
        shavi_dict = {
            "Name 1": [A, C, A, B, A, B],
            "Points A": [0, 0, 0, 0, 0, 0],
            "Points Game": [0, 0, 0, 0, 0, 0],
            "Points B": [0, 0, 0, 0, 0, 0],
            "Name 2": [B, D, C, D, D, C],
        }

        shavi_df = pd.DataFrame(shavi_dict)

        shavi_table = dash_table.DataTable(
            data=shavi_df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in shavi_df.columns],
            id={
                "type": "shavi_table",
                "cat": cat_key,
                "index": str(index),
                "round": str(round),
            },
        )

        return shavi_table

    def _create_shavi_tab(self, df, cat_key) -> dcc.Tabs:
        name_list = list(df["Apelido"])
        # Add Platzhalter for filled shavis
        for i in range(4 - len(name_list) % 4):
            name_list.append("Platzhalter")

        random.shuffle(name_list)
        n_shavis = np.ceil(len(df) / 4)

        shavi_table_list = []
        for i in np.arange(n_shavis, dtype=int):
            print(i)
            current_names = name_list[i * 4 : (i + 1) * 4]
            current_shavi_table = self._create_shavi_table(
                current_names, cat_key=cat_key, index=i, round=1
            )
            shavi_table_list.append(current_shavi_table)

        shavi_tab_button = html.Button(
            id={
                "type": "shavi_tab_button",
                "cat": cat_key,
                "index": str(0),
                "round": str(round),
            },
            children="Start new round",
        )

        shavi_tab = dcc.Tab(
            id={"type": "shavi_tab", "cat": cat_key, "round": str(round)},
            children=[html.Div([*shavi_table_list, shavi_tab_button])],
        )
        return shavi_tab

    def _create_first_page(self):

        self.app.layout = html.Div(
            [
                html.H5("Jogos Setup:"),
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                    # Allow multiple files to be uploaded
                    multiple=False,
                ),
                html.Div(id="output-data-upload"),
            ]
        )

        @self.app.callback(
            Output("output-data-upload", "children"),
            Input("upload-data", "contents"),
            State("upload-data", "filename"),
            prevent_initial_callbacks=True,
        )
        def update_output(list_of_contents, list_of_names):
            if list_of_contents is not None:
                data = list_of_contents.encode("utf8").split(b";base64,")[1]
                with open(os.path.join(working_dir, list_of_names), "wb") as fp:
                    fp.write(base64.decodebytes(data))

                df_dict = pd.read_excel(
                    os.path.join(working_dir, list_of_names),
                    sheet_name=None,
                    skiprows=1,
                )

                for key in df_dict:
                    # strip spaces from column names
                    df_dict[key].columns = [
                        column.strip() for column in df_dict[key].columns
                    ]

                    # fill missing apelido with first name
                    df_dict[key].Apelido.fillna(df_dict[key].Vorname, inplace=True)

                return self._create_group_overview(df_dict)
            else:
                print("is none")

    def run_server(self):
        self.app.run_server(debug=True, use_reloader=True, port=8051)
