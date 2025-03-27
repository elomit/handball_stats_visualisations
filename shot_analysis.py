import os
from typing import Any

import pandas as pd
from matplotlib import pyplot as plt

from constants import missed_shots_list, OUTPUT_DIR

# TODO Verworfen getrennt darstellen
# TODO Heber und Dreher

def analyze_keeper(data) -> dict[str, Any]:

    all_shots = data[data['type'].isin(["Tor", "Gehalten", "Verworfen"])]

    shots = all_shots[~all_shots['own_team']]
    goalie_names = shots['player_name'].unique()
    output = {}

    for keeper in goalie_names:
        images = {"Gesamt": create_shots_graph(shots, True, keeper)}

        # shots per position
        for location in shots[shots['player_name'] == keeper]['location'].unique():
            position_df = shots[(shots['player_name'] == keeper) & (shots['location'] == location)]
            images[location] = create_shots_graph(position_df, True, keeper, location)

        output[keeper] = images

    return output

# TODO maybe create Heatmap
def create_shots_graph(shots: pd.DataFrame, is_keeper: bool, player_name: str = None, location: str = None):

    # check whether for entire team or specific player
    if player_name is None:
        scored_shots = shots[~shots['type'].isin(missed_shots_list)]
        missed_shots = shots[shots['type'].isin(missed_shots_list)]
    else:
        scored_shots = shots[(shots['player_name'] == player_name) & ~(shots['type'].isin(missed_shots_list))]
        missed_shots = shots[(shots['player_name'] == player_name) & (shots['type'].isin(missed_shots_list))]

    success_color = 'red' if is_keeper else 'green'
    fail_color = 'green' if is_keeper else 'red'

    # plot one graph
    plt.figure()
    # always show entire goal (15x10)
    plt.xlim(0, 100)
    plt.xticks(())
    plt.ylim(0, 100)
    plt.yticks(())
    plt.plot(missed_shots["x"], missed_shots["y"], marker='o', linestyle='none', color=fail_color, ms=17, label='Verworfen')
    plt.plot(scored_shots["x"], scored_shots["y"], marker='o', linestyle='none', color=success_color, ms=15, label='Treffer')

    img_name, title = create_plot_title_and_name(player_name, location, is_keeper, len(scored_shots), len(missed_shots))

    plt.title(title)
    img_path = os.path.join(OUTPUT_DIR, img_name)

    # save image
    plt.savefig(img_path)
    plt.close()

    return img_path

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
