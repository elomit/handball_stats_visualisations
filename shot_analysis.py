import os

import pandas as pd
from matplotlib import pyplot as plt

from Analysis import Analysis
from constants import MISSED_SHOTS_FIELDS, OUTPUT_DIR, SHOT_FIELDS, GOALIE_SHOT_FIELDS, SCORED_SHOTS_FIELDS

# TODO Verworfen getrennt darstellen
# TODO Wenn nur eine Location existiert evtl. main und location-based mergen
# TODO Blocks in den Titel schreiben
# TODO Bundle Plots Together by Location

def analyze_shots(data: pd.DataFrame) -> Analysis:
    all_shots = data[data['type'].isin(SHOT_FIELDS)]

    shots = all_shots[all_shots['own_team']]
    player_names = shots['player_name'].unique()
    analysis = Analysis(create_shots_graph(shots, False))

    for player in player_names:
        player_analysis = Analysis(create_shots_graph(shots, False, player))

        # shots per position
        for location in shots[shots['player_name'] == player]['location'].unique():
            position_df = shots[(shots['player_name'] == player) & (shots['location'] == location)]
            player_analysis.add_analysis(Analysis(create_shots_graph(position_df, False, player, location)))

        analysis.add_analysis(player_analysis)

    return analysis


def analyze_keeper(data: pd.DataFrame) -> Analysis:

    all_shots = data[data['type'].isin(GOALIE_SHOT_FIELDS)]

    shots = all_shots[~all_shots['own_team']]
    goalie_names = shots['player_name'].unique()
    analysis = Analysis()

    for keeper in goalie_names:
        keeper_analysis = Analysis(create_shots_graph(shots, True, keeper))

        # shots per position
        for location in shots[shots['player_name'] == keeper]['location'].unique():
            position_df = shots[(shots['player_name'] == keeper) & (shots['location'] == location)]
            keeper_analysis.add_analysis(Analysis(create_shots_graph(position_df, True, keeper, location)))

        analysis.add_analysis(keeper_analysis)

    return analysis

# TODO maybe create Heatmap
def create_shots_graph(shots: pd.DataFrame, is_keeper: bool, player_name: str = None, location: str = None) -> str:

    if player_name is not None:
        shots = shots[shots['player_name'] == player_name]

    scored_shots = shots[shots['type'].isin(SCORED_SHOTS_FIELDS)]
    missed_shots = shots[shots['type'].isin(MISSED_SHOTS_FIELDS)]
    dreher_shots = shots[(shots['x'] == -2) & (shots['y'] == -2)]
    heber_shots = shots[(shots['x'] == -1) & (shots['y'] == -1)]

    success_color = 'red' if is_keeper else 'green'
    fail_color = 'green' if is_keeper else 'red'

    fig, ax = plt.subplots()

    # Configure plot
    plt.xlim(0, 100)
    plt.xticks(())
    plt.ylim(0, 100)
    plt.yticks(())

    # Add Title
    img_name, title = create_plot_title_and_name(player_name, location, is_keeper, len(scored_shots), len(missed_shots))
    plt.title(title)

    # Add Data
    plt.plot(missed_shots["x"], missed_shots["y"], marker='o', linestyle='none', color=fail_color, ms=17,
             label='Verworfen')
    plt.plot(scored_shots["x"], scored_shots["y"], marker='o', linestyle='none', color=success_color, ms=15,
             label='Treffer')

    # Add Textbox with Heber and Dreher
    textbox = ""
    if not dreher_shots.empty:
        textbox = get_trickshot_text(dreher_shots, is_keeper, "Dreher")
    if not heber_shots.empty:
        textbox = get_trickshot_text(heber_shots, is_keeper, "Heber")

    if len(textbox) > 0:
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.15)
        ax.text(0.0175, 0.975, textbox, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)

    # save image
    img_path = os.path.join(OUTPUT_DIR, img_name)
    plt.savefig(img_path)
    plt.close()

    return img_path


def get_trickshot_text(shots: pd.DataFrame, is_keeper: bool, typ: str) -> str:
    scored = shots[shots['type'].isin(SCORED_SHOTS_FIELDS)]
    textbox = typ + " "
    hits = len(scored)
    gesamt = len(shots)
    if is_keeper:
        textbox += "gehalten: " + str(gesamt - hits) + "/" + str(gesamt)
    else:
        textbox += "getroffen: " + str(hits) + "/" + str(gesamt)
    return textbox


def create_plot_title_and_name(player_name, location, is_keeper, scored_sum, missed_sum):
    shots_sum = missed_sum + scored_sum

    try:
        quote = round(((missed_sum if is_keeper else scored_sum) / shots_sum * 100), 2)
    except ZeroDivisionError:
        quote = "0"

    # set the title and labels
    title = "Keeperanalyse für " if is_keeper else "Wurfanalyse für "
    img_name = "plot_"

    if player_name is None:
        title += "die Handballfreunde"
        img_name += "team"
    else:
        title += player_name
        img_name += player_name

    if location is not None:
        title += " von " + location
        img_name += "_" + location

    title += f":\nWürfe =  {shots_sum}, "
    if is_keeper:
        title += f"Gehalten = {missed_sum}, "
    else:
        title += f"Treffer = {scored_sum}, "

    title += f" Quote = {quote}%"
    img_name += ".png"

    return img_name, title
