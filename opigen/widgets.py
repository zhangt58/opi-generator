"""
Module containing widgets to describe opi files.  An opi has a root widget
of type Display.  To create the opi, add widgets as children of this widget.
"""

from collections import namedtuple
from copy import deepcopy
from typing import Literal, Optional, Union

from opigen.config import get_attr_conf, get_ver_conf

from . import actions, scalings

from .borders import Border
from .colors import Color
from .enums import (
    str2LineArrowStyle,
    str2LineStyle,
    str2PointType,
    str2TraceType,
    BasicStyle,
    BorderStyle,
    FormatType_MAP,
    HAlign,
    LineStyle,
    PointType,
    ResizeBehaviour,
    ResizeBehaviour_MAP,
    RotationStep,
    TraceType,
    VAlign,
)

from .table_columns import Column

ATTR_MAP = get_attr_conf()
VER_CONF = get_ver_conf()
DEFAULT_VER = VER_CONF["Default"]

WidgetGeometry = namedtuple(
    "WidgetGeometry", "x, y, width, height, topLeft, topRight, bottomLeft, bottomRight"
)

# tab direction map (BOY to BOB)
TAB_HORIZONTAL_MAP = {True: 0, False: 1}


def _get_widget_version(name: str):
    """Return the version string for the widget."""
    return VER_CONF.get(name, DEFAULT_VER)


class Widget:
    """Base class for any widget to extend.

    Args:
        id - the CSS id for the widget.
        x - the x position of the widget in pixels
        y - the y position of the widget in pixels
        widget - the width of the widget in pixels
        height - the height of the widget in pixels
        name - a name for the widget within the display
    """

    CNT = {}

    def __init__(self, type_id, x, y, width, height, name=None):
        class_name = self.__class__.__name__
        self.version = _get_widget_version(class_name)
        if name is None:
            k = class_name
            v = Widget.CNT.setdefault(k, 0)
            self.name = f"{k}_{v}"
            Widget.CNT[k] += 1
        else:
            self.name = name
        #
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._children = []
        self._parent = None
        self._type_id = type_id
        self.rules = []
        self.phoebus_rules = []
        self.scripts = []

    def __setattr__(self, name, value):
        _cls_name = self.__class__.__name__
        _conf_default = ATTR_MAP["DEFAULT"]
        if _cls_name in ATTR_MAP:
            _conf = {k: v for k, v in _conf_default.items()}
            _conf_ = ATTR_MAP.get(_cls_name)
            _conf.update(_conf_)
        else:
            _conf = _conf_default

        if name in _conf:
            super().__setattr__(name, value)
            if name == "format_type":
                super().__setattr__(f"phoebus_{_conf[name]}", FormatType_MAP[value])
            elif _cls_name == "EmbeddedContainer" and name == "resize_behaviour":
                super().__setattr__(
                    f"phoebus_{_conf[name]}", ResizeBehaviour_MAP[value]
                )
            elif _cls_name == "TabbedContainer" and name == "horizontal_tabs":
                super().__setattr__(f"phoebus_{_conf[name]}", TAB_HORIZONTAL_MAP[value])
            else:
                super().__setattr__(f"phoebus_{_conf[name]}", value)
        else:
            super().__setattr__(name, value)

    def get_type_name(self):
        # widget type name, i.e. tag name, followed by a real type string
        # ('label') and other attributes.
        return "widget"

    def get_type_id(self):
        return self._type_id

    def get_version(self):
        # css
        return "1.0.0"

    def get_version_phoebus(self):
        # phoebus
        return self.version

    def get_type(self):
        try:
            return self.TYPE  # phoebus
        except AttributeError:
            return self.get_type_id()  # css

    def get_parent(self):
        """Get the parent widget of this widget."""
        return self._parent

    def set_parent(self, parent):
        """Set the parent widget of this widget.

        Args:
            widget to be this widget's parent
        """
        self._parent = parent

    def add_child(self, child):
        """Add a widget as a child of this widget.

        Args:
            child widget
        """
        self._children.append(child)
        child.set_parent(self)

    def add_children(self, children: list):
        """Add multiple widgets as children of this widget.

        Args:
            sequence of child widgets
        """
        for child in children:
            self.add_child(child)

    def get_children(self):
        """Get all child widgets."""
        return self._children

    def set_bg_color(self, color):
        """Set background color for the widget.

        Args:
            Color object
        """
        self.transparent = False
        self.background_color = color

    def set_fg_color(self, color):
        """Set background color for the widget.

        Args:
            Color object
        """
        self.foreground_color = color

    def set_border(self, border):
        """Set border for the widget.

        Args:
            Border object
        """
        self.border = border
        self.phoebus_border = border

    def set_font(self, font):
        """Set font for the widget.

        Args:
            Font object
        """
        self.font = font
        self.phoebus_font = font

    def add_rule(self, rule):
        """Add a rule to the widget.

        Args:
            Rule object
        """
        self.rules.append(rule)
        self.phoebus_rules.append(rule)

    def reset_rules(self):
        """Purge all defined rules if any."""
        self.rules = []
        self.phoebus_rules = []

    def add_script(self, script):
        """Add a script to the widget.

        Args:
            script (Script): The Script object to add.
        """
        self.scripts.append(script)

    def add_scale_options(self, width=True, height=True, keep_wh_ratio=False):
        """Add scale options to the widget.

        Args:
            width (bool): True if widget width is scalable
            height (bool): True if widget height is scalable
            keep_wh_ratio (bool):
        """
        self.scale_options = scalings.ScaleOptions(width, height, keep_wh_ratio)

    def get_resources(self):
        """Return a dict of required resources that need to be distributed with the generated OPI.
        the key is the full path of resource files, and the value is the target path.
        """
        return {}

    def geometry(self):
        """Return a namedTuple of WidgetGeometry."""
        x, y, width, height = self.x, self.y, self.width, self.height
        top_left, top_right = (x, y), (x + width, y)
        bottom_left, bottom_right = (x, y + height), (x + width, y + height)
        return WidgetGeometry(
            x, y, width, height, top_left, top_right, bottom_left, bottom_right
        )

    def clone(self):
        """Return a copy of this widget."""
        return deepcopy(self)


