import os
from typing import Union

import opigen.widgets as _widgets
from opigen import (
    fonts,
    colors,
    rules,
    scripts
)
from opigen.colors import Color
from opigen.borders import Border
from opigen.enums import BorderStyle
from opigen.contrib.utils import (
    generate_arrow_points,
    rotate_points
)

# default widget color configurations
DEFAULT_DISPLAY_BG = Color((255, 255, 255), "DISPLAY_BG")
DEFAULT_TEXTUPDATE_BG = Color((240, 240, 240), "TEXTUPDATE_BG")
DEFAULT_TEXTENTRY_BG = Color((236, 240, 241), "TEXTENTRY_BG")
DEFAULT_BORDER_COLOR = Color((0, 128, 255), "BORDER_BLUE")

# absolute path for resource files, e.g. images.
RES_DIRPATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'images')
)


class ProgressBar(_widgets.ProgressBar):

    MINOR_COLOR = colors.CARROT
    MAJOR_COLOR = colors.ALIZARIN
    INVALID_COLOR = colors.INVALID
    NORMAL_COLOR = colors.EMERALD
    def __init__(self, x: int, y: int, width: int, height: int,
                 pv_name: str, minimum: float = 0, maximum: float = 100,
                 limits_from_pv: bool = False,
                 border_alarm_sensitive: bool = False):
        super().__init__(x, y, width, height, pv_name,
                minimum, maximum, limits_from_pv, border_alarm_sensitive)
        self.fill_color = ProgressBar.NORMAL_COLOR
        self.add_rule(
                rules.SelectionRule(
                    "fill_color", pv_name, "Change color per severity",
                    # -1: invalid, 1: major, 2: minor
                    sevr_options=[
                        (-1, ProgressBar.INVALID_COLOR),
                        (1, ProgressBar.MAJOR_COLOR),
                        (2, ProgressBar.MINOR_COLOR)
                    ]))


class ActionButton(_widgets.ActionButton):
    def __init__(self, x, y, width, height, text):
        super().__init__(x, y, width, height, text)
        self.set_font(fonts.DEFAULT)


class SlideButton(_widgets.ImageBoolButton):

    # Emulates SlideButton in Phoebus

    def __init__(self, x, y, width, height, pv_name, alarm_sensitive=False):
        super().__init__(x, y, width, height, pv_name)
        self.on_image = ".images/toggle_on.png"
        self.off_image = ".images/toggle_off.png"
        self.transparency = True
        self.set_border(
            Border(BorderStyle.NONE, 1, DEFAULT_BORDER_COLOR, alarm_sensitive))

    def get_resources(self):
        """Get required resource files and distribute with the final generate OPI.
        """
        return [(os.path.abspath(os.path.join(RES_DIRPATH,
                                              os.path.basename(p))), p)
                for p in (self.on_image, self.off_image)]


class Display(_widgets.Display):

    def __init__(self, width=800, height=600, name=None):
        super().__init__(width, height)
        #
        self.set_bg_color(DEFAULT_DISPLAY_BG)
        if name is not None:
            self.name = name

    def get_opt_size(self):
        """Get the optimal size (width, height) to contain all the
        child widgets.
        """
        children_parent_not_group = []
        for i in self.get_children():
            if hasattr(i, "visible") and not i.visible:
                print(f"Skipping hidden widget: {i.name}")
                continue
            if isinstance(i.get_parent(), _widgets.GroupingContainer):
                print(f"Skipping group child widget: {i.name}")
                continue
            children_parent_not_group.append(i)
        xlist = [i.x for i in children_parent_not_group]
        xlist += [i.x + i.width for i in children_parent_not_group]
        ylist = [i.y for i in children_parent_not_group]
        ylist += [i.y + i.height for i in children_parent_not_group]
        min_x, max_x = min(xlist), max(xlist)
        min_y, max_y = min(ylist), max(ylist)
        opt_w = max_x - min_x
        opt_h = max_y - min_y
        return opt_w, opt_h

    def set_opt_size(self, dw: int = 15, dh: int = 15):
        """Adjust the display size to best contain all child widgets.
        """
        w, h = self.get_opt_size()
        self.width = w + dw
        self.height = h + dh

    def init_vars(self, vars: list[str]):
    #def init_vars(self, names: list[str], values: list, dtypes: list[str]):
        """Use to initialize a list of variables (e.g. loc variables).
        dtype: str or number
        As of now (2024/03/14, Display dose not support script.)
        """
        for var in vars:
            w = _widgets.TextEntry(0, 0, 0, 0, var)
            w.visible = False
            self.add_child(w)
