import json

import pandas as pd

def parse_json(json_string: str) -> pd.DataFrame:
    raw_data = json.loads(json_string)
    data = pd.DataFrame(raw_data['actions'])

    # sort for time
    data.sort_values('timestamp', inplace=True)

    # handle None values
    data['player'] = ["player undefined" if i is None else i for i in data['player']]
    data['x'] = ['0' if i is None else i for i in data['x']]
    data['y'] = ['0' if i is None else i for i in data['y']]
    data['x'] = data['x'].astype(int)
    data['y'] = data['y'].astype(int)

    # split up into minute and second
    data['minute'] = round(data['timestamp'] / 60, 0).astype(int)
    data['seconds'] = (data['timestamp'] % 60).astype(int)

    # make extra column for nr, name and position
    # FIXME: use existing column and filter dict directly with sth like below
    # formatted_data[formatted_data['player'].apply(lambda x: x['player_name'] == 'Ben Loius Vollert')
    for i in range(0, len(data)):
        if data.loc[i, 'player'] != 'player undefined':
            if not pd.isna(data.loc[i, 'player']['number']):
                data.loc[i, 'number'] = int(data.loc[i, 'player']['number'])
            if not pd.isna(data.loc[i, 'player']['player_name']):
                # some names from the app have spaces around them, the same player can be saved with and without
                # them, without the spaces it is one player in all analyses
                data.loc[i, 'player_name'] = data.loc[i, 'player']['player_name'].strip()
        if i == 0:
            data.loc[i, 'attack_time'] = data.loc[i, 'timestamp']
        else:
            data.loc[i, 'attack_time'] = data.loc[i, 'timestamp'] - data.loc[i - 1, 'timestamp']

    data = data.drop('player', axis=1)
    data.fillna(0, inplace=True)
    data['number'] = data['number'].astype(int)
    data['attack_time'] = data['attack_time'].astype(int)

    return data


def parse_games(source_files: list[tuple[str, bytes]]) -> tuple[pd.DataFrame, list[tuple[str, bytes]]]:
    """Parse the json files (name, content) of several games and merge them into one dataframe.

    Returns the merged data and the files that could be parsed, files that are no valid gamedata are skipped.
    """

    all_data = pd.DataFrame()
    parsed_files = []
    for name, content in source_files:
        try:
            data = parse_json(content.decode("utf-8"))
        except Exception:
            print(f"{name} is not a valid gamedata file")
            continue
        all_data = pd.concat([data, all_data], ignore_index=True)
        parsed_files.append((name, content))

    return all_data, parsed_files
