from dash import dcc, html, Dash, dash_table, Input, Output, State, MATCH, ALL
from dash.dash_table.Format import Format, Scheme, Sign, Symbol
import dash_bootstrap_components as dbc

from app_layout import create_basic_layout
from app_logic import load_jogos_config_table, collect_and_update_points


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
            Output({"type": "category-table", "index": MATCH}, "data"),
            Output({"type": "round_table", "round": MATCH, "index": MATCH}, "data"),
            Input(
                {
                    "type": "chave-table",
                    "index": MATCH,
                    "chave": ALL,
                    "game_type": ALL,
                },
                "data",
            ),
            State({"type": "category-table", "index": MATCH}, "data"),
            prevent_initial_call=True,
        )(collect_and_update_points)

    def run_server(self):
        self.app.run_server(debug=True, use_reloader=True, port=8084)


if __name__ == "__main__":
    app = jogos_app()
    app.run_server()
