import json

import pandas as pd

from constants import SCORED_SHOTS_FIELDS, HALF_TIME_SECONDS, COUNTER_ATTACK_LOCATION, ESTIMATED_COUNTER_ATTACK_SECONDS


def parse_json(json_string: str) -> pd.DataFrame:
    raw_data = json.loads(json_string)
    data = pd.DataFrame(raw_data['actions'])

    # sort for time, the row numbers follow the time (the app doesn't always save the actions in time order)
    data = data.sort_values('timestamp', kind='stable', ignore_index=True)

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

    data = data.drop('player', axis=1)
    data.fillna(0, inplace=True)
    data['number'] = data['number'].astype(int)
    _add_attacks(data)

    return data


def _add_attacks(data: pd.DataFrame) -> None:
    """Columns for the attacks of the game (sorted by time): attack (number of the attack),
    attack_start (second the team got the ball) and attack_estimated (True if attack_start is estimated).

    An attack goes on as long as the same team has the actions (e.g. a shot is saved, the team gets the rebound).
    After a goal the ball always goes to the opponent: if the same team has the next action, the action of the opponent
    is missing in the data and the start of the new attack is estimated (see ESTIMATED_COUNTER_ATTACK_SECONDS).
    Each half starts a new attack.
    """

    attacks, starts, estimated = [], [], []
    attack, start, is_estimated = -1, 0, False
    previous = None
    for action in data.itertuples():
        # an action at exactly 30:00 is the last one of the first half (the clock stops there)
        half_start = HALF_TIME_SECONDS if action.timestamp > HALF_TIME_SECONDS else 0
        # the first action of the game or of the second half (the previous one was in the first half,
        # up to exactly 30:00) starts a new attack at the start of the half
        if previous is None or (half_start > 0 and previous.timestamp <= half_start):
            attack, start, is_estimated = attack + 1, half_start, False
        elif action.own_team != previous.own_team:
            attack, start, is_estimated = attack + 1, previous.timestamp, False
        elif previous.type in SCORED_SHOTS_FIELDS:
            since_goal = action.timestamp - previous.timestamp
            if action.location == COUNTER_ATTACK_LOCATION:
                duration = min(ESTIMATED_COUNTER_ATTACK_SECONDS, since_goal)
            else:
                duration = since_goal / 2
            attack, start, is_estimated = attack + 1, action.timestamp - duration, True
        attacks.append(attack)
        starts.append(start)
        estimated.append(is_estimated)
        previous = action

    data['attack'] = attacks
    data['attack_start'] = starts
    data['attack_estimated'] = estimated


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
        # the attack numbers stay unique in the merged data
        if not all_data.empty:
            data['attack'] += all_data['attack'].max() + 1
        all_data = pd.concat([data, all_data], ignore_index=True)
        parsed_files.append((name, content))

    return all_data, parsed_files
