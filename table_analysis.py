import os

import pandas as pd
from matplotlib import pyplot as plt

from Analysis import Analysis
from constants import OUTPUT_DIR, MISSED_SHOTS_FIELDS, SCORED_SHOTS_FIELDS


def game_analysis_table(data: pd.DataFrame, mapping) -> Analysis:

	own_shots = data[data['own_team']]
	opponent_shots = data[~data['own_team']]

	own_scored = own_shots[own_shots['type'].isin(SCORED_SHOTS_FIELDS)]['location'].value_counts().reset_index()
	own_missed = own_shots[own_shots['type'].isin(MISSED_SHOTS_FIELDS)]['location'].value_counts().reset_index()
	opponents_scored = opponent_shots[opponent_shots['type'].isin(SCORED_SHOTS_FIELDS)]['location'].value_counts().reset_index()
	opponents_missed = opponent_shots[opponent_shots['type'].isin(MISSED_SHOTS_FIELDS)]['location'].value_counts().reset_index()

	# differentiate per position shot and miss
	# TODO geht das auch einfacher?
	own_scored.rename(columns={"location": "Position", "count": "Treffer"}, inplace=True)
	own_missed.rename(columns={"location": "Position", "count": "Verworfen"}, inplace=True)
	opponents_scored.rename(columns={"location": "Position", "count": "Treffer"}, inplace=True)
	opponents_missed.rename(columns={"location": "Position", "count": "Verworfen"}, inplace=True)

	own_analysis = own_scored.merge(own_missed, how='outer', on='Position')
	opponent_analysis = opponents_scored.merge(opponents_missed, how='outer', on='Position')

	# Add missing positions to df
	positions_base_dataframe = pd.DataFrame(list(mapping.values()), columns=["Position"]) # TODO wenn wir translations für positionen haben, daraus generieren statt hardcoded
	own_analysis = own_analysis.merge(positions_base_dataframe, how='right', on='Position')
	opponent_analysis = opponent_analysis.merge(positions_base_dataframe, how='right', on='Position')

	own_analysis.fillna(0, inplace=True)
	opponent_analysis.fillna(0, inplace=True)

	own_analysis.sort_values('Position', ascending=True)
	own_analysis.set_index('Position', inplace=True)
	opponent_analysis.sort_values('Position', ascending=True)
	opponent_analysis.set_index('Position', inplace=True)

	# calculate quote per position
	own_analysis['Quote in %'] = get_quote(own_analysis)
	opponent_analysis['Quote in %'] = get_quote(opponent_analysis)

	# TODO quote can be NaN - but this is not clean either
	own_analysis.fillna(0, inplace=True)
	opponent_analysis.fillna(0, inplace=True)

	own_analysis = own_analysis.astype(int)
	opponent_analysis = opponent_analysis.astype(int)
	own_analysis.reset_index(inplace=True)
	opponent_analysis.reset_index(inplace=True)

	# sort values to show most Treffer on top
	own_analysis.sort_values('Treffer', ascending=False, inplace=True)
	opponent_analysis.sort_values('Treffer', ascending=False, inplace=True)

	# save table
	img_path = os.path.join(OUTPUT_DIR, "game_table_analysis.png")
	dataframes_to_image({"Würfe Handballfreunde": own_analysis, "Würfe Gegner": opponent_analysis}, img_path)

	return Analysis(img_path, width=8, height=2.5, top=2.5)


def get_quote(own_analysis):
	return round(own_analysis['Treffer'] / (own_analysis['Treffer'] + own_analysis['Verworfen']) * 100, 2)


def dataframes_to_image(dataframes: dict[str, pd.DataFrame], path: str):
	# Convert pandas dataframe to image to be able to paste it into ppt.
	count = len(dataframes.values())
	fig, ax = plt.subplots(1, count,figsize=(10, 2.75)) # TODO dynamic rows+columns

	i = 0
	for analysis in dataframes.keys():
		ax[i].axis('off')
		ax[i].set_title(analysis)
		ax[i].table(cellText=dataframes[analysis].values, colLabels=dataframes[analysis].columns, cellLoc='center', loc='center')
		i += 1

	plt.savefig(path, bbox_inches='tight')
	plt.close(fig)