
from pathlib import Path

# get this python module's directory full path:

module_dir = Path(__file__).resolve().parent
assets_dir = Path(__file__).resolve().parent.joinpath('assets')
levels_dir = Path(__file__).resolve().parent.joinpath('levels')