class ActionWidget(Widget):
    """
    Base class for any widget that can have a list of actions.
    """

    # No ID, designed to be subclassed only
    def __init__(self, type_id, x, y, width, height, hook_first=True, hook_all=False):
        super(ActionWidget, self).__init__(type_id, x, y, width, height)
        self.actions = actions.ActionsModel(hook_first, hook_all)
        self.phoebus_actions = self.actions

    def execute_as_one(self, execute_all: bool = True):
        """Execute all action in one click or not."""
        self.actions.set_hook_all(execute_all)

    def add_action(self, action):
        """
        Add any action to the list of actions.

        Args:
            action to add
        """
        self.actions.add_action(action)

    def add_write_pv(self, pv, value, description=""):
        self.actions.add_action(actions.WritePv(pv, value, description))

    def add_shell_command(self, command, description="", directory="$(opi.dir)"):
        # directory does not apply to phoebus
        self.actions.add_action(actions.ExecuteCommand(command, description, directory))

    def add_open_opi(
        self,
        path,
        mode=actions.OpenOpi.STANDALONE,
        description=None,
        macros=None,
        parent_macros=True,
    ):
        self.actions.add_action(
            actions.OpenOpi(path, mode, description, macros, parent_macros)
        )

    def add_open_file(self, path: str, description: str = "Open File"):
        self.actions.add_action(actions.OpenFile(path, description))

    def add_exit(self):
        self.actions.add_action(actions.Exit())

    def set_basic_style(self, style):
        # does not work well
        if style == BasicStyle.CLASSIC:
            self.alarm_pulsing = False
            self.backcolor_alarm_sensitive = False
            self.set_bg_color(Color((218, 218, 218), "ControlAndButtons Background"))
            self.style = style
        else:  # NATIVE
            self.style = style


class Display(Widget):
    """
    Display widget.  This is the root widget for any opi.
    """

    TYPE_ID = "org.csstudio.opibuilder.Display"
    TYPE = None

    def __init__(self, width=800, height=600):
        super(Display, self).__init__(
            Display.TYPE_ID, 0, 0, width, height, name="display"
        )
        self.auto_zoom_to_fit_all = False
        self.show_grid = True

    def get_type_name(self):
        return "display"

    def add_scale_options(self, min_width=-1, min_height=-1, autoscale=False):
        """Add scale options to the display.

        Args:
            min_width (int): Display min width, -1 for no scaling
            min_height (int): Display min height, -1 for no scaling
            autoscale (bool): Autoscale child widgets
        """
        self.auto_scale_widgets = scalings.DisplayScaleOptions(
            min_width, min_height, autoscale
        )


class LinearMeter(ActionWidget):
    TYPE_ID = "To-Be-Supported-for-BOY"
    TYPE = "linearmeter"

    def __init__(
        self,
        x,
        y,
        width,
        height,
        pv_name,
        minimum: float = 0,
        maximum: float = 100,
        limits_from_pv: bool = False,
        border_alarm_sensitive: bool = False,
        level_lolo: float = 10.0,
        level_low: float = 20.0,
        level_high: float = 80.0,
        level_hihi: float = 90.0,
        enable_gradient: bool = False,
        highlight_active_region: bool = True,
    ):
        super(LinearMeter, self).__init__(LinearMeter.TYPE_ID, x, y, width, height)
        # dict, {attr_name: (is_color_attr?, attr_value)}
        self.phoebus_linear_meter_colors = self.linear_meter_colors = {}
        #
        self.pv_name = pv_name
        self.minimum = self.phoebus_minimum = minimum
        self.maximum = self.phoebus_maximum = maximum
        self.limits_from_pv = limits_from_pv
        self.phoebus_limits_from_pv = limits_from_pv
        self.border_alarm_sensitive = border_alarm_sensitive
        self.phoebus_border_alarm_sensitive = border_alarm_sensitive
        self.level_lolo, self.level_low = level_lolo, level_low
        self.level_high, self.level_hihi = level_high, level_hihi
        self.enable_gradient = enable_gradient
        self.highlight_active_region = highlight_active_region

    @property
    def enable_gradient(self):
        return self.linear_meter_colors["is_gradient_enabled"]

    @enable_gradient.setter
    def enable_gradient(self, f: bool):
        self.linear_meter_colors["is_gradient_enabled"] = (False, f)

    @property
    def highlight_active_region(self):
        return self.linear_meter_colors["highlight_active_region"]

    @highlight_active_region.setter
    def highlight_active_region(self, f: bool):
        self.linear_meter_colors["is_highlighting_of_active_regions_enabled"] = (
            False,
            f,
        )

    def set_normal_color(self, color: Color):
        """Set color for normal status."""
        self.linear_meter_colors["normal_status_color"] = (True, color)

    def set_minor_color(self, color: Color):
        """Set color for minor status."""
        self.linear_meter_colors["minor_warning_color"] = (True, color)

    def set_major_color(self, color: Color):
        """Set color for major status."""
        self.linear_meter_colors["major_warning_color"] = (True, color)

    def set_knob_color(self, color: Color):
        self.linear_meter_colors["knob_color"] = (True, color)

    def set_needle_color(self, color: Color):
        self.linear_meter_colors["needle_color"] = (True, color)


