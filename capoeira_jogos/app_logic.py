from dash import dcc, html, Dash, dash_table, Input, Output, State, MATCH, ALL
from dash.dash_table.Format import Format, Scheme, Sign, Symbol
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from tempfile import mkdtemp
import base64
import io
from app_layout import create_category_tab, create_round_tab, create_round
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
    df_all_game_points = pd.DataFrame(new_round_values).replace("", 0)

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

    return current_round_table, None


def collect_and_update_cat_points(new_round_table, current_cat_table):
    # flatten incoming list
    new_round_table = list(itertools.chain.from_iterable(new_round_table))

    player_points = defaultdict(int)
    for row in new_round_table:
        player_points[row["Player"]] += row["total points"]

    for i, row in enumerate(current_cat_table):
        for player, points in player_points.items():
            if row["Apelido"] == player:
                current_cat_table[i]["Points"] = points
    return current_cat_table


def _check_best_players(df, n_winners):
    # get top n players from total points
    top_players = df.nlargest(n_winners, "total points")
    bot_players = df.nsmallest(len(df) - n_winners, "total points")
    # get the worst of the best
    worst_of_the_best = top_players["total points"].min()
    # get all players with the same points as the worst of the best
    tied_edge_cases = bot_players[bot_players["total points"] == worst_of_the_best]
    if len(tied_edge_cases) > 0:
        all_tied_edge_cases = df[df["total points"] == worst_of_the_best]
        # remove all tied edge cases from the top players
        top_players = top_players[
            ~top_players["Player"].isin(all_tied_edge_cases["Player"])
        ]
    else:
        all_tied_edge_cases = None

    return top_players, all_tied_edge_cases


def check_ties_in_round(current_round_table, no_of_winners):
    round_df = pd.DataFrame(current_round_table)
    # check for ties if more people are present then there are winners
    if len(round_df) > no_of_winners:
        top_players, all_tied_edge_cases = _check_best_players(round_df, no_of_winners)

        if all_tied_edge_cases is not None:
            if len(top_players) == no_of_winners - 1:
                # case where only one spot is uncertain
                return all_tied_edge_cases["Player"].values
            else:
                # case where more than one spot is uncertain
                return [
                    "There is more then one tiebreaker needed, please manually add points to the tied players: "
                    + ", ".join(all_tied_edge_cases["Player"].values)
                ]

    return ["No tiebreaker needed"]


def enable_next_round_button(tie_breaker_check, n_clicks_new_round):
    if n_clicks_new_round is not None and n_clicks_new_round > 0:
        return True, "new Round already started"

    elif tie_breaker_check is None:
        return True, "Check the tiebreaker box before starting a new round"

    elif "There is more then one tiebreaker needed" in tie_breaker_check:
        return True, tie_breaker_check

    else:
        return False, ""


def start_new_round(
    n_clicks,
    all_round_tables,
    no_of_winners,
    tiebreaker_names,
    current_round_tabs,
    current_round_tab_id,
):
    # I think we only ever need to consider the last entry of these input lists as we are only ever adding one round at a time
    # to make sure nothing wierd happens I should deactivate the all previous buttons and radio menus

    current_cat_id = current_round_tab_id["index"]

    # get current round number:
    current_round = len(n_clicks)

    current_round_table = all_round_tables[current_round - 1]
    tiebreaker_name = tiebreaker_names[current_round - 1]
    no_of_winners = no_of_winners[current_round - 1]

    round_df = pd.DataFrame(current_round_table)
    top_players, all_tied_edge_cases = _check_best_players(round_df, no_of_winners)

    # advancing player_names
    player_names = top_players["Player"].to_list()
    if all_tied_edge_cases is not None:
        player_names.append(tiebreaker_name)

    player_per_shaves = 4
    print(player_names)
    shaves_dict, pairs_dict = create_round(player_names, player_per_shaves)
    print(shaves_dict)
    # create new round tab
    new_tab = create_round_tab(
        category=current_cat_id,
        round_number=current_round + 1,
        players=player_names,
        shave_pairs=pairs_dict,
        shave_names_dict=shaves_dict,
    )

    current_round_tabs.append(new_tab)

    return current_round_tabs


def _organize_games_table(all_games_tables, all_game_table_ids):
    # game_type_dict[cat][game_type][round][chave]
    game_type_dict = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    )
    for game_id, actual_game_table in zip(all_game_table_ids, all_games_tables):
        game_type_dict[game_id["index"]][game_id["game_type"]][game_id["round"]][
            game_id["chave"]
        ].append(pd.DataFrame(actual_game_table))

    return game_type_dict


