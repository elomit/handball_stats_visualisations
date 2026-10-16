"""All colors of the plots and the pdf, so the same meaning has the same color everywhere."""

import colorsys

from matplotlib.colors import LinearSegmentedColormap, to_hex, to_rgb


def _hue_and_saturation(color: str):
    hue, _, saturation = colorsys.rgb_to_hls(*to_rgb(color))
    return hue, saturation


def contrast(color1, color2) -> float:
    """WCAG contrast ratio between two colors (1 = same, 21 = black on white).
    Colors as (r, g, b) from 0 to 1 or as matplotlib color (e.g. hex)."""

    def luminance(color):
        def linear(channel):
            return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

        red, green, blue = color
        return 0.2126 * linear(red) + 0.7152 * linear(green) + 0.0722 * linear(blue)

    brighter, darker = sorted([luminance(to_rgb(color1)), luminance(to_rgb(color2))], reverse=True)
    return (brighter + 0.05) / (darker + 0.05)


def readable_text_color(background, text_colors):
    """The one of the text colors with the higher contrast on the background."""

    return max(text_colors, key=lambda text: contrast(text, background))


def _with_lightness(color: str, lightness: float) -> str:
    """Same hue and saturation as the color, but lighter or darker."""

    hue, saturation = _hue_and_saturation(color)
    return to_hex(colorsys.hls_to_rgb(hue, lightness, saturation))


# region Club colors (Handballfreunde Pankow, taken from the logo)

TEAM_BLUE = '#254159'
TEAM_ORANGE = '#e18d36'

# endregion

# region Palette (one color per meaning, the plots below only use these)

WHITE = '#ffffff'
BLACK = '#000000'
# lines and secondary text
GREY = '#444444'
# areas without data
LIGHT_GREY = '#eeeeee'
# the club blue, but lighter so filled areas don't get too dark (also used for the lines of the pitch)
BLUE = _with_lightness(TEAM_BLUE, 0.435)
ORANGE = TEAM_ORANGE
# good for us
GREEN = '#2eb84c'
# bad for us
RED = '#d92523'

# endregion


# region Pitch plots (field_analysis.py)

# hue and saturation of GREEN / RED, only the lightness changes with the distance to the good quote
# (hue, saturation, lightness at the good quote of the position, lightness at a quote of 0% / 100%)
GOOD_COLOR = (*_hue_and_saturation(GREEN), 0.78, 0.32)
# the red of the pitch is less saturated than RED, otherwise the strong reds dominate the plot
BAD_COLOR = (_hue_and_saturation(RED)[0], 0.5, 0.8, 0.47)
# the label has the same hue as its sector, in this lightness (dark text, light text)
TEXT_LIGHTNESS = (0.15, 0.95)
EMPTY_COLOR = LIGHT_GREY
# used for the sector borders and the plot with the amount of shots
PITCH_LINE_COLOR = BLUE
LINE_COLOR = GREY
GOAL_COLOR = WHITE
# plot with only the amount of shots: share of the pitch line blue for one shot (white for none, full blue for the most)
COUNT_MIN_SHARE = 0.25

# endregion

# region Timelines (timeline_analysis.py)

TIMELINE_COLORS = {
    'Treffer': GREEN,
    'Gegentor': RED,
    'Verworfen': ORANGE,
    'Ballverlust': BLUE,
    'Fehler': GREY,
}
ATTACK_TIME_COLOR = BLUE

# endregion

# region Heatmaps (shot_analysis.py)

# from white (no shots) over the color to a darker version of it for the hotspots (most shots)
HOTSPOT_LIGHTNESS = 0.25
GOOD_HEATMAP = LinearSegmentedColormap.from_list('good', [WHITE, GREEN, _with_lightness(GREEN, HOTSPOT_LIGHTNESS)])
BAD_HEATMAP = LinearSegmentedColormap.from_list('bad', [WHITE, RED, _with_lightness(RED, HOTSPOT_LIGHTNESS)])
# shot counts on the heatmap, the one with more contrast is used (light text on the dark hotspots)
HEATMAP_TEXT_COLORS = (BLACK, WHITE)
# box with the trick shots (Heber, Dreher), drawn transparent
TEXTBOX_COLOR = ORANGE

# endregion

# region PDF (pdf_creation.py)

TEXT_COLOR = BLACK
SECONDARY_TEXT_COLOR = GREY
# links in the index (blue and underlined, like links in a browser)
LINK_COLOR = BLUE

# endregion
