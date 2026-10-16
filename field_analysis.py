"""Shows the shots per position on a handball pitch instead of a table."""

import colorsys
import math
import os

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import Polygon, Rectangle

from Analysis import Analysis, safe_file_name
from colors import readable_text_color, GOOD_COLOR, BAD_COLOR, TEXT_LIGHTNESS, EMPTY_COLOR, PITCH_LINE_COLOR, LINE_COLOR, GOAL_COLOR, \
    COUNT_MIN_SHARE, WHITE
from constants import OUTPUT_DIR, MISSED_SHOTS_FIELDS, SCORED_SHOTS_FIELDS, GOOD_QUOTE, DEFAULT_GOOD_QUOTE, TEAM_NAME, \
    MIRROR_OPPONENT


# region Pitch settings
# pitch size in meters: x along the pitch, y across (-10 to 10)
HALF_WIDTH = 10
GOAL_HALF_WIDTH = 1.5
# the goal is drawn bigger than in reality so it is easier to see (the 6m/9m lines use the real size)
GOAL_DRAW_HALF_WIDTH = GOAL_HALF_WIDTH * 4 / 3
GOAL_DRAW_DEPTH = GOAL_DRAW_HALF_WIDTH
# distances of the drawn lines from the goal; not to scale: the 9m line is further out than in reality,
# so the labels fit into the sectors between 6m and 9m
SIX_M = 6
NINE_M = 11
# the sectors behind 9m are a bit less deep than the ones between 6m and 9m
OUTER_M = NINE_M + (NINE_M - SIX_M) * 0.9
# only the part of each half up to 1m behind the sectors is drawn,
# the two cut halves are placed next to each other with a small gap in between
SHOWN_LENGTH = OUTER_M + 1
GAP = 1.5
# one half with its goal, the halves face the same way (goal on the left) unless a half is mirrored
DRAWN_HALF_LENGTH = GOAL_DRAW_DEPTH + SHOWN_LENGTH
# both halves with the gap, the drawing is centered around x = 0
TOTAL_LENGTH = 2 * DRAWN_HALF_LENGTH + GAP

# the borders between the middle and the back court sectors don't start in the goal center, but are lines
# only slightly tilted from the long axis of the pitch, so the middle sectors are not too narrow near the goal:
# (distance from the long axis at the goal line, tilt in degrees from the long axis), attacker's right is positive
RIGHT_MIDDLE_BORDER = (2.6, 8)
LEFT_MIDDLE_BORDER = (-RIGHT_MIDDLE_BORDER[0], -RIGHT_MIDDLE_BORDER[1])
# angle of the borders between the wings and the back court sectors between 6m and 9m
RIGHT_WING_BORDER = 35
LEFT_WING_BORDER = 180 - RIGHT_WING_BORDER

# sectors as (border from, border to, distance from, distance to)
# a border is either one of the lines above or an angle in degrees seen from the goal center,
# 0 = right goal line, 180 = left goal line (view of the attacker)
# distance is the same as for the 6m/9m lines (distance to the goal)
SECTORS = {
    # inside the 6m goal area
    "KM": (90, 180, 0, SIX_M),
    "K": (0, 90, 0, SIX_M),
    # between 6m and 9m
    "LA": (LEFT_WING_BORDER, 180, SIX_M, NINE_M),
    "L": (LEFT_MIDDLE_BORDER, LEFT_WING_BORDER, SIX_M, NINE_M),
    "M": (90, LEFT_MIDDLE_BORDER, SIX_M, NINE_M),
    "7M": (RIGHT_MIDDLE_BORDER, 90, SIX_M, NINE_M),
    "R": (RIGHT_WING_BORDER, RIGHT_MIDDLE_BORDER, SIX_M, NINE_M),
    "RA": (0, RIGHT_WING_BORDER, SIX_M, NINE_M),
    # behind 9m
    "RL": (LEFT_MIDDLE_BORDER, 180, NINE_M, OUTER_M),
    "RM": (RIGHT_MIDDLE_BORDER, LEFT_MIDDLE_BORDER, NINE_M, OUTER_M),
    "RR": (0, RIGHT_MIDDLE_BORDER, NINE_M, OUTER_M),
}
# endregion

