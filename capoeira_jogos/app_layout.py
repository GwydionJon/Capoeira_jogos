from dash import dcc, html, Dash, dash_table, Input, Output, State, MATCH, ALL
from dash.dash_table.Format import Format, Scheme, Sign, Symbol
import dash_bootstrap_components as dbc


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
                        "To start please click on 'Select Files' and select your prepared excel file.",
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


def create_changable_shavi_settings(category):
    settings_card = dbc.Card(
        style={"font-size": fontsize, "margin-top": "1%", "width": "80%"},
        children=[
            dbc.CardBody(
                id={"type": "category-settings-cardbody", "index": category},
                children=[
                    html.P(
                        "Here you can specify the settings for this category.\n"
                        + "Please note that these settings cant be changed once the shaves are initialized."
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "Types of games in this category:",
                                style={"width": "70%"},
                            ),
                            dbc.Input(
                                id={
                                    "type": "setting-input",
                                    "setting": "type-games",
                                    "index": category,
                                },
                                type="number",
                                min=1,
                                value=2,
                            ),
                            dbc.InputGroupText(
                                "Games per player per type", style={"width": "70%"}
                            ),
                            dbc.Input(
                                id={
                                    "type": "setting-input",
                                    "setting": "number-games",
                                    "index": category,
                                },
                                type="number",
                                min=1,
                                value=2,
                            ),
                        ]
                    ),
                ],
            )
        ],
    )
    return settings_card


def create_category_tab(category, df):
    """
    Noteable ids:

    {"type": "number-games","index": category,}: id for the game types input
    {"type": "number-games-per-player-per-type","index": category,}: id for the amount of games per player per type input
    {"type": "category-table", "index": category}: id for the category data table



    # for the settings input change the readonly attribute to True
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
    setting_card = create_changable_shavi_settings(category)

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
            dbc.Row(
                [
                    dbc.Col(setting_card, width=4),
                    dbc.Col(
                        start_chave_button,
                        align="center",
                        className="d-grid gap-2 col-3 ",
                    ),
                ]
            ),
        ],
    )
    return tab
