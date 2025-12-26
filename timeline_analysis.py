import os

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import AutoMinorLocator

from Analysis import Analysis
from constants import OUTPUT_DIR, MISSED_SHOTS_FIELDS, SCORED_SHOTS_FIELDS


# TODO bessere darstellung überlegen
# Analyse over 60 minutes when we scored, missed or made a mistake.
def full_game_analysis_new(data: pd.DataFrame):

    df_shots = data[data['own_team']]
    df_score = df_shots[df_shots['type'].isin(SCORED_SHOTS_FIELDS)]
    df_fehler = df_shots[df_shots['type'] == 'Fehler']
    df_miss = df_shots[(df_shots['type'].isin(MISSED_SHOTS_FIELDS))]

    spiel_df = pd.DataFrame()

    treffer_list = df_score["minute"].value_counts()[1:]
    fehler_list = df_fehler["minute"].value_counts()[1:]
    verworfen_list = df_miss["minute"].value_counts()[1:]

    for i in range(0, 61):
        if i in treffer_list:
            spiel_df.loc[i, "Treffer"] = treffer_list[i]

        if i in fehler_list:
            spiel_df.loc[i, "Fehler"] = fehler_list[i]

        if i in verworfen_list:
            spiel_df.loc[i, "Verworfen"] = verworfen_list[i]

    fig, ax = plt.subplots(3, 1, figsize=(20, 6))

    fig.subplots_adjust(hspace=.3)

    count = 0
    for column in spiel_df.columns[0:]:
        if column == 'Treffer':
            color = 'green'
        elif column == 'Verworfen':
            color = 'orange'
        else:
            color = 'red'

        ax[count].bar(spiel_df.index, spiel_df[column], width=0.5, color=color, label=column)
        ax[count].legend(loc='upper left')
        ax[count].set_xticks(range(0, 61, 5))
        ax[count].set_xlim(0, 61)
        ax[count].xaxis.set_minor_locator(AutoMinorLocator())
        ax[count].tick_params(which='minor', length=4)
        ax[count].tick_params(which='major', length=7)

        count += 1
    img_path = os.path.join(OUTPUT_DIR, f"plot_spiel_timeline.png")
    plt.savefig(img_path)
    plt.close()

    return Analysis(img_path, width=11.75, height=5, left=-1, top=1)

# TODO find better plot type
def seconds_per_attack(data: pd.DataFrame) -> Analysis:

    # FIXME: use ball changing teams and not time until shot for time in attack - what?
    own_seconds_in_attack = data[data['own_team']]['attack_time']
    opponent_seconds_in_attack = data[~data['own_team']]['attack_time']

    fig, ax = plt.subplots(2, 1, figsize=(15, 6))
    fig.subplots_adjust(hspace=.3)

    ax[0].bar(height=own_seconds_in_attack, x=list(data.loc[own_seconds_in_attack.index, 'minute']))
    ax[0].set_title("Handballfreunde Sekunden pro Angriff")
    ax[0].set_xticks(range(0, 61, 5))
    ax[0].xaxis.set_minor_locator(AutoMinorLocator())
    ax[0].tick_params(which='minor', length=4)
    ax[0].tick_params(which='major', length=7)

    ax[1].bar(height=opponent_seconds_in_attack, x=list(data.loc[opponent_seconds_in_attack.index, 'minute']))
    ax[1].set_title("Gegner Sekunden pro Angriff")
    ax[1].set_xticks(range(0, 61, 5))
    ax[1].xaxis.set_minor_locator(AutoMinorLocator())
    ax[1].tick_params(which='minor', length=4)
    ax[1].tick_params(which='major', length=7)

    # save image
    img_path = os.path.join(OUTPUT_DIR, "plot_time_per_attack_timeline.png")
    plt.savefig(img_path)
    plt.close()

    return Analysis(img_path, width=11.75, height=5, left=-1, top=1)