class ScaledSlider(ActionWidget):
    TYPE_ID = "To-Be-Supported-for-BOY"
    TYPE = "scaledslider"

    def __init__(
        self,
        x,
        y,
        width,
        height,
        pv_name,
        minimum: float = 0,
        maximum: float = 100,
        limits_from_pv: bool = False,
        border_alarm_sensitive: bool = False,
    ):
        super(ScaledSlider, self).__init__(ScaledSlider.TYPE_ID, x, y, width, height)
        self.pv_name = pv_name
        self.minimum = self.phoebus_minimum = minimum
        self.maximum = self.phoebus_maximum = maximum
        self.limits_from_pv = limits_from_pv
        self.phoebus_limits_from_pv = limits_from_pv
        self.border_alarm_sensitive = border_alarm_sensitive
        self.phoebus_border_alarm_sensitive = border_alarm_sensitive


class ProgressBar(ActionWidget):
    TYPE_ID = "To-Be-Supported-for-BOY"
    TYPE = "progressbar"

    def __init__(
        self,
        x,
        y,
        width,
        height,
        pv_name,
        minimum: float = 0,
        maximum: float = 100,
        limits_from_pv: bool = False,
        border_alarm_sensitive: bool = False,
    ):
        super(ProgressBar, self).__init__(ProgressBar.TYPE_ID, x, y, width, height)
        self.pv_name = pv_name
        self.minimum = self.phoebus_minimum = minimum
        self.maximum = self.phoebus_maximum = maximum
        self.limits_from_pv = limits_from_pv
        self.phoebus_limits_from_pv = limits_from_pv
        self.border_alarm_sensitive = border_alarm_sensitive
        self.phoebus_border_alarm_sensitive = border_alarm_sensitive


class FileSelector(ActionWidget):
    TYPE_ID = "To-Be-Supported-for-BOY"
    TYPE = "fileselector"

    def __init__(self, x, y, width, height, pv_name):
        super(FileSelector, self).__init__(FileSelector.TYPE_ID, x, y, width, height)
        self.pv_name = pv_name


