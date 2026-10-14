# Notes for Claude

## Dependencies
This script might later be packaged as a Kivy app with buildozer (background goal, not active work).
Only add libraries that are pure Python or have a python-for-android recipe
(e.g. numpy, pandas, matplotlib, Pillow are fine). Don't add compiled packages without a recipe.

## Code style
Keep paths and settings as module-level CONSTANTS in `constants.py` instead of passing them around as parameters.