#        script = scripts.Script(script_text="""from org.csstudio.display.builder.runtime.script import PVUtil
#        names = {}.split(",")
#        values = {}.split(",")
#        dtypes = {}.split(",")
#        for name, value, dtype in zip(names, values, dtypes):
#            PVUtil.createPV(name, 5000)
#            if dtype != 'str':
#                value = float(value)
#            PVUtil.writePV(name, value, 5000)
#        """.format(','.join(names), ','.join([str(v) for v in values]), ','.join(dtypes)))


class EmbeddedContainer(_widgets.EmbeddedContainer):

    def __init__(self, x, y, width, height, opi_file):
        super().__init__(x, y, width, height, opi_file)
        #
        self.set_bg_color(DEFAULT_DISPLAY_BG)


class GroupingContainer(_widgets.GroupingContainer):

    def __init__(self, x, y, width, height, name=None):
        _widgets.GroupingContainer.__init__(self, x, y, width, height, name)
        #
        self.set_bg_color(DEFAULT_DISPLAY_BG)
        # preset font
        _widgets.GroupingContainer.set_font(self, fonts.GROUPBOX_NAME)
        _widgets.GroupingContainer.set_border(self,
                Border(BorderStyle.GROUP_BOX, 1, colors.ASBESTOS, False))


class Label(_widgets.Label):
    def __init__(self, x, y, width, height, text):
        super().__init__(x, y, width, height, text)
        self.set_font(fonts.DEFAULT)


class TextUpdate(_widgets.TextUpdate):

    def __init__(self, x, y, width, height, pv_name, alarm_sensitive=True):
        super().__init__(x, y, width, height, pv_name)
        #
        self.set_bg_color(DEFAULT_TEXTUPDATE_BG)
        self.set_border(
            Border(BorderStyle.NONE, 0, DEFAULT_BORDER_COLOR, alarm_sensitive))
        self.set_font(fonts.DEFAULT)


class TextEntry(_widgets.TextEntry):

    def __init__(self, x, y, width, height, pv_name, border_alarm_sensitive: bool = True):
        super().__init__(x, y, width, height, pv_name)
        #
        self.set_bg_color(DEFAULT_TEXTENTRY_BG)
        self.set_font(fonts.DEFAULT)
        self.border_alarm_sensitive = border_alarm_sensitive
        self.phoebus_border_alarm_sensitive = border_alarm_sensitive


class Spinner(_widgets.Spinner):

    def __init__(self, x, y, width, height, pv_name):
        super().__init__(x, y, width, height, pv_name)
        #
        self.set_bg_color(DEFAULT_TEXTENTRY_BG)
        self.set_font(fonts.DEFAULT)


class Led(_widgets.Led):

    def __init__(self, x, y, width, height, pv_name, alarm_sensitive=False):
        _widgets.Led.__init__(self, x, y, width, height, pv_name)
        #
        self.effect_3d = False
        self.bulb_border = 1
        self.set_border(
            Border(BorderStyle.NONE, 1, DEFAULT_BORDER_COLOR, alarm_sensitive))
        self.off_color = colors.ALIZARIN
        self.on_color = colors.EMERALD
        self.set_font(fonts.DEFAULT)


class MultiStateLed(_widgets.MultiStateLed):

    def __init__(self, x: int, y: int, width: int, height: int, pv_name: str,
                 alarm_sensitive: bool = False):
        _widgets.MultiStateLed.__init__(self, x, y, width, height, pv_name)
        self.border_alarm_sensitive = alarm_sensitive
        self.set_font(fonts.DEFAULT)


class LedGreenDark(Led):
    def __init__(self, x, y, width, height, pv_name, alarm_sensitive=False):
        Led.__init__(self, x, y, width, height, pv_name, alarm_sensitive)
        self.on_color = colors.GREEN_LED_ON
        self.off_Color = colors.GREEN_LED_OFF


class CheckBox(GroupingContainer):
    """CheckBox with background color support.
    """
    def __init__(self, x, y, width, height, text, pv_name, **kws):
        GroupingContainer.__init__(self, x, y, width + 5, height + 5, "")
        self.chkbox = chkbox = _widgets.CheckBox(
            kws.get("x0", 1), kws.get("y0", 1), width, height, text, pv_name)
        if kws.get("borderless", False):
            self.set_borderless()
        self.add_child(chkbox)
        self.set_font(fonts.DEFAULT)

    def set_borderless(self):
        self.set_border(
            Border(BorderStyle.NONE, 0, Color((255, 255, 255)), False))

    @property
    def pv_name(self):
        return self.chkbox.pv_name

    @pv_name.setter
    def pv_name(self, pv_name: str):
        self.chkbox.pv_name = pv_name

    def set_fg_color(self, c):
        self.chkbox.set_fg_color(c)

    def set_font(self, font):
        self.chkbox.set_font(font)


