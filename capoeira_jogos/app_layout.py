from dash import dcc, html, Dash, dash_table, Input, Output, State, MATCH, ALL
from dash.dash_table.Format import Format, Scheme, Sign, Symbol
import dash_bootstrap_components as dbc
import pandas as pd
from collections import defaultdict

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

    # add category settings to tab
    start_chave_button = dbc.Button(
        children=["Initilize Chaves"],
        id={"type": "start-chave-button", "index": category},
        style={"font-size": fontsize},
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
            dbc.Row(id={"type": "chaves-row", "index": category}),
        ],
    )
    return tab


def create_round_tabs(
    category,
    game_types,
    games_per_player_per_type,
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
                                game_types,
                                games_per_player_per_type,
                                round_number,
                                players,
                                shave_pairs,
                                shave_names_dict,
                            )
                        ],
                        style={"margin": "2%"},
                    ),
                ]
            )
        ]
    )
    return tabs_layout


def create_round_tab(
    category,
    game_types,
    games_per_player_per_type,
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

    # create the tabs
    all_type_acc_item = []
    for game_type in game_types:
        all_type_acc_item.append(
            create_game_type_acc_item(
                category, shave_names_dict, game_type, shave_pairs
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
        ],
        label=f"Round {round_number}",
    )
    return tab


def create_game_type_acc_item(category, shave_names_dict, game_type, pairs):
    # generate a small card for each shavi that included the names and a table for the points
    def _create_shavi_card(
        category, shave_number, shavi_names, game_type, shavi_pairs_for_type
    ):
        # create datatable for the shavi
        print(shavi_pairs_for_type)

        players_1 = [players[0] for players in shavi_pairs_for_type]
        players_2 = [players[1] for players in shavi_pairs_for_type]
        shavi_df = pd.DataFrame(players_1, columns=["Player1"])
        shavi_df["Ref1-P1"] = 0
        shavi_df["Ref1-GP"] = 0
        shavi_df["Ref1-P2"] = 0
        shavi_df["Ref2-P1"] = 0
        shavi_df["Ref2-PGP"] = 0
        shavi_df["Ref2-P2"] = 0
        shavi_df["Ref3-P1"] = 0
        shavi_df["Ref3-PGP"] = 0
        shavi_df["Ref3-P2"] = 0
        shavi_df["Player2"] = players_2
        print(shavi_df)
        card = dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4(str(shavi_names), style={"textAlign": "center"}),
                        dash_table.DataTable(shavi_df.to_dict("records")),
                    ]
                )
            ]
        )
        return card

    cards = []
    for shave in shave_names_dict.keys():
        cards.append(
            _create_shavi_card(
                category,
                shave,
                shave_names_dict[shave],
                game_type,
                pairs[shave][game_type],
            )
        )

    acc_item = dbc.AccordionItem(title=game_type, children=[html.Div(cards)])
    return acc_item
