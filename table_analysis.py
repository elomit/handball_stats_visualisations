import math
import os

import pandas as pd
from matplotlib import pyplot as plt

from Analysis import Analysis
from constants import OUTPUT_DIR, MISSED_SHOTS_FIELDS, SCORED_SHOTS_FIELDS, SHOT_FIELDS, \
	QUOTE_TABLE_MAX_ROWS, QUOTE_TABLE_COLUMNS, TABLE_MAX_SCALE


def tables_to_image(tables: list[tuple[str, pd.DataFrame]], path: str, figsize: tuple, loc: str = 'center',
                    font_size: float = None):
    """(title, dataframe) side by side in one image, to be able to paste them into the pdf.
    loc is the position of the tables in their part of the image, e.g. 'upper center' to align their tops.
    font_size is a fixed font size with the columns as wide as their texts, by default the font gets smaller
    until the texts fit into the columns. The image then gets as wide as the tables (figsize only gives the height).
    Column names can have more lines (with \\n)."""

    count = len(tables)
    drawn_tables = []

    fig, ax = plt.subplots(1, count, figsize=figsize)

    # Make ax always iterable
    if count == 1:
        ax = [ax]

    for i, (title, dataframe) in enumerate(tables):
        ax[i].axis('off')
        ax[i].set_title(title)
        table = ax[i].table(
            cellText=dataframe.values,
            colLabels=dataframe.columns,
            cellLoc='center',
            loc=loc
        )
        if font_size:
            table.auto_set_font_size(False)
            table.set_fontsize(font_size)
            table.auto_set_column_width(range(len(dataframe.columns)))
            table.scale(1, 1.2)
        drawn_tables.append(table)
        header_lines = max(str(column).count('\n') + 1 for column in dataframe.columns)

        # the header and the total rows (a cell with 'Gesamt') are bold
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.get_text().set_fontweight('bold')
                cell.set_height(cell.get_height() * header_lines)
            elif 'Gesamt' in dataframe.iloc[row - 1].values:
                cell.get_text().set_fontweight('bold')

    if font_size:
        _place_side_by_side(fig, ax, drawn_tables)
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)


def _place_side_by_side(fig, axes: list, tables: list, gap: float = 0.25):
    """Make every axes as wide as its table and the figure as wide as all of them with gap (inches) between them,
    so tables with columns as wide as their texts don't overlap."""

    renderer = fig.canvas.get_renderer()
    widths = [table.get_window_extent(renderer).width / fig.dpi for table in tables]
    total_width = sum(widths) + gap * (len(widths) - 1)
    fig.set_size_inches(total_width, fig.get_size_inches()[1])

    x = 0
    for axes, width in zip(axes, widths):
        position = axes.get_position()
        axes.set_position([x / total_width, position.y0, width / total_width, position.height])
        x += width + gap


def block_table(data: pd.DataFrame) -> Analysis | None:
	"""Our blocks (shots of the opponent blocked by our players): the total first, then per player the number
	of blocks and the positions the blocked shots came from, most blocks first. None if there were no blocks."""

	blocks = data[~data['own_team'] & (data['type'] == 'Block')]
	if blocks.empty:
		return None

	rows = [(player, len(player_blocks), _positions_text(player_blocks))
			for player, player_blocks in blocks.groupby('player_name')]
	rows.sort(key=lambda row: (-row[1], row[0]))
	rows.insert(0, ('Gesamt', len(blocks), _positions_text(blocks)))
	table = pd.DataFrame(rows, columns=['Spieler', 'Blocks', 'Wurf von'])

	img_path = os.path.join(OUTPUT_DIR, "block_table.png")
	# about 0.2 inch per row (with the header), so there is no empty space below the table
	tables_to_image([('', table)], img_path, figsize=(4, 0.2 * (len(table) + 1)), loc='upper center', font_size=9)
	return Analysis(img_path, title="Blocks", max_scale=TABLE_MAX_SCALE)


def _positions_text(actions: pd.DataFrame) -> str:
	"""Positions of the actions with their count, most first, e.g. 'RM (9M) 2, RL (9M) 1'."""

	return ", ".join(f"{location} {count}" for location, count in actions['location'].value_counts().items())


