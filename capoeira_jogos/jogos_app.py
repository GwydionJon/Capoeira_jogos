from cProfile import label
from dash import dcc, html, Dash, dash_table
from dash.dash_table.Format import Format, Scheme, Sign, Symbol
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import os
import pandas as pd
import numpy as np
from tempfile import mkdtemp
import base64
import random
from collections import defaultdict

working_dir = mkdtemp()


def _make_round_header(names, points=None):
    if points is None:
        points = np.zeros(len(names))
    label_string = ""
    for name, point in zip(names, points):
        label_string += f"  {name}: {point},    "
    return label_string


# Create the app class
def calculate_round_points(round_data, group_data):
    scale_game_points = 0.9
    shavi_df_list = []
    for shavi in round_data:
        shavi_df_list.append(pd.DataFrame(shavi))
    df = pd.concat(shavi_df_list)

    # convert all numbers to float
    df[["Points Game", "Points B", "Points A"]] = df[
        ["Points Game", "Points B", "Points A"]
    ].astype(float)

    df["Points Game"] = df["Points Game"] * scale_game_points
    df_round_result = pd.DataFrame(group_data)
    names_list = list(
        set([item for sublist in df[["Name 1", "Name 2"]].values for item in sublist])
    )
    df_round_result = df_round_result[df_round_result["Apelido"].isin(names_list)]
    for player in names_list:

        points_total_A = df.loc[df["Name 1"] == player][
            ["Points Game", "Points A"]
        ].to_numpy()
        points_total_B = df.loc[df["Name 2"] == player][
            ["Points Game", "Points B"]
        ].to_numpy()
        df_round_result.loc[df_round_result["Apelido"] == player, "Points"] = np.sum(
            points_total_A
        ) + np.sum(points_total_B)
    return df_round_result


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
        self._create_callbacks()
        # self._create_jogos_tabs()

        self.scale_game_points = 0.9
        self.shavi_size = 4

    def _create_callbacks(self):
        @self.app.callback(
            Output("output-data-upload", "children"),
            Output("upload-data", "children"),
            Input("upload-data", "contents"),
            State("upload-data", "filename"),
            State("upload-data", "children"),
            prevent_initial_callbacks=True,
        )
        def update_output(list_of_contents, list_of_names, upload_label):
            if list_of_contents is not None:
                upload_label = html.Div([f"Using: {list_of_names}"])
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

                return self._create_group_overview(df_dict), upload_label
            else:
                print("is none")

        @self.app.callback(
            Output(
                {"type": "shavi_table", "cat": MATCH, "index": MATCH, "round": MATCH},
                "data",
            ),
            [
                Input(
                    {
                        "type": "shavi_table",
                        "cat": MATCH,
                        "index": MATCH,
                        "round": MATCH,
                    },
                    "data",
                )
            ],
            [State({"type": "cat_names_point_list", "cat": MATCH}, "data")],
        )
        def format_shavi_points(data_input, group_data):
            # add values seperated by +-sign together
            for i, column in enumerate(data_input):
                for key in ["Points A", "Points B", "Points Game"]:
                    if "+" in str(data_input[i][key]):
                        data_input[i][key] = str(
                            np.sum(list(map(int, data_input[i][key].split("+"))))
                        )

            return data_input

        # assign label per round
        @self.app.callback(
            Output({"type": "round_label", "cat": MATCH, "round": MATCH}, "children"),
            [
                Input(
                    {"type": "shavi_table", "cat": MATCH, "index": ALL, "round": MATCH},
                    "data",
                )
            ],
            [
                State({"type": "cat_names_point_list", "cat": MATCH}, "data"),
                State(
                    {"type": "round_label", "cat": MATCH, "round": MATCH}, "children"
                ),
            ],
        )
        def update_label(data_input, group_data, round_label):
            if data_input:
                df_round = calculate_round_points(data_input, group_data).sort_values(
                    "Points", ascending=False
                )

                return _make_round_header(df_round["Apelido"], df_round["Points"])
            else:
                return round_label

        @self.app.callback(
            Output({"type": "cat_names_point_list", "cat": MATCH}, "data"),
            [
                Input(
                    {"type": "shavi_table", "cat": MATCH, "index": ALL, "round": ALL},
                    "data",
                ),
                Input(
                    {"type": "shavi_table", "cat": MATCH, "index": ALL, "round": ALL},
                    "id",
                ),
            ],
            [
                State({"type": "cat_names_point_list", "cat": MATCH}, "data"),
            ],
        )
        def calculate_group_points(data_input, id_input, group_data):
            if data_input:
                # sort the shavis according to their rounds
                shavi_round_dict = defaultdict(list)
                for shavi_data, shavi_id in zip(data_input, id_input):
                    round = shavi_id["round"]
                    shavi_round_dict[round].append(shavi_data)

                for i, (round, round_data) in enumerate(shavi_round_dict.items()):
                    # for the first round create a new dataframe
                    if i == 0:
                        df_group = calculate_round_points(round_data, group_data)
                    # after the first round only add the points
                    else:
                        df_group["Points"] = (
                            df_group["Points"]
                            + calculate_round_points(round_data, group_data)["Points"]
                        )

                return df_group.to_dict("records")
            else:
                return group_data

        # confirm new round
        @self.app.callback(
            [
                Output({"type": "new_round_confirm_button", "cat": MATCH}, "displayed"),
                Output({"type": "new_round_confirm_button", "cat": MATCH}, "message"),
            ],
            [Input({"type": "new_round_button", "cat": MATCH}, "n_clicks")],
            [
                State({"type": "new_round_dropdown", "cat": MATCH}, "value"),
                State({"type": "cat_names_point_list", "cat": MATCH}, "data"),
            ],
            prevent_initial_callbacks=True,
        )
        def confirm_new_round(button_clicks, new_player_number, cat_player_data):
            if new_player_number:
                df_group = pd.DataFrame(cat_player_data)
                df_round_winner = df_group.nlargest(new_player_number, "Points")
                name_list = list(df_round_winner["Apelido"])
                return (
                    True,
                    f"Do you wish to start a new round with these participants: \n {name_list}",
                )
            else:
                return False, ""

        @self.app.callback(
            [Output({"type": "shavi_tabs", "cat": MATCH}, "children")],
            [
                Input(
                    {"type": "new_round_confirm_button", "cat": MATCH},
                    "submit_n_clicks",
                )
            ],
            [
                State({"type": "shavi_tabs", "cat": MATCH}, "children"),
                State({"type": "shavi_tabs", "cat": MATCH}, "id"),
                State({"type": "new_round_dropdown", "cat": MATCH}, "value"),
                State({"type": "cat_names_point_list", "cat": MATCH}, "data"),
            ],
            prevent_initial_callbacks=True,
        )
        def create_new_round(
            confirm_click, tabs, tabs_id, new_player_number, cat_player_data
        ):
            if new_player_number is None:
                return [tabs]

            else:
                df_group = pd.DataFrame(cat_player_data)
                df_round_winner = df_group.nlargest(new_player_number, "Points")

                cat_key = tabs_id["cat"]
                tabs.append(
                    self._create_shavi_tab(
                        df_round_winner, cat_key=cat_key, round=confirm_click + 1
                    )
                )
                return [tabs]

    def _create_group_overview(self, dict_df):
        list_group_tabs = []

        # loop over game categories (groups by rank)
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
                                style_cell={"maxWidth": "100px"},
                                style_as_list_view=False,
                                id={"type": "cat_names_point_list", "cat": key},
                                sort_action="native",
                            ),
                        ]
                    )
                ],
            )
            tab.children.append(html.H5("Shavis:"))
            tab.children.append(
                dcc.Tabs(
                    id={"type": "shavi_tabs", "cat": key},
                    children=[self._create_shavi_tab(df, cat_key=key)],
                )
            )

            # button and dropdown list for new round in cat
            new_round_confirm_warning = dcc.ConfirmDialog(
                id={"type": "new_round_confirm_button", "cat": key}, message=""
            )

            new_round_button = html.Button(
                id={
                    "type": "new_round_button",
                    "cat": key,
                },
                children="Start new round",
                n_clicks=0,
                style={"width": "40%"},
            )
            new_round_dropdown = dcc.Dropdown(
                [32, 16, 8, 4],
                id={"type": "new_round_dropdown", "cat": key},
                style={"width": "80%"},
                placeholder="Please select how many players should go to the next round:",
            )

            tab.children.append(
                html.Div(
                    [new_round_confirm_warning, new_round_dropdown, new_round_button],
                    style={"width": "49%", "display": "inline-block"},
                )
            )

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
            style_cell_conditional=[
                {
                    "if": {"column_id": "Name 1"},
                    "max-width": "25px",
                    "textAlign": "left",
                    "backgroundColor": "rgb(23,35,230)",
                    "color": "white",
                },
                {
                    "if": {"column_id": "Name 2"},
                    "max-width": "25px",
                    "textAlign": "left",
                    "backgroundColor": "rgb(50,50,50)",
                    "color": "white",
                },
                {"if": {"column_id": "Points A"}, "max-width": "25px"},
                {"if": {"column_id": "Points B"}, "max-width": "25px"},
                {"if": {"column_id": "Points Game"}, "max-width": "25px"},
            ],
            # id="test"
        )
        for column in shavi_table.columns:
            if column["name"] in ["Points A", "Points Game", "Points B"]:
                # column["type"] = "numeric"
                column["editable"] = True

        return shavi_table

    def _create_shavi_tab(self, df, cat_key, round=1) -> dcc.Tabs:
        name_list = list(df["Apelido"])
        name_label = html.H6(
            _make_round_header(name_list),
            id={"type": "round_label", "cat": cat_key, "round": str(round)},
        )
        # Add Platzhalter for filled shavis
        if len(name_list) % self.shavi_size != 0:
            for i in range(self.shavi_size - len(name_list) % self.shavi_size):
                name_list.append("Platzhalter")

        random.shuffle(name_list)
        n_shavis = np.ceil(len(df) / self.shavi_size)
        shavi_table_list = []
        for i in np.arange(n_shavis, dtype=int):
            current_names = name_list[i * self.shavi_size : (i + 1) * self.shavi_size]
            current_shavi_table = self._create_shavi_table(
                current_names, cat_key=cat_key, index=i, round=round
            )
            shavi_table_list.append(current_shavi_table)

        shavi_tab = dcc.Tab(
            label=f"Round {round}",
            id={"type": "shavi_tab", "cat": cat_key, "round": str(round)},
            children=[
                html.Div([name_label, *shavi_table_list], style={"width": "50%"})
            ],
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

    def run_server(self):
        self.app.run_server(debug=True, use_reloader=True, port=8051)
