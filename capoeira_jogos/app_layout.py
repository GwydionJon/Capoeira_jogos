from dash import dcc, html, Dash, dash_table, Input, Output, State, MATCH, ALL
from dash.dash_table.Format import Format, Scheme, Sign, Symbol
import dash_bootstrap_components as dbc
import pandas as pd
from collections import defaultdict
import random

fontsize = 18


def create_basic_layout():
    layout = html.Div(
        id="div-app-container",
        style={
            "font-size": fontsize,
            "margin-left": "5%",
            "margin-top": "1%",
            "width": "80%",
        },
        children=[
            dbc.Row([dbc.Col(html.H1("Capoeira Jogos"))]),  # end first row
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            # "This file should at least include a list of all apelidos and 'Apelido' as a column title. If you have multiple categories please put them in individual excel pages in the same document."
                            [
                                html.P(
                                    [
                                        "This program was written by Gwydion Daskalakis and is freely shared under the ",
                                        html.A(
                                            "MIT License",
                                            href="https://github.com/GwydionJon/Capoeira_jogos/blob/main/LICENSE",
                                            target="_blank",
                                        ),
                                        html.Br(),
                                        "A more detailed instruction as well as the underlying source code is found in the  ",
                                        html.A(
                                            "github repository",
                                            href="https://github.com/GwydionJon/Capoeira_jogos",
                                            target="_blank",
                                        ),
                                        html.Br(),
                                        "To use this program you need to prepare a suitable excel file that lists all your categories and their participants. An ",
                                        html.A(
                                            "example file",
                                            href="https://github.com/GwydionJon/Capoeira_jogos/blob/main/examples/example_excel_file.xlsx",
                                            target="_blank",
                                        ),
                                        " is provided.",
                                    ],
                                    style={"font-size": fontsize},
                                ),
                            ]
                        ),
                    )
                ]
            ),  # end second row
            dbc.Row(
                [
                    html.P(
                        "To start please click on 'Select Files' and select your prepared excel file."
                        + "It is best if each player has a set 'Apelido' in the excel file.",
                        style={"font-size": fontsize},
                    ),
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div(
                            [
                                "Drag and Drop or ",
                                html.A("Select Files", style={"color": "blue"}),
                            ]
                        ),
                        style={
                            "width": "25%",
                            "height": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderRadius": "5px",
                            "textAlign": "center",
                            "margin": "10px",
                            "font-size": fontsize,
                        },  # Allow multiple files to be uploaded
                        multiple=False,
                    ),
                ]
            ),
            dbc.Row(id="output-data-upload"),  # this is where everything else goes
        ],
    )
    return layout


def create_category_tab(category, df):
    """
    Noteable ids:
    t


    {"type": "category-table", "index": category}: id for the category data table

    {"type": "chaves-row", "index": category}: here goes the chaves

    """

    # add points columns to table
    df["Points"] = 0
    df.insert(0, "Points", df.pop("Points"))

    # create the point data table for the category
    data_table = dash_table.DataTable(
        df.to_dict("records"),
        [{"name": i, "id": i} for i in df.columns],
        id={"type": "category-table", "index": category},
    )

    # create the tab itself
    tab = dcc.Tab(
        id={"type": "category-tab", "index": category},
        label=category,
        children=[
            dbc.Row(
                html.P(
                    f"Point and Chaves for {category}", style={"font-size": fontsize}
                ),
            ),
            dbc.Row(
                data_table,
            ),
            dbc.Row(
                id={"type": "chaves-row", "index": category},
                children=add_round_0(
                    table_participants=data_table.data, category=category
                ),
            ),
        ],
    )
    return tab


def add_round_0(table_participants, category):
    names_list = [player["Apelido"] for player in table_participants]
    player_per_shaves = 4
    # create chaves
    shaves_dict, pairs_dict = create_round(names_list, player_per_shaves)
    # create the first tab
    shave_tabs = create_round_tabs(
        category=category,
        round_number=1,
        players=names_list,
        shave_pairs=pairs_dict,
        shave_names_dict=shaves_dict,
    )
    return shave_tabs


