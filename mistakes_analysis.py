import os

import pandas as pd
from matplotlib import pyplot as plt

from Analysis import Analysis
from constants import OUTPUT_DIR
from table_analysis import dataframes_to_image  # TODO: Make utils function


def mistake_analysis_table(data: pd.DataFrame, mapping) -> Analysis:

	own_team_df = data[data['own_team']]

	own_technical_mistakes = own_team_df[own_team_df['type'] == 'Fehler']['location'].value_counts().reset_index()
	own_ball_lost = own_team_df[own_team_df['type'] == 'Ballverlust']['location'].value_counts().reset_index()

	# differentiate per position shot and miss
	# TODO geht das auch einfacher?
	own_technical_mistakes.rename(columns={"location": "Position", "count": "Fehler"}, inplace=True)
	own_ball_lost.rename(columns={"location": "Position", "count": "Ballverlust"}, inplace=True)
	own_analysis = own_technical_mistakes.merge(own_ball_lost, how='outer', on='Position')

	# Add missing positions to df
	positions_base_dataframe = pd.DataFrame(list(mapping.values()), columns=["Position"]) # TODO wenn wir translations für positionen haben, daraus generieren statt hardcoded
	own_analysis = own_analysis.merge(positions_base_dataframe, how='right', on='Position')

	own_analysis.fillna(0, inplace=True)
	own_analysis.sort_values('Position', ascending=True)
	own_analysis.set_index('Position', inplace=True)
	own_analysis = own_analysis[~((own_analysis["Ballverlust"] == 0) & (own_analysis["Fehler"] == 0))]
	own_analysis = own_analysis.astype(int)
	own_analysis.reset_index(inplace=True)

	# sort values to show most Treffer on top
	total_technical_mistakes = own_analysis["Fehler"].sum()
	total_ball_lost = own_analysis["Ballverlust"].sum()
	if total_technical_mistakes >= total_ball_lost:
		own_analysis.sort_values('Fehler', ascending=False, inplace=True)
	else:
		own_analysis.sort_values('Ballverlust', ascending=False, inplace=True)
		own_analysis = own_analysis[["Position", "Ballverlust", "Fehler"]]
	own_analysis.rename(columns={
			"Fehler": f'Technische Fehler: {total_technical_mistakes}', 
			"Ballverlust": f"Ballverluste: {total_ball_lost}"
		},inplace=True)

	# save table
	img_path = os.path.join(OUTPUT_DIR, "mistake_table_analysis.png")
	dataframes_to_image({"Fehleranalyse": own_analysis}, img_path)

	return Analysis(img_path, width=8, height=2.5, top=2.5)