# region Fonts
LABEL_FONT_SIZE = 11
TITLE_FONT_SIZE = LABEL_FONT_SIZE * 16 / 11
LEGEND_FONT_SIZE = LABEL_FONT_SIZE * 12 / 11
# endregion

# region Starting methods
def field_shot_analysis(data: pd.DataFrame, mapping) -> Analysis:
    """Visualise shots and quote per position on a pitch: own shots on the left goal, opponent shots on the right goal."""

    own_stats, opponent_stats, _ = _team_stats(data, mapping)
    good_quotes = _good_quotes(mapping)

    return _field_plot(
        _quote_half(own_stats, f"Würfe {TEAM_NAME}", good_quotes, inverted=False),
        _quote_half(opponent_stats, "Würfe Gegner", good_quotes, inverted=True, mirrored=MIRROR_OPPONENT),
        mapping,
        legend=f"Grün = gut für {TEAM_NAME} (eigene Quote ab Richtwert, Gegner darunter), Rot = schlecht"
               "  ·  Kräftiger = weiter weg vom Richtwert\n" + _good_quote_text(good_quotes),
        file_name="field_shot_analysis.png",
        title="Wurfquote pro Position")


def field_shot_count_analysis(data: pd.DataFrame, mapping) -> Analysis:
    """Visualise only the amount of shots per position on a pitch: white = no shots, pitch line blue = most shots."""

    own_stats, opponent_stats, max_shots = _team_stats(data, mapping)

    return _field_plot(
        _count_half(own_stats, f"Würfe {TEAM_NAME}", max_shots),
        _count_half(opponent_stats, "Würfe Gegner", max_shots, mirrored=MIRROR_OPPONENT),
        mapping,
        legend=f"Anzahl Würfe pro Position  ·  Weiß = keine Würfe, Blau = {max_shots} Würfe (Maximum im Spiel)",
        file_name="field_shot_count_analysis.png",
        title="Würfe pro Position")


def player_field_analysis(shots: pd.DataFrame, mapping, player: str, is_keeper: bool = False) -> Analysis:
    """Quote (left) and amount of shots (right) per position of one player on one page.

    For a keeper, shots are the shots on his goal and the quote is the quote of saved shots.
    """

    stats = _shots_per_position(shots[shots['player_name'] == player], mapping)
    max_shots = max(stats['Würfe'].max(), 1)
    good_quotes = _good_quotes(mapping)
    quote_name = "Quote"
    # the keeper sees the shots of the opponent, so both halves are mirrored like the opponent half of the team plots
    mirrored = is_keeper and MIRROR_OPPONENT

    if is_keeper:
        # a saved shot counts for the keeper, so the good quote is the opposite of the one of the shooter
        stats['Treffer'] = stats['Würfe'] - stats['Treffer']
        good_quotes = {name: 1 - quote for name, quote in good_quotes.items()}
        quote_name = "Paraden"

    return _field_plot(
        _quote_half(stats, quote_name, good_quotes, inverted=False, mirrored=mirrored),
        _count_half(stats, "Würfe", max_shots, mirrored=mirrored),
        mapping,
        legend=f"Links: Grün = {quote_name} ab Richtwert, Rot = darunter, kräftiger = weiter weg vom Richtwert"
               f"  ·  Rechts: Weiß = keine Würfe, Blau = {max_shots} Würfe\n" + _good_quote_text(good_quotes),
        file_name=f"field_{'keeper' if is_keeper else 'player'}_{safe_file_name(player)}.png",
        title=player)


def mistake_field_analysis(data: pd.DataFrame, mapping) -> Analysis:
    """Own mistakes per position on a pitch: ball losses (bad passes) on the left, technical mistakes on the right."""

    stats = _mistakes_per_position(data[data['own_team']], mapping)
    # same scale for both halves to make them comparable
    max_mistakes = max(stats.max().max(), 1)

    return _field_plot(
        _count_half(stats, "Ballverluste", max_mistakes, column='Ballverlust'),
        _count_half(stats, "Technische Fehler", max_mistakes, column='Fehler'),
        mapping,
        legend="Ballverluste = Fehlpass, nicht gefangen  ·  Technische Fehler = Schritte, 2Mal, Stürmerfoul\n"
               f"Weiß = keine Fehler, Blau = {max_mistakes} Fehler (Maximum im Spiel)",
        file_name="field_mistake_analysis.png",
        title="Fehleranalyse")


