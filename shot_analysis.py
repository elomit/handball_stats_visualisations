import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from Analysis import Analysis
from constants import MISSED_SHOTS_FIELDS, OUTPUT_DIR, SHOT_FIELDS, GOALIE_SHOTS_FIELDS, SCORED_SHOTS_FIELDS

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

    all_shots = data[data['type'].isin(GOALIE_SHOTS_FIELDS)]

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

def create_shots_graph(shots: pd.DataFrame, is_keeper: bool, player_name: str = None, location: str = None) -> str:

    if player_name is not None:
        shots = shots[shots['player_name'] == player_name]

    scored_shots = shots[shots['type'].isin(SCORED_SHOTS_FIELDS)]
    missed_shots = shots[shots['type'].isin(MISSED_SHOTS_FIELDS)]
    dreher_shots = shots[(shots['x'] == -2) & (shots['y'] == -2)]
    heber_shots = shots[(shots['x'] == -1) & (shots['y'] == -1)]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])

    # Add Title
    img_name, title = create_plot_title_and_name(player_name, location, is_keeper, len(scored_shots), len(missed_shots))
    fig.suptitle(title)

    # Add Heatmaps
    plot_shots = shots[
        shots['x'].notna() &
        shots['y'].notna() &
        (shots['x'] != -2) &
        (shots['y'] != -2) &
        (shots['x'] != -1) &
        (shots['y'] != -1)
    ]

    miss_label = 'Gehalten' if is_keeper else 'Verworfen'
    goal_label = 'Tore' if is_keeper else 'Treffer'

    for ax, shots_subset, cmap, label in [
        (axes[0], missed_shots, 'Greens' if is_keeper else 'Reds', miss_label),
        (axes[1], scored_shots, 'Reds' if is_keeper else 'Greens', goal_label),
    ]:
        ax.set_xlim(0, 100)
        ax.set_xticks(())
        ax.set_ylim(0, 100)
        ax.set_yticks(())
        ax.set_aspect('equal', adjustable='box')
        ax.set_title(label)

        if not plot_shots.empty and not shots_subset.empty:
            bins = 100
            x_edges = np.linspace(0, 100, bins + 1)
            y_edges = np.linspace(0, 100, bins + 1)
            x_centers = (x_edges[:-1] + x_edges[1:]) / 2
            y_centers = (y_edges[:-1] + y_edges[1:]) / 2
            x_grid, y_grid = np.meshgrid(x_centers, y_centers)

            sigma = 5
            blur_radius = 6
            hotspot_map = np.zeros((bins, bins), dtype=float)
            count_map = np.zeros((bins, bins), dtype=float)

            for _, shot in shots_subset.iterrows():
                x = float(shot['x'])
                y = float(shot['y'])
                if np.isnan(x) or np.isnan(y):
                    continue
                influence = np.exp(-((x_grid - x) ** 2 + (y_grid - y) ** 2) / (2 * sigma ** 2))
                hotspot_map += influence
                count_map += ((x_grid - x) ** 2 + (y_grid - y) ** 2 <= blur_radius ** 2).astype(float)

            if hotspot_map.max() > 0:
                hotspot_map = hotspot_map / hotspot_map.max()

            ax.pcolor(
                x_edges,
                y_edges,
                hotspot_map,
                cmap=cmap,
                alpha=0.85,
                vmin=0,
                vmax=1,
            )

            # Build list of shot coordinates for contribution checks
            shot_coords = []
            for _, shot in shots_subset.iterrows():
                sx = shot['x']
                sy = shot['y']
                try:
                    sx = float(sx)
                    sy = float(sy)
                except Exception:
                    continue
                if np.isnan(sx) or np.isnan(sy):
                    continue
                shot_coords.append((sx, sy))

            mask = count_map > 0
            visited = np.zeros_like(mask, dtype=bool)
            neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

            def get_region(i, j):
                stack = [(i, j)]
                region = []
                while stack:
                    ci, cj = stack.pop()
                    if ci < 0 or ci >= bins or cj < 0 or cj >= bins or visited[ci, cj] or not mask[ci, cj]:
                        continue
                    visited[ci, cj] = True
                    region.append((ci, cj))
                    for di, dj in neighbors:
                        stack.append((ci + di, cj + dj))
                return region

            # For each connected region, count unique shots contributing (by overlap with shot blur)
            for i in range(bins):
                for j in range(bins):
                    if mask[i, j] and not visited[i, j]:
                        region = get_region(i, j)

                        # region mask for quick lookup
                        region_mask = np.zeros_like(mask, dtype=bool)
                        for (ri, rj) in region:
                            region_mask[ri, rj] = True

                        contributing = 0
                        for (sx, sy) in shot_coords:
                            # cells where this shot influences
                            shot_influence = ((x_grid - sx) ** 2 + (y_grid - sy) ** 2) <= (blur_radius ** 2)
                            # if any influenced cell is inside region, this shot contributes
                            if np.any(shot_influence & region_mask):
                                contributing += 1

                        if contributing == 0:
                            continue

                        # choose strongest cell for label placement
                        best_i, best_j = max(region, key=lambda cell: hotspot_map[cell])
                        count = int(round(contributing))
                        x_center = x_centers[best_j]
                        y_center = y_centers[best_i]
                        text_color = 'white' if hotspot_map[best_i, best_j] > 0.5 else 'black'
                        fontsize = 6 if count < 10 else 5
                        ax.text(
                            x_center,
                            y_center,
                            str(count),
                            ha='center',
                            va='center',
                            fontsize=fontsize,
                            color=text_color,
                            alpha=0.95,
                        )

    # Add Textbox with Heber and Dreher
    textbox = ""
    if not dreher_shots.empty:
        textbox = get_trickshot_text(dreher_shots, is_keeper, "Dreher")
    if not heber_shots.empty:
        textbox = get_trickshot_text(heber_shots, is_keeper, "Heber")

    if len(textbox) > 0:
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.15)
        axes[0].text(0.0175, 0.975, textbox, transform=axes[0].transAxes, fontsize=10,
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
