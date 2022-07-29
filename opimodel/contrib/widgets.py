import opimodel.widgets as _widgets
from opimodel.colors import Color
from opimodel.borders import Border, BorderStyle
import os

# default widget color configurations
DEFAULT_DISPLAY_BG = Color((255, 255, 255), "DISPLAY_BG")
DEFAULT_TEXTUPDATE_BG = Color((240, 240, 240), "TEXTUPDATE_BG")
DEFAULT_TEXTENTRY_BG = Color((236, 240, 241), "TEXTENTRY_BG")
DEFAULT_BORDER_COLOR = Color((0, 128, 255), "BORDER_BLUE")

# absolute path for resource files, e.g. images.
RES_DIRPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'images'))


class SlideButton(_widgets.ImageBoolButton):
    def __init__(self, x, y, width, height, pv_name):
        super(self.__class__, self).__init__(x, y, width, height, pv_name)
        self.on_image = ".images/toggle_on.svg"
        self.off_image = ".images/toggle_off.svg"

    def get_resources(self):
        """Get required resource files and distribute with the final generate OPI.
        """
        return [(os.path.abspath(os.path.join(RES_DIRPATH, os.path.basename(p))), p)
                    for p in (self.on_image, self.off_image)]


class Display(_widgets.Display):
    def __init__(self, width=800, height=600):
        super(self.__class__, self).__init__(width, height)
        #
        self.set_bg_color(DEFAULT_DISPLAY_BG)


class LinkingContainer(_widgets.LinkingContainer):
    def __init__(self, x, y, width, height, opi_file):
        super(self.__class__, self).__init__(x, y, width, height, opi_file)
        #
        self.set_bg_color(DEFAULT_DISPLAY_BG)


class GroupingContainer(_widgets.GroupingContainer):
    def __init__(self, x, y, width, height):
        super(self.__class__, self).__init__(x, y, width, height)
        #
        self.set_bg_color(DEFAULT_DISPLAY_BG)


class TextUpdate(_widgets.TextMonitor):
    def __init__(self, x, y, width, height, pv_name):
        super(self.__class__, self).__init__(x, y, width, height, pv_name)
        #
        self.set_bg_color(DEFAULT_TEXTUPDATE_BG)


class TextEntry(_widgets.TextInput):
    def __init__(self, x, y, width, height, pv_name):
        super(self.__class__, self).__init__(x, y, width, height, pv_name)
        #
        self.set_bg_color(DEFAULT_TEXTENTRY_BG)


class Led(_widgets.Led):
    def __init__(self, x, y, width, height, pv_name, alarm_sensitive=False):
        super(self.__class__, self).__init__(x, y, width, height, pv_name)
        #
        self.effect_3d = False
        self.bulb_border = 1
        self.set_border(
            Border(BorderStyle.NONE, 1, DEFAULT_BORDER_COLOR, alarm_sensitive))