def split_round_in_chaves(name_list, player_per_shaves):
    random.seed(0.2)  # set fixed seed
    random.shuffle(name_list)
    # amount of chaves
    no_chaves = (len(name_list) // player_per_shaves) + 1

    # fill up with empty players
    name_list += ["Placeholder"] * (no_chaves * player_per_shaves - len(name_list))
    # split names in chaves
    shaves_dict = {}
    for i in range(no_chaves):
        shaves_dict[f"Chave {i}"] = name_list[
            i * player_per_shaves : (i + 1) * player_per_shaves
        ]
    return shaves_dict


def make_shaves_pairings(shave_names, game_types):
    """
    Generate pairrings for one shave and every game type.
    Return a dict
    """
    # [A, C, A, B, A, B, A, C]
    # [B, D, C, D, D, C, B, D]
    # create a list of all possible combinations
    combos = [
        [shave_names[0], shave_names[1]],
        [shave_names[2], shave_names[3]],
        [shave_names[0], shave_names[2]],
        [shave_names[1], shave_names[3]],
        [shave_names[0], shave_names[3]],
        [shave_names[1], shave_names[2]],
        [shave_names[0], shave_names[1]],
        [shave_names[2], shave_names[3]],
    ]
    games_per_type = 2  # two games for each game type, so every player plays once

    # create a dict with game types as keys and empty lists as values
    finished_pairs = defaultdict(list)

    for game_type in game_types:
        for i in range(games_per_type):
            finished_pairs[game_type].append(combos.pop(0))

    return finished_pairs


def create_round(name_list, player_per_shaves):
    # calc total games in round
    game_types = ["Sao Bento", "Benguela", "Iuna", "Angola"]

    shaves_dict = split_round_in_chaves(name_list, player_per_shaves)
    pair_dict = {}
    for key, shave_names in shaves_dict.items():
        pair_dict[key] = make_shaves_pairings(shave_names, game_types)

    return shaves_dict, pair_dict


def create_round_tabs(
    category,
    round_number,
    players,
    shave_pairs,
    shave_names_dict,
):
    tabs_layout = html.Div(
        [
            dbc.Row(
                [
                    html.P("For entering points please note the following:"),
                    html.Br(),
                    html.P(
                        [
                            "Ref1-P1 are the points that referee 1 gave to player 1.",
                            html.Br(),
                            "Ref1-GP are the points that referee 1 gave for the combined game.",
                            html.Br(),
                            "Ref1-P2 are the points that referee 1 gave to player 2.",
                            html.Br(),
                            "This follows for Ref2 and Ref3 respectively.",
                        ]
                    ),
                    dcc.Tabs(
                        id={"type": "cat-round-tabs", "index": category},
                        children=[
                            create_round_tab(
                                category,
                                round_number,
                                players,
                                shave_pairs,
                                shave_names_dict,
                            )
                        ],
                        style={"margin": "2%"},
                    ),
                ]
            ),
        ]
    )
    return tabs_layout


def create_round_tab(
    category,
    round_number,
    players,
    shave_pairs,
    shave_names_dict,
):
    df_round = pd.DataFrame(players, columns=["Player"])
    df_round["personal points"] = 0
    df_round["game points"] = 0
    df_round["total points"] = 0
    df_round.drop(df_round[df_round["Player"] == "Placeholder"].index, inplace=True)
    df_round.sort_values("Player", inplace=True)
    overview_table = dash_table.DataTable(
        df_round.to_dict("records"),
        id={"type": "round_table", "round": round_number, "index": category},
    )

    game_types = ["Sao Bento", "Benguela", "Iuna", "Angola"]

    # create the tabs
    all_type_acc_item = []
    for game_type in game_types:
        all_type_acc_item.append(
            create_game_type_acc_item(
                category, round_number, shave_names_dict, game_type, shave_pairs
            )
        )

    # add all tabs to main tabs
    shave_game_type_accordion = dbc.Accordion(
        id={"type": "shave-tabs", "category": category, "round": round_number},
        children=all_type_acc_item,
        style={"margin": "2%"},
    )

    tab = dcc.Tab(
        children=[
            html.Div(overview_table, style={"width": "50%", "margin": "2%"}),
            html.Div(shave_game_type_accordion, style={"width": "80%", "margin": "2%"}),
            dbc.Row(
                style={"width": "80%", "margin": "3%"},
                children=[
                    dbc.Col(
                        [
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText(
                                        "How many should advance to the next round?"
                                    ),
                                    dcc.Dropdown(
                                        options=[32, 16, 8, 4],
                                        value=16,
                                        id={
                                            "type": "advance-dropdown",
                                            "round": round_number,
                                            "index": category,
                                        },
                                        style={"margin-top": "0.5%", "width": "100%"},
                                    ),
                                ],
                                style={"margin": ".5%", "width": "100%"},
                                className="mb-3",
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText(
                                        "In case of a draw please choose:"
                                    ),
                                    dbc.RadioItems(
                                        options=[],
                                        id={
                                            "type": "round_tie_breaker",
                                            "round": round_number,
                                            "index": category,
                                        },
                                    ),
                                ],
                                style={
                                    "margin-top": ".5%",
                                    "margin-left": "5%",
                                    "width": "70%",
                                },
                                className="mb-3",
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Button(
                                f"Finish Round {round_number}",
                                disabled=True,
                                id={
                                    "type": "add-round-button",
                                    "round": round_number,
                                    "index": category,
                                },
                                style={"margin": ".5%", "width": "40%"},
                            ),
                            html.P(
                                "Check the tiebreaker box before starting a new round",
                                id={
                                    "type": "check_tiebreaker_text",
                                    "round": round_number,
                                    "index": category,
                                },
                            ),
                        ]
                    ),
                ],
            ),
        ],
        label=f"Round {round_number}",
    )
    return tab


