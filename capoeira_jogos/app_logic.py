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


def collect_and_update_round_points(new_round_values, current_round_table):
    # flatten 2d list
    new_round_values = list(itertools.chain.from_iterable(new_round_values))
    # convert to df
    df_all_game_points = pd.DataFrame(new_round_values)

    # extract all player names
    names = pd.unique(df_all_game_points[["Player 1", "Player 2"]].values.ravel("K"))

    for name in names:
        filtered_player_one = df_all_game_points[
            df_all_game_points["Player 1"] == name
        ].filter(like="P1")
        filtered_player_two = df_all_game_points[
            df_all_game_points["Player 2"] == name
        ].filter(like="P2")
        filtered_player_gp = df_all_game_points[
            (df_all_game_points["Player 2"] == name)
            | (df_all_game_points["Player 1"] == name)
        ].filter(like="GP")

        # Step 2: Select columns containing 'gp' for every player

        sum_p1 = filtered_player_one.astype(int).sum().sum()
        sum_p2 = filtered_player_two.astype(int).sum().sum()
        sum_gp = filtered_player_gp.astype(int).sum().sum() * 0.9

        # add points to existing round table
        for row in current_round_table:
            if row["Player"] == name:
                row["personal points"] = sum_p1 + sum_p2
                row["game points"] = sum_gp
                row["total points"] = sum_p1 + sum_p2 + sum_gp

    return current_round_table


def collect_and_update_cat_points(new_round_table, current_cat_table):
    print("update cat")
    print(new_round_table)
    # print()
    print(current_cat_table)
    # flatten incoming list
    new_round_table = list(itertools.chain.from_iterable(new_round_table))

    player_points = defaultdict(int)
    for row in new_round_table:
        player_points[row["Player"]] += row["total points"]

    for i, row in enumerate(current_cat_table):
        for player, points in player_points.items():
            if row["Apelido"] == player:
                current_cat_table[i]["Points"] = points
    print(current_cat_table)
    return current_cat_table
