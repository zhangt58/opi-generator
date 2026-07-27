__version__ = "1.1.0"

from .config import get_color_def_path
from .config import get_font_def_path
from .fonts import parse_font_file
from .colors import parse_color_file
from .renderers import *

# load font def
parse_font_file(get_font_def_path())
# load color def
parse_color_file(get_color_def_path())

# predefined colors
from . import colors
ALARM_COLORS = {
    'invalid': colors.WISTERIA,
    'normal': colors.EMERALD,
    'minor': colors.CARROT,
    'major': colors.ALIZARIN,
}
