import os

import pandas as pd
from matplotlib import pyplot as plt

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

    fig, ax = plt.subplots(3, 1, sharex=True, figsize=(20, 6))

    plt.xlim(0, 61)
    plt.xticks(range(0, 61))
    fig.subplots_adjust(hspace=0)

    count = 0
    for column in spiel_df.columns[0:]:
        if column == 'Treffer':
            color = 'green'
        elif column == 'Verworfen':
            color = 'orange'
        else:
            color = 'red'

        ax[count].bar(spiel_df.index, spiel_df[column], width=0.5, color=color, label=column)
        ax[count].set_yticks(range(0, 3))
        ax[count].set_ylim(0, 2.25) # Hardcoded sucks, but the whole plot is temporary anyway
        ax[count].legend(loc='upper left')

        count += 1
    img_path = os.path.join(OUTPUT_DIR, f"plot_spiel_timeline.png")
    plt.savefig(img_path)
    plt.close()

    return Analysis(img_path)