class Rectangle(ActionWidget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.Rectangle"
    TYPE = "rectangle"  # phoebus

    def __init__(self, x, y, width, height):
        super(Rectangle, self).__init__(Rectangle.TYPE_ID, x, y, width, height)

    def set_line_color(self, color: Union[Color, None] = None):
        """Set the line color."""
        if color is None:
            color = Color((189, 195, 199), "Silver")
        self.line_color = color

    def set_area_color(self, color: Union[Color, None] = None):
        """Set the area (background) color."""
        if color is None:
            color = Color((218, 218, 218), "ControlAndButtons Background")
        self.transparent = False
        self.background_color = color


class Polygon(ActionWidget):
    TYPE_ID = "POLYGON-TO-BE-SUPPORTED-BOY"
    TYPE = "polygon"

    def __init__(self, x0: int, y0: int, width: int, height: int):
        super(Polygon, self).__init__(Polygon.TYPE_ID, x0, y0, width, height)
        self.points = []
        self.set_line_color()
        self.set_area_color()

    def add_point(self, x: int, y: int):
        """Add a point to the polygon. The point (x, y) is relative to the polygon
        rectangle area defined by (x0, y0, width, height).
        """
        self.points.append((x, y))

    def add_points(self, *points):
        """Pass points in the form of (x1, y1), (x2, y2), ..."""
        for x, y in points:
            self.points.append((x, y))

    def set_line_color(self, color: Union[Color, None] = None):
        """Set the line color."""
        if color is None:
            color = Color((189, 195, 199), "Silver")
        self.line_color = color

    def set_area_color(self, color: Union[Color, None] = None):
        """Set the area (background) color."""
        if color is None:
            color = Color((218, 218, 218), "ControlAndButtons Background")
        self.transparent = False
        self.background_color = color


class Line(Widget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.polyline"
    TYPE = "polyline"

    def __init__(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        line_width: int = 1,
        line_style: Union[int, str] = "solid",
    ):
        """Widget x,y location is calculated to be the top-left corner of
        rectangle defined by the diagonal from `(x0, y0)` to `(x1, y1)`.
        The width and height are the lengths of the sides.

        The point `(x, y)` is measured in the global frame.
        """
        super(Line, self).__init__(
            Line.TYPE_ID,
            x=min(x0, x1),
            y=min(y0, y1),
            width=abs(x0 - x1) + 1,
            height=abs(y0 - y1) + 1,
        )
        self.points = [(x0, y0), (x1, y1)]
        self.phoebus_points = [(x0 - self.x, y0 - self.y), (x1 - self.x, y1 - self.y)]
        self.line_width = line_width
        if isinstance(line_style, str):
            line_style = str2LineStyle(line_style)
        self.line_style = line_style
        self.set_line_color()

    def add_point(self, x: int, y: int):
        """Add a point with x, y coordinate, the same as `append_point`."""
        self.append_point(x, y)

    def append_point(self, x: int, y: int):
        """Append a point with x, y coordinate to the existing list of points."""
        self.points.append((x, y))
        self.phoebus_points.append((x - self.x, y - self.y))

    def insert_point(self, index: int, x: int, y: int):
        """Insert a point with x, y coordinate."""
        self.points.insert(index, (x, y))
        self.phoebus_points.insert(index, (x - self.x, y - self.y))

    def set_line_color(self, c: Color = None):
        """Set the line color."""
        if c is None:
            c = Color((189, 195, 199), "Silver")
        # background_color
        self.set_bg_color(c)

    def set_arrow_style(self, s: str):
        """Set arrows style: none, from, to, both."""
        self.phoebus_arrows = str2LineArrowStyle(s)

    def set_arrow_length(self, i: int):
        """Set arrow length if arrow style is not none."""
        self.phoebus_arrow_length = i


def _parse_halignment(alignment):
    if isinstance(alignment, str):
        match alignment.lower().strip():
            case "left":
                return HAlign.LEFT
            case "right":
                return HAlign.RIGHT
            case "center":
                return HAlign.CENTER
            case _:
                raise ValueError("horizontal_alignment must be left, right, or center")
    if alignment in (HAlign.LEFT, HAlign.CENTER, HAlign.RIGHT):
        return alignment
    raise TypeError("Error: horizontal_alignment must be of type String or HAlign")


def _parse_valignment(alignment):
    if isinstance(alignment, str):
        match alignment.lower().strip():
            case "top":
                return VAlign.TOP
            case "bottom":
                return VAlign.BOTTOM
            case "middle":
                return VAlign.MIDDLE
            case _:
                raise ValueError("Error: alignment must be top, bottom, or middle")
    if alignment in (VAlign.TOP, VAlign.MIDDLE, VAlign.BOTTOM):
        return alignment
    raise TypeError("Error: vertical_alignment must be of type String or VAlign")


class Label(Widget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.Label"
    TYPE = "label"  # phoebus

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        horizontal_alignment: Optional[Union[str, HAlign]] = None,
        vertical_alignment: Optional[Union[str, VAlign]] = None,
    ):
        super().__init__(Label.TYPE_ID, x, y, width, height)
        self.text = text
        if horizontal_alignment is None:
            _ha = HAlign.LEFT
        else:
            _ha = _parse_halignment(horizontal_alignment)
        self.__dict__['_horizontal_alignment'] = _ha
        self.__dict__['horizontal_alignment'] = _ha
        self.__dict__['phoebus_horizontal_alignment'] = _ha
        if vertical_alignment is None:
            _va = VAlign.MIDDLE
        else:
            _va = _parse_valignment(vertical_alignment)
        self.__dict__['_vertical_alignment'] = _va
        self.__dict__['vertical_alignment'] = _va
        self.__dict__['phoebus_vertical_alignment'] = _va

    def rotate(
        self,
        deg: Literal[
            RotationStep.D0, RotationStep.D90, RotationStep.D180, RotationStep.D_90
        ],
    ):
        self.rotation_step = deg.value

    @property
    def horizontal_alignment(self):
        return self.__dict__['_horizontal_alignment']

    @horizontal_alignment.setter
    def horizontal_alignment(self, alignment: Union[str, HAlign]):
        value = _parse_halignment(alignment)
        self.__dict__['_horizontal_alignment'] = value
        self.__dict__['horizontal_alignment'] = value
        self.__dict__['phoebus_horizontal_alignment'] = value

    @property
    def vertical_alignment(self):
        return self.__dict__['_vertical_alignment']

    @vertical_alignment.setter
    def vertical_alignment(self, alignment: Union[str, VAlign]):
        value = _parse_valignment(alignment)
        self.__dict__['_vertical_alignment'] = value
        self.__dict__['vertical_alignment'] = value
        self.__dict__['phoebus_vertical_alignment'] = value


class TextUpdate(Widget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.TextUpdate"
    TYPE = "textupdate"

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        pv: str,
        horizontal_alignment: Optional[Union[str, HAlign]] = None,
        vertical_alignment: Optional[Union[str, VAlign]] = None,
    ):
        super().__init__(TextUpdate.TYPE_ID, x, y, width, height)
        self.pv_name = pv
        if horizontal_alignment is None:
            _ha = HAlign.CENTER
        else:
            _ha = _parse_halignment(horizontal_alignment)
        self.__dict__['_horizontal_alignment'] = _ha
        self.__dict__['horizontal_alignment'] = _ha
        self.__dict__['phoebus_horizontal_alignment'] = _ha
        if vertical_alignment is None:
            _va = VAlign.MIDDLE
        else:
            _va = _parse_valignment(vertical_alignment)
        self.__dict__['_vertical_alignment'] = _va
        self.__dict__['vertical_alignment'] = _va
        self.__dict__['phoebus_vertical_alignment'] = _va

    @property
    def horizontal_alignment(self):
        return self.__dict__['_horizontal_alignment']

    @horizontal_alignment.setter
    def horizontal_alignment(self, alignment: Union[str, HAlign]):
        value = _parse_halignment(alignment)
        self.__dict__['_horizontal_alignment'] = value
        self.__dict__['horizontal_alignment'] = value
        self.__dict__['phoebus_horizontal_alignment'] = value

    @property
    def vertical_alignment(self):
        return self.__dict__['_vertical_alignment']

    @vertical_alignment.setter
    def vertical_alignment(self, alignment: Union[str, VAlign]):
        value = _parse_valignment(alignment)
        self.__dict__['_vertical_alignment'] = value
        self.__dict__['vertical_alignment'] = value
        self.__dict__['phoebus_vertical_alignment'] = value


class TextEntry(Widget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.TextInput"
    TYPE = "textentry"

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        pv: str,
        horizontal_alignment: Optional[Union[str, HAlign]] = None,
        vertical_alignment: Optional[Union[str, VAlign]] = None,
        style=None,
    ) -> None:
        super().__init__(TextEntry.TYPE_ID, x, y, width, height)
        self.pv_name = pv
        if horizontal_alignment is None:
            _ha = HAlign.LEFT
        else:
            _ha = _parse_halignment(horizontal_alignment)
        self.__dict__['_horizontal_alignment'] = _ha
        self.__dict__['horizontal_alignment'] = _ha
        self.__dict__['phoebus_horizontal_alignment'] = _ha
        if vertical_alignment is None:
            _va = VAlign.MIDDLE
        else:
            _va = _parse_valignment(vertical_alignment)
        self.__dict__['_vertical_alignment'] = _va
        self.__dict__['vertical_alignment'] = _va
        self.__dict__['phoebus_vertical_alignment'] = _va
        if style is not None:
            self.set_basic_style(style)

    @property
    def horizontal_alignment(self):
        return self.__dict__['_horizontal_alignment']

    @horizontal_alignment.setter
    def horizontal_alignment(self, alignment: Union[str, HAlign]):
        value = _parse_halignment(alignment)
        self.__dict__['_horizontal_alignment'] = value
        self.__dict__['horizontal_alignment'] = value
        self.__dict__['phoebus_horizontal_alignment'] = value

    @property
    def vertical_alignment(self):
        return self.__dict__['_vertical_alignment']

    @vertical_alignment.setter
    def vertical_alignment(self, alignment: Union[str, VAlign]):
        value = _parse_valignment(alignment)
        self.__dict__['_vertical_alignment'] = value
        self.__dict__['vertical_alignment'] = value
        self.__dict__['phoebus_vertical_alignment'] = value


class Spinner(Widget):
    TYPE_ID = "TO-Be-Supported-BOY"
    TYPE = "spinner"

    def __init__(self, x, y, width, height, pv_name: str):
        super(Spinner, self).__init__(Spinner.TYPE_ID, x, y, width, height)
        self.pv_name = pv_name


class GroupingContainer(Widget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.groupingContainer"
    TYPE = "group"

    def __init__(self, x, y, width, height, name=""):
        super(GroupingContainer, self).__init__(
            GroupingContainer.TYPE_ID, x, y, width, height, name
        )
        self.lock_children = True
        self.transparent = True  # transparent background


class TabbedContainer(Widget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.tab"
    TYPE = "tabs"

    def __init__(self, x, y, width, height):
        super(TabbedContainer, self).__init__(
            TabbedContainer.TYPE_ID, x, y, width, height
        )
        self.tab_count = 0
        self.tabs = []
        self.phoebus_tabs = self.tabs

    def add_tab(
        self,
        name,
        widget=None,
        dw=2,
        dh=33,
        background_color=None,
        foreground_color=None,
    ):
        """Add a new tab named as *name*, containing *widget*

        _grp.width = self.width - dw
        _grp.height = self.height - dh
        """
        # create a grouping container for the content widget
        _grp = GroupingContainer(1, 1, self.width - dw, self.height - dh)

        if widget is not None:
            _grp.add_child(widget)

        _grp.set_border(Border(BorderStyle.NONE, 0, Color((255, 255, 255)), False))
        _grp.name = name

        self.tabs.append((name, _grp, background_color, foreground_color))
        self.tab_count += 1

    def add_child_to_tab(self, tab_name, widget):
        """Adds a new *widget* to tab with name *tab*"""
        for tab in self.tabs:
            if tab[0] == tab_name:
                tab[1].add_child(widget)
                return

        raise ValueError(f"Error! {tab_name} not found in available tabs.")

    def set_font(self, font):
        """Set font for each tab. Call this method after added all tabs (only for BOY)."""
        self.phoebus_font = font
        for i in range(self.tab_count):
            setattr(self, f"tab_{i}_font", font)


class EmbeddedContainer(Widget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.linkingContainer"
    TYPE = "embedded"

    def __init__(self, x, y, width, height, opi_file):
        super(EmbeddedContainer, self).__init__(
            EmbeddedContainer.TYPE_ID, x, y, width, height
        )
        self.opi_file = opi_file
        self.resize_behaviour = ResizeBehaviour.CROP


class ActionButton(ActionWidget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.ActionButton"
    TYPE = "action_button"

    def __init__(
        self, x, y, width, height, text, style=None, hook_first=True, hook_all=False
    ):
        super(ActionButton, self).__init__(
            ActionButton.TYPE_ID, x, y, width, height, hook_first, hook_all
        )

        self.text = text
        if style is not None:
            self.set_basic_style(style)
        self.border_alarm_sensitive = False


class MenuButton(ActionWidget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.MenuButton"

    def __init__(self, x, y, width, height, text):
        super(MenuButton, self).__init__(MenuButton.TYPE_ID, x, y, width, height)

        self.label = text


class CheckBox(ActionWidget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.checkbox"
    TYPE = "checkbox"

    def __init__(self, x, y, width, height, text, pv_name):
        super(CheckBox, self).__init__(CheckBox.TYPE_ID, x, y, width, height)

        self.label = text
        self.pv_name = pv_name


class ToggleButton(ActionWidget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.BoolButton"
    TYPE = "bool_button"

    def __init__(self, x, y, width, height, on_text, off_text, pv_name=None):
        super(ToggleButton, self).__init__(ToggleButton.TYPE_ID, x, y, width, height)

        if pv_name is not None:
            self.pv_name = pv_name

        self.on_label = on_text
        self.off_label = off_text
        self.toggle_button = True
        self.effect_3d = True
        self.square_button = True
        self.show_boolean_label = True
        self.show_led = False
        self.push_action_index = 0
        self.released_action_index = 1

    def add_push_action(self, action):
        self.actions.add_action(action)
        self.push_action_index = len(self.actions) - 1

    def add_release_action(self, action):
        self.actions.add_action(action)
        self.released_action_index = len(self.actions) - 1


class Led(Widget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.LED"
    TYPE = "led"

    def __init__(self, x, y, width, height, pv):
        super(Led, self).__init__(Led.TYPE_ID, x, y, width, height)
        self.pv_name = pv


class MultiStateLed(ActionWidget):
    TYPE_ID = "To-Be-Supported-for-BOY-IF-APPLICABLE"
    TYPE = "multi_state_led"

    DEFAULT_COLORS = {
        # 0: dark green: OFF
        0: Color((60, 100, 60), name="OFF"),
        # 1: green: ON
        1: Color((0, 255, 0), name="ON"),
        # -1: pink, Err (fallback)
        -1: Color((255, 0, 255)),
    }

    def __init__(self, x, y, width, height, pv):
        super(MultiStateLed, self).__init__(MultiStateLed.TYPE_ID, x, y, width, height)
        self.pv_name = pv
        # reset all states, add new ones with add_state()
        self.states = []
        self.phoebus_states = []

    def reset_states(self):
        self.states = []
        self.phoebus_states = []

    def add_state(self, value: int, label: str, color: Color):
        """Add a new state."""
        self.states.append((value, label, color))
        self.phoebus_states.append((value, label, color))

    def _get_state_color(self, i: int, n: int):
        # Return the color for i-th state of total n states.
        #
        # starting at 3rd state (i=2), only change blue at different level
        if i in (0, 1):
            return MultiStateLed.DEFAULT_COLORS[i]
        else:
            if n < 9:
                v0_blue = 80
                d_blue = 40
            else:
                v0_blue = 40
                d_blue = int((255 - v0_blue) / (n - 2))
            b = (i - 2) * d_blue + v0_blue
            if b > 255:
                b = 255
            return Color((10, 0, b), name=f"State {i + 1}")

    def auto_add_states(self, n: int):
        """Automatically add *n* states, by default naming conventions."""
        for i in range(n):
            color = self._get_state_color(i, n)
            self.add_state(i, f"State {i + 1}", color)


class Byte(Widget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.bytemonitor"
    TYPE = "byte_monitor"

    def __init__(self, x, y, width, height, pv, bits, start_bit=None):
        super(Byte, self).__init__(Byte.TYPE_ID, x, y, width, height)
        self.pv_name = pv
        self.effect_3d = False
        self.square_led = False
        self.numBits = bits
        self.led_border = 1
        self.border_alarm_sensitive = False
        self.led_packed = True
        if start_bit is not None:
            self.startBit = start_bit


class Image(Widget):
    TYPE_ID = "TO-BE-SUPPORTED"
    TYPE = "picture"

    def __init__(self, x: int, y: int, width: int, height: int, file: str):
        super(Image, self).__init__(Image.TYPE_ID, x, y, width, height)
        self.file = file
        self.phoebus_file = file


class Symbol(ActionWidget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.edm.symbolwidget"
    TYPE = "symbol"

    def __init__(
        self,
        x,
        y,
        width,
        height,
        pv_name,
        image_file: str = None,
        initial_index: int = 0,
        border_alarm_sensitive: bool = False,
    ):
        super(Symbol, self).__init__(Symbol.TYPE_ID, x, y, width, height)
        self.pv_name = pv_name
        self.symbols = []
        self.phoebus_symbols = []
        if image_file is not None:
            self.add_symbol(image_file)
        self.initial_index = initial_index
        self.border_alarm_sensitive = border_alarm_sensitive

    def add_symbol(self, image_file: str):
        """Add an image file as a new symbol."""
        self.symbols.append(image_file)
        self.phoebus_symbols.append(image_file)

    def add_symbols(self, image_files: list[str]):
        self.symbols.extend(image_files)
        self.phoebus_symbols.extend(image_files)


# Tank
class Tank(Widget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.tank"

    def __init__(self, x, y, width, height, pv):
        super(Tank, self).__init__(Tank.TYPE_ID, x, y, width, height)
        self.pv_name = pv
        self.effect_3d = False


class DataBrowser(Widget):
    TYPE_ID = "org.csstudio.trends.databrowser.opiwidget"
    TYPE = "databrowser"

    def __init__(self, x, y, width, height, filename):
        super(DataBrowser, self).__init__(DataBrowser.TYPE_ID, x, y, width, height)
        self.show_toolbar = True
        self.filename = filename


class ImageBoolButton(ActionWidget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.ImageBoolButton"

    def __init__(
        self, x, y, width, height, pv_name=None, on_image=None, off_image=None
    ):
        super(ImageBoolButton, self).__init__(
            ImageBoolButton.TYPE_ID, x, y, width, height
        )
        if on_image is not None:
            self.on_image = on_image
        if off_image is not None:
            self.off_image = off_image
        if pv_name is not None:
            self.pv_name = pv_name


class SlideButton(ActionWidget):
    TYPE_ID = "TO-BE-SUPPORTED"  # not available for BOY
    TYPE = "slide_button"

    def __init__(self, x, y, width, height, pv_name=None):
        super(SlideButton, self).__init__(SlideButton.TYPE_ID, x, y, width, height)
        if pv_name is not None:
            self.phoebus_pv_name = pv_name
        self.phoebus_label = ""


class Table(ActionWidget):
    TYPE_ID = "TO-BE-SUPPORTED"  # not available for BOY or to be supported
    TYPE = "table"

    def __init__(
        self, x: int, y: int, width: int, height: int, pv_name: Optional[str] = None
    ) -> None:
        super(Table, self).__init__(Table.TYPE_ID, x, y, width, height)
        if pv_name is not None:
            self.phoebus_pv_name = pv_name
        self.phoebus_columns = []

    def reset_columns(self) -> None:
        self.phoebus_columns = []

    def add_column(self, column: Column) -> None:
        self.phoebus_columns.append(column)

    def add_columns(self, columns: list[Column]) -> None:
        self.phoebus_columns.extend(columns)


class WebBrowser(ActionWidget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.webbrowser"
    TYPE = "webbrowser"

    def __init__(self, x, y, width, height, url):
        super(WebBrowser, self).__init__(WebBrowser.TYPE_ID, x, y, width, height)
        self.url = url
        self.phoebus_url = url


class _ChartWidget(ActionWidget):
    """Class that creates an XYGraph in CS-Studio and Phoebus.

    This graph will always be made to be a bar graph. Other graph types are possible, but not via
    the use of this widget.

    Attributes:
        show_toolbar (bool): Shows the toolbar on the graph
        trace_count (int): Total number of traces (data sequences) on the graph
        axis_count (int): The count of axes on the graph.
        phoebus_axes (list): The list of axes and their settings for Phoebus.
        phoebus_traces (list): The list of traces and their settings for Phoebus.
    """

    def __init__(self, type_id, x, y, width, height, **kws):
        """Initializes the XYGraph with the given dimensions.

        Args:
            x (int): The x-coordinate of the graph.
            y (int): The y-coordinate of the graph.
            width (int): The width of the graph.
            height (int): The height of the graph.

        Keyword Arguments
        -----------------
        has_xaxis : bool
            If has X-axis for non-timestamp, e.g. False for StripChart, while True for XYPlot.
            Defaults True.
        """
        super().__init__(type_id, x, y, width, height)
        self.trace_count = 0
        self.axis_count = 2

        self._has_xaxis = kws.get("has_xaxis", True)
        # Phoebus renders axes vastly different from CS-Studio, so data is
        # stored differently for it as well
        self.phoebus_axes = [
            # legend, autoscale?, min, max, grid?, visible?, color, title_font, scale_font, [if has non-temporal xaixs?]
            ["X Axis", True, 0, 100, True, True, None, None, None, self._has_xaxis],
            ["Y Axis 1", True, 0, 100, True, True, None, None, None],
        ]
        self.phoebus_traces = []

        # Sets the x-axis and first y-axis to show their grids
        self.set_axis_grid(True, 0)
        self.set_axis_grid(True, 1)

    def add_y_axis(self):
        """Adds a y-axis to the graph.

        Returns:
            int: The current axis count after adding the new axis.
        """
        self.axis_count += 1

        # CS-Studio
        setattr(self, f"axis_{self.axis_count - 1}_y_axis", True)

        # Phoebus
        self.phoebus_axes.append(
            [
                f"Y Axis {self.axis_count - 1}",
                True,
                0,
                100,
                True,
                True,
                None,
                None,
                None,
            ]
        )

        self.set_axis_grid(True, self.axis_count - 1)

        return self.axis_count

    def hide_axis(self, hidden: bool, axis=0):
        """Hide axis or not."""
        self.phoebus_axes[axis][5] = not hidden

    def set_axis_font(self, type: str, font, axis=0):
        """Set title or scale font, only support Phoebus now."""
        if type == "title":
            self.phoebus_axes[axis][7] = font
        elif type == "scale":
            self.phoebus_axes[axis][8] = font

    def set_axis_scale(self, minimum, maximum, axis=0):
        """Sets the minimum and maximum values for a given axis, and disables the auto-scaling.

        Args:
            minimum (float): The minimum value for the axis.
            maximum (float): The maximum value for the axis.
            axis (int, optional): The index of the axis. Defaults to the x-axis (0).
        """
        if axis == 0 and not self._has_xaxis:
            return
        # CS-Studio
        setattr(self, f"axis_{axis}_auto_scale", False)
        setattr(self, f"axis_{axis}_minimum", minimum)
        setattr(self, f"axis_{axis}_maximum", maximum)

        # Phoebus
        self.phoebus_axes[axis][1] = False  # autoscale
        self.phoebus_axes[axis][2] = minimum
        self.phoebus_axes[axis][3] = maximum

    def auto_scale(self, on: str, axis: int):
        """Set axis autoscale on or off."""
        is_on = on == "on"
        if axis == 0 and not self._has_xaxis:
            self.autoscale = is_on
            self.phoebus_autoscale = is_on
        else:
            setattr(self, f"axis_{axis}_auto_scale", is_on)
            self.phoebus_axes[axis][1] = is_on

    def set_axis_title(self, title, axis=0):
        """Sets the title of a given axis.

        Args:
            title (str): The title for the axis.
            axis (int, optional): The index of the axis. Defaults to the x-axis (0).
        """
        # CS-Studio
        setattr(self, f"axis_{axis}_axis_title", title)

        # Phoebus
        self.phoebus_axes[axis][0] = title

    def set_axis_color(self, color, axis=0):
        """Sets the color for a given axis.

        Args:
            color (Color): The color for the axis.
            axis (int, optional): The index of the axis. Defaults to the x-axis (0).
        """
        if axis == 0 and not self._has_xaxis:
            self.set_fg_color(color)
        else:
            # CS-Studio
            setattr(self, f"axis_{axis}_axis_color", color)
            setattr(self, f"axis_{axis}_grid_color", color)

            # Phoebus
            self.phoebus_axes[axis][6] = color

    def set_axis_grid(self, grid_on=True, axis=0):
        """Sets if the grid corresponding to an axis should be shown.

        Args:
            grid_on (bool, optional): Whether the grid should be shown. Defaults to true.
            axis (int, optional): The index of the axis. Defaults to the x-axis (0).
        """
        if axis == 0 and not self._has_xaxis:
            self.show_grid = grid_on
            self.phoebus_show_grid = grid_on
        else:
            # CS-Studio
            setattr(self, f"axis_{axis}_show_grid", grid_on)
            # Phoebus
            self.phoebus_axes[axis][4] = grid_on

    def add_trace(
        self,
        y_pv,
        x_pv=None,
        yerr_pv=None,
        legend=None,
        trace_type=TraceType.BARS,
        line_width=10,
        line_style=LineStyle.SOLID,
        point_type=PointType.NONE,
        point_size=10,
        trace_color=None,
        y_axis=0,
    ):
        """Adds a trace to the graph.

        The trace will take the form of a bar graph. If no X PV is provided, the OPI will
        automatically assign values such that the trace's datapoints are on integers on the x-axis.

        The index of the y-axis a trace is assigned to is different from the overall axis index.
        The default y-axis has an index of 0 of y-axes, but an index of 1 overall since the x-axis
        is the 0th axis.

        Args:
            y_pv (str): The process variable for the y-values of the trace.
            x_pv (str, optional): The process variable for the x-values of the trace.
            yerr_pv (str, optional): The process variable for the yerr-values of the trace.
            legend (str, optional): The name that will be displayed on the legend.
            line_width (int, optional): The line width for the trace. Defaults to 10.
            trace_color (Color, optional): The color for the trace.
            y_axis (int, optional): The index of the y-axis for the trace.
                Defaults to the first y-axis (0).
        """
        if isinstance(trace_type, str):
            trace_type = str2TraceType(trace_type)
        if isinstance(line_style, str):
            line_style = str2LineStyle(line_style)
        if isinstance(point_type, str):
            point_type = str2PointType(point_type)
        # CS-Studio
        trace_index = self.trace_count

        if x_pv is not None:
            setattr(self, f"trace_{trace_index}_x_pv", x_pv)

        setattr(self, f"trace_{trace_index}_y_pv", y_pv)
        setattr(self, f"trace_{trace_index}_concatenate_data", False)
        setattr(self, f"trace_{trace_index}_line_width", line_width)
        setattr(self, f"trace_{trace_index}_line_style", line_style)
        setattr(self, f"trace_{trace_index}_point_type", point_type)
        setattr(self, f"trace_{trace_index}_point_size", point_size)
        # map BOY to PHOEBUS
        setattr(self, f"trace_{trace_index}_trace_type", 3)

        if legend is not None:
            setattr(self, f"trace_{trace_index}_name", legend)

        if trace_color is not None:
            setattr(self, f"trace_{trace_index}_trace_color", trace_color)

        setattr(self, f"trace_{trace_index}_y_axis_index", y_axis + 1)

        self.trace_count += 1

        # Phoebus
        self.phoebus_traces.append(
            [
                self.get_type(),
                legend,
                x_pv,
                y_pv,
                yerr_pv,
                trace_type,
                line_width,
                line_style,
                point_type,
                point_size,
                y_axis,
                trace_color,
            ]
        )


class XYPlot(_ChartWidget):
    TYPE_ID = "org.csstudio.opibuilder.widgets.xyGraph"
    TYPE = "xyplot"

    def __init__(self, x, y, width, height, show_toolbar=False):
        self._has_xaxis = True
        super(XYPlot, self).__init__(
            XYPlot.TYPE_ID, x, y, width, height, has_xaxis=True
        )
        self.show_toolbar = show_toolbar


class StripChart(_ChartWidget):
    TYPE_ID = "TO-BE-SUPPORTED"
    TYPE = "stripchart"

    def __init__(self, x, y, width, height, show_toolbar=False, start=None):
        super(StripChart, self).__init__(
            StripChart.TYPE_ID, x, y, width, height, has_xaxis=False
        )
        self.show_toolbar = show_toolbar
        # the starting time, relative to now
        if start is None:
            start_time = "5 minutes"
        else:
            start_time = start
        self.start = start_time

    def set_label_font(self, font):
        self.label_font = font

    def set_scale_font(self, font):
        self.scale_font = font

    def set_title_font(self, font):
        self.title_font = font


class ComboBox(ActionWidget):
    TYPE_ID = "COMBOBOX-TO-BE-SUPPORTED-BOY"
    TYPE = "combo"

    def __init__(self, x: int, y: int, width: int, height: int, pv_name: str):
        super(ComboBox, self).__init__(ComboBox.TYPE_ID, x, y, width, height)
        self.pv_name = pv_name
