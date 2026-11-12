import math
import os

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import AutoMinorLocator

from Analysis import Analysis
from colors import TIMELINE_COLORS, OWN_ATTACK_COLOR, OPPONENT_ATTACK_COLOR, ATTEMPT_SEPARATOR_COLOR, ATTACK_GAP_COLOR, \
    ESTIMATED_ATTACK_HATCH, ESTIMATED_ATTACK_HATCH_COLORS
from constants import OUTPUT_DIR, MISSED_SHOTS_FIELDS, SCORED_SHOTS_FIELDS, TEAM_NAME, \
    ATTACK_TIMELINE_ROW_MINUTES, ATTEMPT_DURATION_STEP_SECONDS, HALF_TIME_SECONDS

# team (own_team): name and color of the attacks
ATTACK_TEAMS = {True: (TEAM_NAME, OWN_ATTACK_COLOR), False: ("Gegner", OPPONENT_ATTACK_COLOR)}


# TODO bessere darstellung überlegen
# Analyse over 60 minutes when we scored, missed or made a mistake.
def full_game_analysis_new(data: pd.DataFrame):

    df_shots = data[data['own_team']]
    df_shots_other_team = data[~data['own_team']]
    df_goals_other_team = df_shots_other_team[df_shots_other_team['type'].isin(SCORED_SHOTS_FIELDS)]
    df_score = df_shots[df_shots['type'].isin(SCORED_SHOTS_FIELDS)]
    df_fehler = df_shots[df_shots['type'] == 'Fehler']
    df_ballverlust = df_shots[df_shots['type'] == 'Ballverlust']
    df_miss = df_shots[(df_shots['type'].isin(MISSED_SHOTS_FIELDS))]

    spiel_df = pd.DataFrame()

    treffer_list = df_score["minute"].value_counts()
    fehler_list = df_fehler["minute"].value_counts()
    ballverlust_list = df_ballverlust["minute"].value_counts()
    verworfen_list = df_miss["minute"].value_counts()
    goals_other_team_list = df_goals_other_team["minute"].value_counts()

    for i in range(0, 61):
        if i in treffer_list:
            spiel_df.loc[i, "Treffer"] = treffer_list[i]

        if i in goals_other_team_list:
            spiel_df.loc[i, "Gegentor"] = goals_other_team_list[i]

        if i in fehler_list:
            spiel_df.loc[i, "Fehler"] = fehler_list[i]

        if i in ballverlust_list:
            spiel_df.loc[i, "Ballverlust"] = ballverlust_list[i]

        if i in verworfen_list:
            spiel_df.loc[i, "Verworfen"] = verworfen_list[i]

    order = ['Treffer', 'Gegentor', 'Verworfen', 'Ballverlust', 'Fehler']
    spiel_df = spiel_df.reindex(columns=order, fill_value=0)

    column_count = len(spiel_df.columns)
    fig_height = 2.5 * column_count
    fig, ax = plt.subplots(column_count, 1, figsize=(20, fig_height))

    fig.subplots_adjust(hspace=.3)

    count = 0
    for column in spiel_df.columns[0:]:
        color = TIMELINE_COLORS[column]

        if column == 'Ballverlust':
            label = 'Ballverlust (Fehlpass, nicht gefangen)'
        elif column == 'Fehler':
            label = 'Technischer Fehler (Schritte, 2Mal, Stürmerfoul)'
        else:
            label = column

        ax[count].bar(spiel_df.index, spiel_df[column], width=0.5, color=color, label=label)
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

    return Analysis(img_path, width=11.75, height=7, left=-1, top=0, title="Spielverlauf")

