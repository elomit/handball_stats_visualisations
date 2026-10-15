"""Colors used in the plots."""

# hue and saturation stay the same, only the lightness changes with the distance to the good quote
# (hue, saturation, lightness at the good quote of the position, lightness at a quote of 0% / 100%)
GOOD_COLOR = (0.37, 0.6, 0.78, 0.32)
BAD_COLOR = (0.98, 0.5, 0.8, 0.47)
# the label has the same hue as its sector, in this lightness (dark text, light text)
TEXT_LIGHTNESS = (0.15, 0.95)
EMPTY_COLOR = '#eeeeee'
# blue like the lines on a handball court, used for the sector borders and the plot with the amount of shots
PITCH_LINE_COLOR = '#1f5fbf'
LINE_COLOR = '#444444'
# plot with only the amount of shots: share of the pitch line blue for one shot (white for none, full blue for the most)
COUNT_MIN_SHARE = 0.25
# links in the index of the pdf (blue and underlined, like links in a browser)
LINK_COLOR = '#0645ad'
