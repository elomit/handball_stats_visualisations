import pandas as pd
import matplotlib.pyplot as plt
import json

PATH = r"250222_hbf2_rehberge.json"
missed_shots_list = ['Block', 'Verworfen', 'Gehalten']

# import data and format df
def import_and_format_df(PATH):
    with open(PATH) as json_data:
        data = json.load(json_data)
        raw_data = pd.DataFrame(data['actions'])
    
    # sort for time
    raw_data.sort_values('timestamp', inplace=True)
    
    # handle None values
    raw_data['player'] = ["player undefined" if i is None else i for i in raw_data['player']]
    raw_data['x'] = ['0' if i is None else i for i in raw_data['x']]
    raw_data['y'] = ['0' if i is None else i for i in raw_data['y']]
    raw_data['x'] = raw_data['x'].astype(int)
    raw_data['y'] = raw_data['y'].astype(int)

    # split up into minute and second
    raw_data['minute'] = round(raw_data['timestamp'] / 60, 0).astype(int)
    raw_data['seconds'] = (raw_data['timestamp'] / 60 % 1 * 60).astype(int)

    # make extra column for nr, name and position
    # FIXME: use existing column and filter dict directly with sth like below
    # formatted_data[formatted_data['player'].apply(lambda x: x['player_name'] == 'Ben Loius Vollert')
    raw_data['player_name'] = ''
    raw_data['number'] = 0
    raw_data['position'] = ''
    for i in range(0,len(raw_data)):
        if raw_data.loc[i,'player'] != 'player undefined':
            if not pd.isna(raw_data.loc[i,'player']['number']):
                raw_data.loc[i,'number'] = int(raw_data.loc[i,'player']['number'])
            if not pd.isna(raw_data.loc[i,'player']['player_name']):
                raw_data.loc[i,'player_name'] = raw_data.loc[i,'player']['player_name']
            if not pd.isna(raw_data.loc[i,'player']['position']):
                raw_data.loc[i,'position'] = raw_data.loc[i,'player']['position']
        if i == 0:
            raw_data.loc[i,'attack_time'] = raw_data.loc[i,'timestamp']
        else:
            raw_data.loc[i,'attack_time'] = raw_data.loc[i,'timestamp'] - raw_data.loc[i-1,'timestamp']

    raw_data.fillna(0, inplace=True)
    raw_data['number'] = raw_data['number'].astype(int)
    raw_data['attack_time'] = raw_data['attack_time'].astype(int)

    return raw_data


def shot_visualisation(formatted_data, team, player=None):
    """Visualisa shots."""
    # FIXME: Make heatmap instead of normal plot
    
    # check whether visualisation for attack or defense (keeper)
    if team == 'handballfreunde':
        df_shots = formatted_data[formatted_data['own_team'] == True]
        success_color = 'green'
        fail_color = 'red'
    else:
        df_shots = formatted_data[formatted_data['own_team'] == False]
        success_color = 'red'  # for keeper a missed shot is good
        fail_color = 'green'

    # check whether for entire team or specific player
    if player is None:
        df_score = df_shots[~(df_shots['type'].isin(missed_shots_list))]
        df_miss = df_shots[(df_shots['type'].isin(missed_shots_list))]
    else:
        df_score = df_shots[(df_shots['player_name'] == player) & ~(df_shots['type'].isin(missed_shots_list))]
        df_miss = df_shots[(df_shots['player_name'] == player) & (df_shots['type'].isin(missed_shots_list))]

    # calculate quote
    scored = len(df_score)
    missed = len(df_miss)
    shots = missed + scored
    try:
        if team == 'handballfreunde':
            quote = round(( scored / (shots) * 100), 2)
        else:
            quote = round(( missed / (shots) * 100), 2)
    except:
        quote = "0"

    # plot one graph
    plt.figure()
    # always show entire goal (15x10)
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.plot(df_miss["x"], df_miss["y"], marker='o', linestyle='none', color=fail_color, ms=17,
                label='Verworfen')
    plt.plot(df_score["x"], df_score["y"], marker='o', linestyle='none', color=success_color, ms=15,
                label='Treffer')
    # set the title and labels
    if player is None:
        plt.title(
                f"Wurfanalyse für Handballfreunde: Würfe =  {shots}, Teffer = {scored}, Quote = {quote}%"
                )
    else:
        if team == 'handballfreunde':
            plt.title(
                        f"Wurfanalyse für {player}: Würfe =  {shots}, Teffer = {scored}, Quote = {quote}%"
                        )
        else:
            plt.title(
                        f"Keeperanalyse für {player}: Würfe =  {shots}, Gehalten = {missed}, Quote = {quote}%"
                        )


## main
formatted_data = import_and_format_df(PATH)
shot_visualisation(formatted_data, 'handballfreunde')

for player in formatted_data['player_name'].unique():

    # sort out keepers
    if 'TW' not in list(formatted_data[formatted_data['player_name'] == player]['position']):
        shot_visualisation(formatted_data, 'handballfreunde', player)
    else:
        shot_visualisation(formatted_data, 'opponent', player)