def attack_timeline(data: pd.DataFrame) -> Analysis:
    """Attacks of one game over the game time in rows of ATTACK_TIMELINE_ROW_MINUTES minutes: one box per attack,
    ours in the strong blue, the ones of the opponent in the light blue. In an attack with more than one attempt
    a thin white line separates the attempts (e.g. shot saved, rebound, second shot).
    Estimated attacks (attack of the other team missing in the data) are hatched, and so is the gap before them
    in the color of the missing team (from its last action to the estimated start).
    The attack running at the end of a half has no action: the other team had the ball from the last action
    of the half until the end of the half."""

    # boxes: (start, end) in minutes, own team, estimated
    attacks = _attacks(data)
    boxes = [(attack['start'] / 60, attack['end'] / 60, attack['own_team'], attack['estimated'])
             for _, attack in attacks.iterrows()]
    # missing attacks of the other team: before an estimated attack, from the end of the previous attack
    # (the attack numbers follow the game time)
    previous_end = attacks['end'].shift()
    missing = attacks[attacks['estimated'] & (previous_end < attacks['start'])]
    boxes += [(previous_end[number] / 60, attack['start'] / 60, not attack['own_team'], True)
              for number, attack in missing.iterrows()]
    # attacks running at the end of a half (an action at exactly 30:00 still belongs to the first half)
    halves = ((data['timestamp'] <= HALF_TIME_SECONDS, HALF_TIME_SECONDS),
              ((data['timestamp'] > HALF_TIME_SECONDS) & (data['timestamp'] <= 2 * HALF_TIME_SECONDS), 2 * HALF_TIME_SECONDS))
    for in_half, half_end in halves:
        if in_half.any():
            last = data[in_half].iloc[-1]
            if last['timestamp'] < half_end:
                boxes.append((last['timestamp'] / 60, half_end / 60, not last['own_team'], False))
    # separators at every attempt that isn't the last one of its attack (the last one is the end of the box)
    attempts = _attempts(data)
    separators = list(attempts[attempts['number'] < attempts['attempts'] - 1]['end'] / 60)

    game_minutes = max(60, math.ceil(data['timestamp'].max() / 60)) if not data.empty else 60
    rows = math.ceil(game_minutes / ATTACK_TIMELINE_ROW_MINUTES)
    fig, axes = plt.subplots(rows, 1, figsize=(15, 1.3 * rows), squeeze=False)
    axes = axes[:, 0]
    fig.subplots_adjust(hspace=0.8)

    for row, ax in enumerate(axes):
        # every row gets all boxes, the x range cuts them to the minutes of the row
        # three layers: the boxes, the hatch of the estimated ones (matplotlib draws a hatch in the edge color, so
        # it gets its own layer without an edge) and on top the white gaps between the attacks
        widths = [box[1] - box[0] for box in boxes]
        lefts = [box[0] for box in boxes]
        ax.barh(y=0, height=1, width=widths, left=lefts, color=[ATTACK_TEAMS[box[2]][1] for box in boxes], linewidth=0)
        estimated = [box for box in boxes if box[3]]
        if estimated:
            ax.barh(y=0, height=1,
                    width=[box[1] - box[0] for box in estimated],
                    left=[box[0] for box in estimated],
                    color='none', edgecolor=[ESTIMATED_ATTACK_HATCH_COLORS[box[2]] for box in estimated],
                    hatch=ESTIMATED_ATTACK_HATCH, linewidth=0)
        ax.barh(y=0, height=1, width=widths, left=lefts, color='none', edgecolor=ATTACK_GAP_COLOR, linewidth=1)
        ax.vlines(separators, -0.5, 0.5, color=ATTEMPT_SEPARATOR_COLOR, linewidth=1)

        row_start = row * ATTACK_TIMELINE_ROW_MINUTES
        ax.set_xlim(row_start, row_start + ATTACK_TIMELINE_ROW_MINUTES)
        ax.set_ylim(-0.5, 0.5)
        ax.set_xticks(range(row_start, row_start + ATTACK_TIMELINE_ROW_MINUTES + 1))
        ax.set_yticks([])
        for side in ('left', 'right', 'top'):
            ax.spines[side].set_visible(False)
    axes[-1].set_xlabel("Minute")

    axes[0].legend(handles=[
        Patch(color=OWN_ATTACK_COLOR, label=TEAM_NAME),
        Patch(color=OPPONENT_ATTACK_COLOR, label="Gegner"),
        Patch(facecolor=OWN_ATTACK_COLOR, hatch='|', edgecolor=ATTEMPT_SEPARATOR_COLOR, linewidth=0,
              label="weiße Linie: nächster Wurfversuch im selben Angriff"),
        Patch(facecolor=OPPONENT_ATTACK_COLOR, hatch=ESTIMATED_ATTACK_HATCH,
              edgecolor=ESTIMATED_ATTACK_HATCH_COLORS[False], linewidth=0,
              label="schraffiert: geschätzt (Angriff fehlt in den Daten)"),
    ], loc='lower center', bbox_to_anchor=(0.5, 1.15), ncol=4, frameon=False)

    img_path = os.path.join(OUTPUT_DIR, "plot_attack_timeline.png")
    plt.savefig(img_path, dpi=200, bbox_inches='tight')
    plt.close(fig)

    return Analysis(img_path, title="Ballbesitz / Angriffsdauer")


