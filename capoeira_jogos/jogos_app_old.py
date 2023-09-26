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


def save_round(
    cat_name,
    chave_round_dict,
    df_group,
    storage_dict=defaultdict(lambda: defaultdict(dict)),
):

    for round_nb, round_data in chave_round_dict.items():

        chave_df_list = [pd.DataFrame(chave) for chave in round_data]
        storage_dict[cat_name]["round_data"][f"round_{round_nb}"] = pd.concat(
            chave_df_list
        )
    storage_dict[cat_name]["group_data"] = df_group

    try:
        with pd.ExcelWriter("jogos_results.xlsx", engine="openpyxl") as writer:

            for cat_id, cat_value in storage_dict.items():

                if isinstance(cat_value["group_data"], pd.DataFrame):
                    cat_value["group_data"].to_excel(
                        writer, sheet_name=f"{cat_id}_main"
                    )

                    for round_number, round_value in cat_value["round_data"].items():
                        round_value.to_excel(
                            writer, sheet_name=f"{cat_id}_{round_number}"
                        )

    except PermissionError:
        with pd.ExcelWriter(
            "IF_THIS_APPEARS_CLOSE_EXCEL.xlsx", engine="openpyxl"
        ) as writer:

            for cat_id, cat_value in storage_dict.items():

                if isinstance(cat_value["group_data"], pd.DataFrame):
                    cat_value["group_data"].to_excel(
                        writer, sheet_name=f"{cat_id}_main"
                    )

                    for round_number, round_value in cat_value["round_data"].items():
                        round_value.to_excel(
                            writer, sheet_name=f"{cat_id}_{round_number}"
                        )

    except RuntimeError:
        # RuntimeError: dictionary changed size during iteration
        # no idea what to do about this...
        pass


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
    chave_df_list = []
    for chave in round_data:
        chave_df_list.append(pd.DataFrame(chave))
    df = pd.concat(chave_df_list)

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
        external_stylesheets = [dbc.themes.BOOTSTRAP]
        self.app = Dash(
            __name__,
            external_stylesheets=external_stylesheets,
            suppress_callback_exceptions=False,
        )
        self.app.title = "capoeira jogos"
        self._create_first_page()
        self._create_callbacks()
        # self._create_jogos_tabs()

        self.scale_game_points = 0.9
        self.chave_size = 4

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
                    df_dict[key].Apelido.fillna(df_dict[key].Name, inplace=True)

                return self._create_group_overview(df_dict), upload_label
            else:
                return html.Div(""), upload_label

        @self.app.callback(
            Output(
                {"type": "chave_table", "cat": MATCH, "index": MATCH, "round": MATCH},
                "data",
            ),
            [
                Input(
                    {
                        "type": "chave_table",
                        "cat": MATCH,
                        "index": MATCH,
                        "round": MATCH,
                    },
                    "data",
                )
            ],
            [State({"type": "cat_names_point_list", "cat": MATCH}, "data")],
        )
        def format_chave_points(data_input, group_data):
            # add values seperated by +-sign together
            for i, column in enumerate(data_input):
                for key in ["Points A", "Points B", "Points Game"]:
                    if "+" in str(data_input[i][key]):
                        data_input[i][key] = str(
                            np.sum(list(map(int, data_input[i][key].split("+"))))
                        )
                    try:
                        int(data_input[i][key])
                    except:
                        data_input[i][key] = 0
            return data_input

        # assign label per round
        @self.app.callback(
            Output({"type": "round_label", "cat": MATCH, "round": MATCH}, "children"),
            [
                Input(
                    {"type": "chave_table", "cat": MATCH, "index": ALL, "round": MATCH},
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
                    {"type": "chave_table", "cat": MATCH, "index": ALL, "round": ALL},
                    "data",
                ),
                Input(
                    {"type": "chave_table", "cat": MATCH, "index": ALL, "round": ALL},
                    "id",
                ),
            ],
            [
                State({"type": "cat_names_point_list", "cat": MATCH}, "data"),
            ],
        )
        def calculate_group_points(data_input, id_input, group_data):
            if data_input:
                # sort the chaves according to their rounds
                chave_round_dict = defaultdict(list)
                for chave_data, chave_id in zip(data_input, id_input):
                    round = chave_id["round"]
                    chave_round_dict[round].append(chave_data)

                for i, (round, round_data) in enumerate(chave_round_dict.items()):
                    # for the first round create a new dataframe
                    if i == 0:
                        df_group = calculate_round_points(round_data, group_data)
                    # after the first round only add the points
                    else:
                        df_group["Points"] = (
                            df_group["Points"]
                            + calculate_round_points(round_data, group_data)["Points"]
                        )
                save_round(id_input[0]["cat"], chave_round_dict, df_group)
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
            [Output({"type": "chave_tabs", "cat": MATCH}, "children")],
            [
                Input(
                    {"type": "new_round_confirm_button", "cat": MATCH},
                    "submit_n_clicks",
                )
            ],
            [
                State({"type": "chave_tabs", "cat": MATCH}, "children"),
                State({"type": "chave_tabs", "cat": MATCH}, "id"),
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
                    self._create_chave_tab(
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
                                    for c in df.columns[1:]
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
            tab.children.append(html.H5("Chaves:"))
            tab.children.append(
                dcc.Tabs(
                    id={"type": "chave_tabs", "cat": key},
                    children=[self._create_chave_tab(df, cat_key=key)],
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

    def _create_chave_table(self, names, round, cat_key, index):

        A, B, C, D = names
        chave_dict = {
            "Name 1": [A, C, A, B, A, B, A, C],
            "Points A": [0, 0, 0, 0, 0, 0, 0, 0],
            "Points Game": [0, 0, 0, 0, 0, 0, 0, 0],
            "Points B": [0, 0, 0, 0, 0, 0, 0, 0],
            "Name 2": [B, D, C, D, D, C, B, D],
        }

        chave_df = pd.DataFrame(chave_dict)

        chave_table = dash_table.DataTable(
            data=chave_df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in chave_df.columns],
            id={
                "type": "chave_table",
                "cat": cat_key,
                "index": str(index),
                "round": str(round),
            },
            style_data_conditional=[
                {"if": {"row_index": 0}, "backgroundColor": "#EB7D7D"},
                {"if": {"row_index": 1}, "backgroundColor": "#EB7D7D"},
                {"if": {"row_index": 2}, "backgroundColor": "#C3E84C"},
                {"if": {"row_index": 3}, "backgroundColor": "#C3E84C"},
                {"if": {"row_index": 4}, "backgroundColor": "#5CE84C"},
                {"if": {"row_index": 5}, "backgroundColor": "#5CE84C"},
                {"if": {"row_index": 6}, "backgroundColor": "#7D32BF"},
                {"if": {"row_index": 7}, "backgroundColor": "#7D32BF"},
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
        for column in chave_table.columns:
            if column["name"] in ["Points A", "Points Game", "Points B"]:
                # column["type"] = "numeric"
                column["editable"] = True

        return chave_table

    def _create_chave_tab(self, df, cat_key, round=1) -> dcc.Tabs:
        name_list = list(df["Apelido"])
        name_label = html.H6(
            _make_round_header(name_list),
            id={"type": "round_label", "cat": cat_key, "round": str(round)},
        )
        # Add Platzhalter for filled chaves
        random.shuffle(name_list)

        if len(name_list) % self.chave_size != 0:
            for i in range(self.chave_size - len(name_list) % self.chave_size):
                name_list.append("Platzhalter")

        n_chaves = np.ceil(len(df) / self.chave_size)
        chave_table_list = []
        for i in np.arange(n_chaves, dtype=int):
            current_names = name_list[i * self.chave_size : (i + 1) * self.chave_size]
            current_chave_table = self._create_chave_table(
                current_names, cat_key=cat_key, index=i, round=round
            )
            chave_table_list.append(
                html.Div([html.Div(f"Chave {i+1}:"), current_chave_table])
            )

        # explain coloring:
        coloring_label = html.Div(
            [
                html.Label(
                    [
                        "The different colors in each chave represent possible different game types. \n",
                        "For example red are the ",
                        html.Span("Sao bento", style={"color": "#EB7D7D"}),
                        " games, yellow ",
                        html.Span("Benguela", style={"color": "#C3E84C"}),
                        ", green and purple ",
                        html.Span("Iúna", style={"color": "#5CE84C"}),
                        " or ",
                        html.Span("Angola", style={"color": "#7D32BF"}),
                        " respectively. \n",
                        "When run locally this program will try to save each point change as a comprehensive excel file, please do not have excel open while entering new points! ",
                    ]
                ),
                "Hint: you can add multiple numbers with the + sign like: `3+4+5` into a field. This will than be calculated automatically.",
            ]
        )

        # create the entire tab
        chave_tab = dcc.Tab(
            label=f"Round {round}",
            id={"type": "chave_tab", "cat": cat_key, "round": str(round)},
            children=[
                html.Div(
                    [name_label, coloring_label, *chave_table_list],
                    style={"width": "50%"},
                )
            ],
        )

        return chave_tab

    def _create_first_page(self):

        self.app.layout = html.Div(
            [
                html.H5("Jogos Manager:"),
                html.Div(
                    # "This file should at least include a list of all apelidos and 'Apelido' as a column title. If you have multiple categories please put them in individual excel pages in the same document."
                    [
                        html.Label(
                            [
                                "This program was written by Gwydion Daskalakis and is freely shared under the ",
                                html.A(
                                    "MIT License",
                                    href="https://github.com/GwydionJon/Capoeira_jogos/blob/main/LICENSE",
                                    target="_blank",
                                ),
                            ]
                        ),
                        html.Label(
                            [
                                "A more detailed instruction as well as the underlying source code is found in the  ",
                                html.A(
                                    "github repository",
                                    href="https://github.com/GwydionJon/Capoeira_jogos",
                                    target="_blank",
                                ),
                            ]
                        ),
                        html.Label(
                            [
                                "To use this program you need to prepare a suitable excel file that lists all your categories and their participants. An ",
                                html.A(
                                    "example file",
                                    href="https://github.com/GwydionJon/Capoeira_jogos/blob/main/examples/example_excel_file.xlsx",
                                    target="_blank",
                                ),
                                " is provided.",
                            ]
                        ),
                    ]
                ),
                html.Div(
                    "To start please click on 'Select Files' and select your prepared excel file."
                ),
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