def create_game_type_acc_item(category, round, shave_names_dict, game_type, pairs):
    # generate a small card for each chave that included the names and a table for the points
    def _create_chave_card(
        category, round, shave_index, chave_names, game_type, chave_pairs_for_type
    ):
        # create datatable for the chave

        players_1 = [players[0] for players in chave_pairs_for_type]
        players_2 = [players[1] for players in chave_pairs_for_type]
        chave_df = pd.DataFrame(players_1, columns=["Player 1"])
        chave_df["Ref1-P1"] = 0
        chave_df["Ref1-GP"] = 0
        chave_df["Ref1-P2"] = 0
        chave_df["Ref2-P1"] = 0
        chave_df["Ref2-PGP"] = 0
        chave_df["Ref2-P2"] = 0
        chave_df["Ref3-P1"] = 0
        chave_df["Ref3-PGP"] = 0
        chave_df["Ref3-P2"] = 0
        chave_df["Player 2"] = players_2

        # set table styling:

        outer_table_style = [
            {
                "if": {"column_id": "Player 1"},
                "width": "15%",
                "textAlign": "left",
                "backgroundColor": "rgb(23,35,230)",
                "color": "white",
                "border": "1px solid black",
            },
            {
                "if": {"column_id": "Player 2"},
                "width": "15%",
                "textAlign": "left",
                "backgroundColor": "rgb(50,50,50)",
                "color": "white",
            },
        ]
        inner_table_style_P1 = [
            {
                "if": {"column_id": c},
                "max-width": "10%",
                "backgroundColor": "rgb(51,67,181)",
                "color": "white",
            }
            for c in ["Ref1-P1", "Ref2-P1", "Ref3-P1"]
        ]
        inner_table_style_P2 = [
            {
                "if": {"column_id": c},
                "max-width": "10%",
                "backgroundColor": "rgb(90,90,90)",
                "color": "white",
            }
            for c in ["Ref1-P2", "Ref2-P2", "Ref3-P2"]
        ]

        style_data_conditional = (
            outer_table_style + inner_table_style_P1 + inner_table_style_P2
        )
        chave_table = dash_table.DataTable(
            chave_df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in chave_df.columns],
            id={
                "type": "chave-table",
                "round": round,
                "index": category,
                "chave": shave_index,
                "game_type": game_type,
            },
            style_data_conditional=style_data_conditional,
        )
        for column in chave_table.columns:
            if "-" in column["name"]:
                # column["type"] = "numeric"
                column["editable"] = True

        card = dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4(str(chave_names), style={"textAlign": "center"}),
                        chave_table,
                    ]
                )
            ]
        )
        return card

    cards = []
    for shave in shave_names_dict.keys():
        cards.append(
            _create_chave_card(
                category,
                round,
                shave,
                shave_names_dict[shave],
                game_type,
                pairs[shave][game_type],
            )
        )

    acc_item = dbc.AccordionItem(title=game_type, children=[html.Div(cards)])
    return acc_item