def _quote_half(stats: pd.DataFrame, title: str, good_quotes: dict, inverted: bool, mirrored: bool = False) -> dict:
    """Half of the pitch colored by the quote compared to the good quote of the position (inverted for the opponent)."""

    scored = stats['Treffer'].sum()
    shots = stats['Würfe'].sum()
    return dict(
        title=f"{title}: {scored}/{shots} ({_quote_text(scored, shots)})",
        sector_color=lambda name: _sector_color(stats, name, good_quotes[name], inverted),
        sector_label=lambda name: _label(stats, name),
        edge_color=PITCH_LINE_COLOR,
        mirrored=mirrored)


def _count_half(stats: pd.DataFrame, title: str, max_count: int, column: str = 'Würfe', mirrored: bool = False) -> dict:
    """Half of the pitch colored by the amount in the column (white = none, blue = max_count)."""

    return dict(
        title=f"{title}: {stats[column].sum()}",
        sector_color=lambda name: _count_color(stats.loc[name, column], max_count),
        sector_label=lambda name: f"{name}\n{stats.loc[name, column]}",
        # the blue pitch lines would disappear in the blue sectors
        edge_color=LINE_COLOR,
        mirrored=mirrored)

# endregion


# region Stats

def _team_stats(data: pd.DataFrame, mapping):
    """Stats per position for both teams and the most shots from one position (same scale for both teams)."""

    own_stats = _shots_per_position(data[data['own_team']], mapping)
    opponent_stats = _shots_per_position(data[~data['own_team']], mapping)
    max_shots = max(own_stats['Würfe'].max(), opponent_stats['Würfe'].max(), 1)
    return own_stats, opponent_stats, max_shots


def _good_quotes(mapping) -> dict:
    """Good quote per position name (GOOD_QUOTE uses the position codes), DEFAULT_GOOD_QUOTE if missing there."""

    return {name: GOOD_QUOTE.get(code, DEFAULT_GOOD_QUOTE) for code, name in mapping.items()}


def _shots_per_position(shots: pd.DataFrame, mapping) -> pd.DataFrame:
    """Count scored shots and all shots per position (index is the mapped position name)."""

    stats = pd.DataFrame(index=list(mapping.values()))
    stats['Treffer'] = shots[shots['type'].isin(SCORED_SHOTS_FIELDS)]['location'].value_counts()
    stats['Würfe'] = shots[shots['type'].isin(SCORED_SHOTS_FIELDS + MISSED_SHOTS_FIELDS)]['location'].value_counts()

    return stats.fillna(0).astype(int)



def _mistakes_per_position(actions: pd.DataFrame, mapping) -> pd.DataFrame:
    """Count ball losses and technical mistakes per position (index is the mapped position name)."""

    stats = pd.DataFrame(index=list(mapping.values()))
    for mistake_type in ['Ballverlust', 'Fehler']:
        stats[mistake_type] = actions[actions['type'] == mistake_type]['location'].value_counts()

    return stats.fillna(0).astype(int)

# endregion


# region Drawing

def _field_plot(left_half: dict, right_half: dict, mapping, legend: str, file_name: str, title: str) -> Analysis:
    """Draw two halves (see _quote_half and _count_half) on the pitch and save the image."""

    fig, ax = plt.subplots(figsize=(16, 9))
    _draw_half(ax, mapping, 0, **left_half)
    _draw_half(ax, mapping, 1, **right_half)

    ax.text(0, -HALF_WIDTH - 1.2, legend, ha='center', va='top', fontsize=LEGEND_FONT_SIZE, color=LINE_COLOR)
    ax.set_xlim(-TOTAL_LENGTH / 2 - 0.5, TOTAL_LENGTH / 2 + 0.5)
    ax.set_ylim(-HALF_WIDTH - 2.5, HALF_WIDTH + 2)
    ax.set_aspect('equal')
    ax.axis('off')

    img_path = os.path.join(OUTPUT_DIR, file_name)
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    return Analysis(img_path, width=8, height=2.5, top=2.5, title=title)