class Arrow(_widgets.Polygon):

    def __init__(self, x: int, y: int, length: int, thickness: int,
                 color: Color = DEFAULT_BORDER_COLOR, **kws):
        """ Create an arrow widget pointing to the point (x, y), rotate with *rotate*
        keyword argument, e.g. +30 clockwise, -30 counter-clockwise.

        Examples:
        >>> arrow = Arrow(300, 500, 100, 4, head_fraction=0.25, angle1=20, angle2=80)
        """
        super().__init__(x - length, y, length, thickness)

        head_fraction = kws.get('head_fraction', 0.2)
        angle1 = kws.get('angle1', 30)
        angle2 = kws.get('angle2', 70)
        rotate = kws.get('rotate', 0.0)
        p1 = (length, int(thickness / 2))
        pts = generate_arrow_points(p1, length, thickness, head_fraction, angle1, angle2)
        self.add_points(
            *rotate_points((p1[0] - int(length / 2), p1[1]), pts, rotate)
        )
        self.set_color(color)

    def set_color(self, color: Color):
        """ Set the same color for line/area color.
        """
        self.set_line_color(color)
        self.set_area_color(color)

    def rotate(self, angle: float, ref_point: tuple[int, int] = None):
        """ Rotate the points w.r.t. the reference point (x, y) by angle degree.
        Note that the reference point is the relative inside the polygon.
        """
        if ref_point is None:
            # the center of the polygon (relative inside)
            ref_point = (self.width // 2, self.height // 2)
        self.points = rotate_points(ref_point, self.points, angle)

    def map_to_local(self, point: tuple[int, int]):
        """ Return the point in the global canvas coordinate to the Arrow polygon.
        """
        x, y = point
        return x - self.x, y - self.y


class HorizontalLine(_widgets.Line):

    """ Create a horizontal line widget, starting from (x, y) with the length of *length*,
    thickness of *thickness*, and color of *color*.
    """

    def __init__(self, x: int, y: int, length: int, thickness: int = 1, style: str = "solid",
                 color: Color = None):
        super(HorizontalLine, self).__init__(x, y, x + length, y, thickness, style)
        if color is None:
            color = Color((189, 195, 199), "Silver")
        self.set_line_color(color)


class VerticalLine(_widgets.Line):

    """ Create a vertical line widget, starting from (x, y) with the length of *length*,
    thickness of *thickness*, and color of *color*.
    """

    def __init__(self, x: int, y: int, length: int, thickness: int = 1, style: str = "solid",
                 color: Color = None):
        super(VerticalLine, self).__init__(x, y, x, y + length, thickness, style)
        if color is None:
            color = Color((189, 195, 199), "Silver")
        self.set_line_color(color)


class PointerLine(_widgets.Line):

    """ A pointer line widget, starting from (x1, y2), via two 90 degree right turns to
    the end point (x2, y2). Please, 90 degree right turns is true only if y2 keeps the same.

    #       <-   l   ->
    # ___   11________21
    #  ^    |         |
    #  h    |         v
    # _v_   p1        p2
    """

    def __init__(self, x1: int, y1: int, x2: int, y2: Union[int, None] = None, height: int = 10,
                 thickness: int = 1, arrow_length: int = 8, style: str = "solid",
                 color: Color = None, arrow_style: str = "to"):
        if y2 is None:
            y2 = y1
        x11, y11 = x1, y1 - height
        x21, y21 = x2, y2 - height
        super(PointerLine, self).__init__(x11, y11, x21, y21, thickness, style)
        if color is None:
            color = Color((189, 195, 199), "Silver")
        self.set_line_color(color)
        self.set_arrow_style(arrow_style)
        self.set_arrow_length(arrow_length)
        # add points
        self.insert_point(0, x1, y1)
        self.append_point(x2, y2)


class ComboBox(_widgets.ComboBox):

    def __init__(self, x: int, y: int, width: int, height: int, pv_name: str,
                 alarm_sensitive: bool = False):
        _widgets.ComboBox.__init__(self, x, y, width, height, pv_name)
        self.set_font(fonts.DEFAULT)
        self.set_border(
            Border(BorderStyle.NONE, 1, DEFAULT_BORDER_COLOR, alarm_sensitive)
        )


class Rectangle(_widgets.Rectangle):

    def __init__(self, x: int, y: int, width: int, height: int,
                 color: Color = DEFAULT_BORDER_COLOR):
        super().__init__(x, y, width, height)

        self.set_color(color)

    def set_color(self, color: Color):
        """ Set the same color for background and border.
        """
        self.set_bg_color(color)
        self.line_color = color