def seconds_per_attempt(data: pd.DataFrame) -> Analysis:
    """Number of attempts by their time, grouped in steps of ATTEMPT_DURATION_STEP_SECONDS seconds
    ([0, 5), [5, 10), ...), one diagram per team (ours on top), both with the same axes to compare them.
    The time of an attempt goes from the start of the attack or the previous attempt of the attack to the attempt;
    for an attack with one attempt it's the attack time."""

    attempts = _attempts(data)
    step = ATTEMPT_DURATION_STEP_SECONDS
    # steps up to the one with the longest attempt
    end = (math.floor(attempts['duration'].max() / step) + 1) * step if not attempts.empty else step
    steps = list(range(0, end, step))

    fig, axes = plt.subplots(2, 1, figsize=(15, 8), sharex=True, sharey=True)
    fig.subplots_adjust(hspace=0.3)
    for ax, is_own_team in zip(axes, (True, False)):
        team, color = ATTACK_TEAMS[is_own_team]
        seconds = attempts[attempts['own_team'] == is_own_team]['duration']
        counts = [((seconds >= start) & (seconds < start + step)).sum() for start in steps]
        ax.bar([start + step / 2 for start in steps], counts, width=step * 0.8, color=color,
               edgecolor=ATTACK_GAP_COLOR, linewidth=0.5)

        ax.set_title(team, loc='left')
        ax.set_ylabel("Anzahl Wurfversuche")
        ax.grid(axis='y', color='#e5e5e5', linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ('right', 'top'):
            ax.spines[side].set_visible(False)
        # shared x axis: show the seconds below both diagrams
        ax.tick_params(labelbottom=True)

    axes[0].set_xlim(0, end)
    axes[0].set_xticks(range(0, end + 1, step))
    axes[-1].set_xlabel("Sekunden")

    img_path = os.path.join(OUTPUT_DIR, "plot_seconds_per_attempt.png")
    plt.savefig(img_path, dpi=200, bbox_inches='tight')
    plt.close(fig)

    return Analysis(img_path, title="Sekunden pro Wurfversuch")


def _attacks(data: pd.DataFrame) -> pd.DataFrame:
    """One row per attack: own_team, start and end (second the team got the ball and of its last action)
    and estimated."""

    return data.groupby('attack').agg(own_team=('own_team', 'first'), start=('attack_start', 'first'),
                                      end=('timestamp', 'max'), estimated=('attack_estimated', 'first'))


def _attempts(data: pd.DataFrame) -> pd.DataFrame:
    """One row per attempt (action) of the attacks: attack, own_team, number (0 = first attempt of the attack),
    attempts (number of attempts of the attack), start (start of the attack or the previous attempt), end (second of
    the attempt) and duration."""

    actions = data.sort_values(['attack', 'timestamp'], kind='stable')
    by_attack = actions.groupby('attack')['timestamp']
    attempts = pd.DataFrame({
        'attack': actions['attack'],
        'own_team': actions['own_team'],
        'number': by_attack.cumcount(),
        'attempts': by_attack.transform('size'),
        'start': by_attack.shift().fillna(actions['attack_start']),
        'end': actions['timestamp'],
    })
    attempts['duration'] = attempts['end'] - attempts['start']
    return attempts
