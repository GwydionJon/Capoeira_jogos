from dash import dcc, html, Dash, dash_table, Input, Output, State, MATCH, ALL
from dash.dash_table.Format import Format, Scheme, Sign, Symbol
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from tempfile import mkdtemp
import base64
import io
from app_layout import create_category_tab, create_round_tabs
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


def initialize_chaves_block_settings(n_clicks):
    return (True,), True


def split_round_in_chaves(name_list, player_per_shaves):
    random.seed(42)  # set fixed seed
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

    # create a list of all possible combinations
    combos = [
        [shave_names[0], shave_names[1]],
        [shave_names[2], shave_names[3]],
        [shave_names[0], shave_names[3]],
        [shave_names[1], shave_names[2]],
        [shave_names[1], shave_names[3]],
        [shave_names[0], shave_names[2]],
        [shave_names[0], shave_names[1]],
        [shave_names[2], shave_names[3]],
    ]
    games_per_type = 2  # two games for each game type, so every player plays once

    # check how many total games are for this shave
    total_games = len(game_types) * games_per_type
    # repeat shave_names list until longer than total games
    if total_games > len(combos):
        adjusted_pairs = combos * (total_games // len(shave_names) + 1)
        adjusted_pairs = adjusted_pairs[: total_games - 1]
    else:
        adjusted_pairs = combos[:total_games]

    print(adjusted_pairs)

    # create a dict with game types as keys and empty lists as values
    finished_pairs = defaultdict(list)

    for game_type in game_types:
        for i in range(games_per_type):
            finished_pairs[game_type].append(adjusted_pairs.pop(0))

    return finished_pairs


def create_round(name_list, game_types, games_per_player, player_per_shaves):
    # calc total games in round

    shaves_dict = split_round_in_chaves(name_list, player_per_shaves)
    pair_dict = {}
    for key, shave in shaves_dict.items():
        pair_dict[key] = make_shaves_pairings(shave, game_types, games_per_player)

    return shaves_dict, pair_dict


def initialize_chaves_start_round(
    n_clicks,
    chaves_row_children,
    table_participants,
    game_types,
    games_per_player_per_type,
    category,
):
    # only start chaves once
    if n_clicks > 1:
        return chaves_row_children

    else:
        names_list = [player["Apelido"] for player in table_participants]
        player_per_shaves = 4
        # create chaves
        shaves_dict, pairs_dict = create_round(
            names_list, game_types, games_per_player_per_type, player_per_shaves
        )
        category = category["index"]
        # create the first tab
        shave_tabs = create_round_tabs(
            category=category,
            game_types=game_types,
            games_per_player_per_type=games_per_player_per_type,
            round_number=1,
            players=names_list,
            shave_pairs=pairs_dict,
            shave_names_dict=shaves_dict,
        )