def _draw_half(ax, mapping, half: int, title: str, sector_color, sector_label, edge_color: str, mirrored: bool):
    """Draw the sectors with their stats in the left (half = 0) or right (half = 1) half.
    A mirrored half is rotated by 180° (goal on the right).

    sector_color(name) and sector_label(name) are called for every sector (name of the position).
    """

    for code, (border_from, border_to, distance_from, distance_to) in SECTORS.items():
        name = mapping[code]
        points = [_to_pitch(point, half, mirrored)
                  for point in _sector_points(border_from, border_to, distance_from, distance_to)]
        color = sector_color(name)
        ax.add_patch(Polygon(points, closed=True, facecolor=color, edgecolor=edge_color, linewidth=1.5))
        ax.text(*_centroid(points), sector_label(name), ha='center', va='center', fontsize=LABEL_FONT_SIZE,
                color=_text_color(color))

    title_x = _half_start(half) + DRAWN_HALF_LENGTH / 2
    ax.text(title_x, HALF_WIDTH + 0.8, title, ha='center', va='bottom', fontsize=TITLE_FONT_SIZE)
    _draw_pitch_lines(ax, half, mirrored)


def _draw_pitch_lines(ax, half: int, mirrored: bool):
    """Draw outline and goal of a cut half (6m/9m lines are the borders of the sectors).
    The edge where a half is cut off is dotted, so it doesn't look like the center line."""

    goal_line_x = _goal_line_x(half, mirrored)
    direction = -1 if mirrored else 1
    cut_x = goal_line_x + direction * SHOWN_LENGTH
    ax.plot([cut_x, goal_line_x, goal_line_x, cut_x], [-HALF_WIDTH, -HALF_WIDTH, HALF_WIDTH, HALF_WIDTH],
            color=LINE_COLOR, linewidth=1.5)
    ax.plot([cut_x, cut_x], [-HALF_WIDTH, HALF_WIDTH], color=LINE_COLOR, linewidth=1, linestyle=':')

    goal_x = goal_line_x if mirrored else goal_line_x - GOAL_DRAW_DEPTH
    ax.add_patch(Rectangle((goal_x, -GOAL_DRAW_HALF_WIDTH), GOAL_DRAW_DEPTH, 2 * GOAL_DRAW_HALF_WIDTH,
                               facecolor=GOAL_COLOR, edgecolor=LINE_COLOR, linewidth=1.5, hatch='//'))

# endregion


# region Geometry

def _half_start(half: int) -> float:
    """x where the left (half = 0) or right (half = 1) half with its goal starts."""

    return -TOTAL_LENGTH / 2 + half * (DRAWN_HALF_LENGTH + GAP)


def _goal_line_x(half: int, mirrored: bool) -> float:
    """x of the goal line, the goal is on the left of the half (on the right if mirrored)."""

    return _half_start(half) + (SHOWN_LENGTH if mirrored else GOAL_DRAW_DEPTH)


def _to_pitch(point, half: int, mirrored: bool):
    """Convert a point seen from the goal (x = across, attacker's left negative; y = distance from goal line)
    to pitch coordinates. A mirrored half is rotated by 180°, otherwise both halves face the same way."""

    x, y = point
    if mirrored:
        return _goal_line_x(half, mirrored) - y, -x
    return _goal_line_x(half, mirrored) + y, x


def _sector_points(border_from, border_to, distance_from: float, distance_to: float, steps: int = 300):
    """Polygon points of a sector between two borders and two goal distances, cut at the side line."""

    outer = _arc(border_from, border_to, distance_to, steps)
    inner = _arc(border_from, border_to, distance_from, steps)
    return outer + inner[::-1]


def _arc(border_from, border_to, distance: float, steps: int):
    """Points with the same distance to the goal (like the 6m line) between two borders."""

    angle_from = _border_angle(border_from, distance)
    angle_to = _border_angle(border_to, distance)
    return [_point_on_ray(math.radians(angle_from + (angle_to - angle_from) * i / steps), distance)
            for i in range(steps + 1)]


def _border_angle(border, distance: float) -> float:
    """Angle (seen from the goal center) where the border reaches the given distance to the goal."""

    if not isinstance(border, tuple):
        return border

    offset, tilt = border
    slope = math.tan(math.radians(tilt))
    # along the border line, the distance to the goal grows with the distance from the goal line
    low, high = 0.0, distance
    for _ in range(50):
        middle = (low + high) / 2
        if _distance_to_goal(offset + middle * slope, middle) < distance:
            low = middle
        else:
            high = middle
    return math.degrees(math.atan2(high, offset + high * slope))