def player_position_summary_table(data: pd.DataFrame) -> Analysis:
	"""Render a player-level quote summary for total and per position."""

	# get shots from own team 
	shots = data[data['own_team']]
	shots = shots[shots['type'].isin(SHOT_FIELDS)]

	# destinguish miss and score
	scored = shots[shots['type'].isin(SCORED_SHOTS_FIELDS)]
	missed = shots[shots['type'].isin(MISSED_SHOTS_FIELDS)]

	# group by player and position
	scored_by_player_position = scored.groupby(['player_name', 'location']).size().rename('Treffer')
	missed_by_player_position = missed.groupby(['player_name', 'location']).size().rename('Verworfen')

	# put together scores and missed shots
	summary = pd.concat([scored_by_player_position, missed_by_player_position], axis=1).fillna(0)
	summary = summary.reset_index()

	# total per player
	totals = summary.groupby('player_name')[['Treffer', 'Verworfen']].sum().reset_index()
	totals['location'] = 'Gesamt'

	# combine totals and summary
	combined = pd.concat([totals, summary], ignore_index=True, sort=False)
	combined['Treffer'] = combined['Treffer'].astype(int)
	combined['Verworfen'] = combined['Verworfen'].astype(int)

	# add column for quote
	combined['Quote in % (Treffer/Würfe)'] = (combined['Treffer'] / (combined['Treffer'] + combined['Verworfen']) * 100).round(0)
	combined['Quote in % (Treffer/Würfe)'] = combined.apply(
		lambda row: f"{int(row['Quote in % (Treffer/Würfe)'])} ({row['Treffer']}/{int(row['Treffer'] + row['Verworfen'])})",
		axis=1
	)

	# format table
	combined = combined.rename(columns={'player_name': 'Spieler', 'location': 'Position'})
	combined['PositionOrder'] = combined['Position'].apply(lambda x: 0 if x == 'Gesamt' else 1)
	combined = combined.sort_values(['Spieler', 'PositionOrder', 'Position'], ascending=[True, True, True])
	combined = combined[['Spieler', 'Position', 'Quote in % (Treffer/Würfe)']]
	combined = combined.rename(columns={'Quote in % (Treffer/Würfe)': 'Quote in %\n(Treffer/Würfe)'})

	# columns side by side, several pages if they don't fit on one: the first page is this analysis,
	# the following pages are sub analyses without title (no entry in the index)
	columns = _split_into_columns(combined)
	analysis = None
	for page_number, start in enumerate(range(0, len(columns), QUOTE_TABLE_COLUMNS)):
		page_columns = columns[start:start + QUOTE_TABLE_COLUMNS]
		img_name = 'player_summary_table.png' if page_number == 0 else f'player_summary_table_{page_number + 1}.png'
		img_path = os.path.join(OUTPUT_DIR, img_name)
		tables_to_image([('', column) for column in page_columns], img_path, figsize=(2.5 * len(page_columns), 2.75),
						loc='upper center', font_size=9)
		if analysis is None:
			analysis = Analysis(img_path, width=8, height=5, top=2, title="Quote pro Spieler", max_scale=TABLE_MAX_SCALE)
		else:
			analysis.add_analysis(Analysis(img_path, max_scale=TABLE_MAX_SCALE))

	return analysis


def _split_into_columns(table: pd.DataFrame) -> list[pd.DataFrame]:
	"""Split the table (sorted by player) into as few pages with columns of at most QUOTE_TABLE_MAX_ROWS rows
	as possible, the columns with about the same length. The rows of a player stay together (a player with more rows gets a column alone),
	the player name is only shown in the first row of the player."""

	if table.empty:
		return [table]

	players = [rows for _, rows in table.groupby('Spieler', sort=False)]
	sizes = [len(rows) for rows in players]
	column_count = _count_columns(sizes)
	# more than one page: every page gets the same number of columns (shorter ones), not one column on the last page
	if column_count > QUOTE_TABLE_COLUMNS:
		column_count = min(math.ceil(column_count / QUOTE_TABLE_COLUMNS) * QUOTE_TABLE_COLUMNS, len(players))

	# a player is added to the column if that brings it closer to its share of the remaining rows
	# (remaining rows / remaining columns), or if the remaining players wouldn't fit into the remaining columns
	columns = []
	for i, rows in enumerate(players):
		if columns:
			column_rows = sum(len(player_rows) for player_rows in columns[-1])
			share = (column_rows + sum(sizes[i:])) / (column_count - len(columns) + 1)
			fits = column_rows + sizes[i] <= QUOTE_TABLE_MAX_ROWS
			closer = abs(column_rows + sizes[i] - share) <= abs(column_rows - share)
			rest_fits = _count_columns(sizes[i:]) <= column_count - len(columns)
			if fits and (closer or not rest_fits):
				columns[-1].append(rows)
				continue
		columns.append([rows])

	result = []
	for column in columns:
		column = pd.concat(column)
		column.loc[column['Spieler'].duplicated(), 'Spieler'] = ''
		result.append(column)
	return result


def _count_columns(sizes: list[int]) -> int:
	"""Fewest columns of at most QUOTE_TABLE_MAX_ROWS rows for players with these numbers of rows (in this order):
	filling every column as far as possible."""

	count, column_rows = 0, 0
	for size in sizes:
		if count and column_rows + size <= QUOTE_TABLE_MAX_ROWS:
			column_rows += size
		else:
			count += 1
			column_rows = size
	return count
