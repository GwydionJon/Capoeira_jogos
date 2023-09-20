from dash import dcc, html, Dash, dash_table, Input, Output, State, MATCH, ALL
from dash.dash_table.Format import Format, Scheme, Sign, Symbol
import dash_bootstrap_components as dbc

from app_layout import create_basic_layout
from app_logic import (
    load_jogos_config_table,
    collect_and_update_round_points,
    collect_and_update_cat_points,
    check_ties_in_round,
    enable_next_round_button,
    start_new_round,
)


class jogos_app:
    def __init__(self):
        print()

        external_stylesheets = [dbc.themes.BOOTSTRAP]
        self.app = Dash(
            __name__,
            external_stylesheets=external_stylesheets,
            suppress_callback_exceptions=False,
        )
        self.app.title = "capoeira jogos"

        self.scale_game_points = 0.9
        self.chave_size = 4

        self.app.layout = create_basic_layout()

        # add callbacks

        # callback for upload file
        self.app.callback(
            Output("output-data-upload", "children"),
            Output("upload-data", "children"),
            Input("upload-data", "contents"),
            State("upload-data", "filename"),
            State("upload-data", "children"),
            prevent_initial_call=True,
        )(load_jogos_config_table)

        self.app.callback(
            # Output({"type": "category-table", "index": MATCH}, "data"),
            Output({"type": "round_table", "round": MATCH, "index": MATCH}, "data"),
            Output(
                {
                    "type": "round_tie_breaker",
                    "round": MATCH,
                    "index": MATCH,
                },
                "value",
            ),
            Input(
                {
                    "type": "chave-table",
                    "index": MATCH,
                    "round": MATCH,
                    "chave": ALL,
                    "game_type": ALL,
                },
                "data",
            ),
            State({"type": "round_table", "round": MATCH, "index": MATCH}, "data"),
            prevent_initial_call=True,
        )(collect_and_update_round_points)

        self.app.callback(
            Output({"type": "category-table", "index": MATCH}, "data"),
            Input({"type": "round_table", "round": ALL, "index": MATCH}, "data"),
            State({"type": "category-table", "index": MATCH}, "data"),
            prevent_initial_call=True,
        )(collect_and_update_cat_points)

        self.app.callback(
            Output(
                {
                    "type": "round_tie_breaker",
                    "round": MATCH,
                    "index": MATCH,
                },
                "options",
            ),
            Input({"type": "round_table", "round": MATCH, "index": MATCH}, "data"),
            Input(
                {
                    "type": "advance-dropdown",
                    "round": MATCH,
                    "index": MATCH,
                },
                "value",
            ),
            prevent_initial_call=True,
        )(check_ties_in_round)

        self.app.callback(
            Output(
                {
                    "type": "add-round-button",
                    "round": MATCH,
                    "index": MATCH,
                },
                "disabled",
            ),
            Output(
                {
                    "type": "check_tiebreaker_text",
                    "round": MATCH,
                    "index": MATCH,
                },
                "children",
            ),
            Input(
                {"type": "round_tie_breaker", "round": MATCH, "index": MATCH}, "value"
            ),
            prevent_initial_call=True,
        )(enable_next_round_button)

        self.app.callback(
            Output(
                {"type": "cat-round-tabs", "index": MATCH},
                "children",
            ),
            Input(
                {"type": "add-round-button", "round": ALL, "index": MATCH}, "n_clicks"
            ),
            State({"type": "round_table", "round": ALL, "index": MATCH}, "data"),
            State(
                {
                    "type": "advance-dropdown",
                    "round": ALL,
                    "index": MATCH,
                },
                "value",
            ),
            State(
                {
                    "type": "advance-dropdown",
                    "round": ALL,
                    "index": MATCH,
                },
                "value",
            ),
            State(
                {"type": "cat-round-tabs", "index": MATCH},
                "children",
            ),
            prevent_initial_call=True,
        )(start_new_round)

    def run_server(self):
        self.app.run_server(debug=True, use_reloader=True, port=8084)


if __name__ == "__main__":
    app = jogos_app()
    app.run_server()