def _point_on_ray(angle: float, distance: float):
    """Point on the ray from the goal center where the distance to the goal is reached.

    The 6m and 9m lines are measured from the goal (posts and goal line), that is why the ray length
    is found with a bisection. The point is cut at the side lines and the center line.
    """

    direction_x, direction_y = math.cos(angle), math.sin(angle)
    low, high = 0.0, distance + GOAL_HALF_WIDTH
    for _ in range(50):
        middle = (low + high) / 2
        if _distance_to_goal(middle * direction_x, middle * direction_y) < distance:
            low = middle
        else:
            high = middle

    length = min(high, _ray_length_to_border(direction_x, direction_y))
    return length * direction_x, length * direction_y


def _distance_to_goal(x: float, y: float) -> float:
    return math.hypot(max(abs(x) - GOAL_HALF_WIDTH, 0), y)


def _ray_length_to_border(direction_x: float, direction_y: float) -> float:
    lengths = [HALF_WIDTH / abs(direction_x) if abs(direction_x) > 1e-9 else math.inf,
               SHOWN_LENGTH / direction_y if direction_y > 1e-9 else math.inf]
    return min(lengths)


def _centroid(points):
    """Center of mass of a polygon (shoelace formula), used to place the labels."""

    area = center_x = center_y = 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
        cross = x1 * y2 - x2 * y1
        area += cross
        center_x += (x1 + x2) * cross
        center_y += (y1 + y2) * cross
    return center_x / (3 * area), center_y / (3 * area)

# endregion


# region Colors

def _sector_color(stats: pd.DataFrame, name: str, good_quote: float, inverted: bool):
    """Green if the quote is good for us, red if bad (compared to the good quote of the position);
    the further the quote is from the good quote, the darker the color."""

    shots = stats.loc[name, 'Würfe']
    if shots == 0:
        return to_rgb(EMPTY_COLOR)

    quote = stats.loc[name, 'Treffer'] / shots
    # a high quote of the opponent is bad for us
    hue, saturation, lightest, darkest = GOOD_COLOR if (quote >= good_quote) != inverted else BAD_COLOR

    # 0 at the good quote, 1 at 0% or 100%
    if quote >= good_quote:
        # a good quote of 100% can only be reached, not exceeded
        distance = (quote - good_quote) / (1 - good_quote) if good_quote < 1 else 0
    else:
        distance = (good_quote - quote) / good_quote
    lightness = lightest + distance * (darkest - lightest)
    return colorsys.hls_to_rgb(hue, lightness, saturation)


def _count_color(count: int, max_count: int):
    """Mix from white (none) to the blue of the pitch lines (most)."""

    if count == 0:
        return to_rgb(WHITE)

    # a single one already gets a light blue, so it is visibly different from none
    share = COUNT_MIN_SHARE + (1 - COUNT_MIN_SHARE) * (count - 1) / max(max_count - 1, 1)
    return tuple(1 + share * (channel - 1) for channel in to_rgb(PITCH_LINE_COLOR))


def _text_color(background):
    """Very dark or very light version of the background color, whichever has the higher contrast (WCAG)."""

    hue, _, saturation = colorsys.rgb_to_hls(*background)
    dark = colorsys.hls_to_rgb(hue, TEXT_LIGHTNESS[0], saturation)
    light = colorsys.hls_to_rgb(hue, TEXT_LIGHTNESS[1], saturation)
    return readable_text_color(background, (dark, light))


# endregion


# region Texts

def _label(stats: pd.DataFrame, name: str) -> str:
    scored = stats.loc[name, 'Treffer']
    shots = stats.loc[name, 'Würfe']
    return f"{name}\n{scored}/{shots} ({_quote_text(scored, shots)})"


def _quote_text(scored: int, shots: int) -> str:
    return f"{round(scored / shots * 100)}%" if shots > 0 else "-"


def _good_quote_text(good_quotes: dict) -> str:
    """Legend line with the good quotes, positions with the same quote are grouped."""

    names_per_quote = {}
    for name, quote in good_quotes.items():
        names_per_quote.setdefault(quote, []).append(name)
    return "Richtwerte: " + "  ·  ".join(f"{', '.join(names)} {round(quote * 100)}%"
                                         for quote, names in sorted(names_per_quote.items()))

# endregion