def generate_category_results(
    n_clicks, all_games_tables, all_rounds_tables, all_game_table_ids
):
    # all games tables strucute: all_games_tables[game_type*round][game]

    best_game_Layout = html.Div(children=[html.H2("Best Games for each category:")])

    # find the winners in category:
    last_round_df = pd.DataFrame(all_rounds_tables[-1])
    last_round_df.sort_values(by=["total points"], ascending=False, inplace=True)

    last_round_table = dbc.Table.from_dataframe(
        last_round_df, striped=True, bordered=True, hover=True
    )
    best_game_Layout.children.append(html.H2("Category winners:"))
    best_game_Layout.children.append(last_round_table)

    orgnaized_games_tables = _organize_games_table(all_games_tables, all_game_table_ids)

    for category, category_games in orgnaized_games_tables.items():
        for game_type, game_type_games in category_games.items():
            # concanate all games for one game type over all rounds tables

            total_game_type_df = pd.DataFrame()
            for round, round_games in game_type_games.items():
                for chave, chave_games in round_games.items():
                    for game in chave_games:
                        total_game_type_df = pd.concat([total_game_type_df, game])

            df_for_game_type = pd.DataFrame()
            df_for_game_type["GP"] = (
                total_game_type_df["Ref1-GP"].values.astype(int)
                + total_game_type_df["Ref2-GP"].values.astype(int)
                + total_game_type_df["Ref3-GP"].values.astype(int)
            )
            df_for_game_type["P1"] = (
                total_game_type_df["Ref1-P1"].values.astype(int)
                + total_game_type_df["Ref2-P1"].values.astype(int)
                + total_game_type_df["Ref3-P1"].values.astype(int)
            )
            df_for_game_type["P2"] = (
                total_game_type_df["Ref1-P2"].values.astype(int)
                + total_game_type_df["Ref2-P2"].values.astype(int)
                + total_game_type_df["Ref3-P2"].values.astype(int)
            )
            df_for_game_type["Player 1"] = total_game_type_df["Player 1"].values
            df_for_game_type["Player 2"] = total_game_type_df["Player 2"].values

            best_game_points = df_for_game_type.nlargest(1, "GP")["GP"].values[0]
            result_columns = ["Player 1", "Player 2", "P1", "P2", "GP"]
            best_games = df_for_game_type[df_for_game_type["GP"] == best_game_points][
                result_columns
            ]

            # make dash table
            new_table = dbc.Table.from_dataframe(
                best_games, striped=True, bordered=True, hover=True
            )
            best_game_Layout.children.append(html.H2(f"Best {game_type} games:"))
            best_game_Layout.children.append(new_table)
    return True, best_game_Layout


def save_everything_to_excl(all_games_tables, all_game_table_ids, filename):

    save_dict = {}

    orgnaized_games_tables = _organize_games_table(all_games_tables, all_game_table_ids)
    for category, category_games in orgnaized_games_tables.items():
        list_of_df = []
        list_of_keys = []
        for game_type, game_type_games in category_games.items():
            # concanate all games for one game type over all rounds tables
            for round, round_games in game_type_games.items():
                for chave, chave_games in round_games.items():
                    for game in chave_games:
                        list_of_df.append(game)
                        list_of_keys.append((f"Round: {round}", game_type, chave))

        total_cat_type_df = pd.concat(list_of_df, keys=list_of_keys).sort_index(
            level=0, sort_remaining=False
        )

        save_dict[category] = total_cat_type_df

    # create excel file
    print(filename)
    filename = "Results_" + filename
    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        for category, df in save_dict.items():
            df.to_excel(writer, sheet_name=category)

    return None


def export_group_games(n_clicks, shave_tables, shave_tables_id, filename):
    orgnaized_games_tables = _organize_games_table(shave_tables, shave_tables_id)
    for category, category_games in orgnaized_games_tables.items():
        list_of_df = []
        list_of_keys = []
        for game_type, game_type_games in category_games.items():
            # concanate all games for one game type over all rounds tables
            for round, round_games in game_type_games.items():
                for chave, chave_games in round_games.items():
                    for game in chave_games:
                        list_of_df.append(game[["Player 1", "Player 2"]])
                        list_of_keys.append((f"Round: {round}", game_type, chave))

        total_cat_type_df = pd.concat(list_of_df, keys=list_of_keys).sort_index(
            level=0, sort_remaining=False
        )

        filename = f"Games_{category}_{filename}"
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            total_cat_type_df.to_excel(writer, sheet_name=category)

    return n_clicks
