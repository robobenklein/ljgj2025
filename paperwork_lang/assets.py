
from pathlib import Path

# get this python module's directory full path:

module_dir = Path(__file__).resolve().parent
assets_dir = Path(__file__).resolve().parent.joinpath('assets')
levels_dir = Path(__file__).resolve().parent.joinpath('levels')

starter_code = {
    "mainmenu": """
# This your code input box
# (Sorry it sucks so bad lol)
# This is where you'd write instructions for your employees,
# such as
MOVE Desk A
# or
TAKE doc
# and you can use labels for control flow
#LOOP1
""",
}
