"""Class that renders the axes of graphs in Phoebus"""

from lxml import etree as et

from opigen.opimodel.colors import Color
from .fonts import OpiFont


class OpiAxis:
    """Class that renders the axes of graphs in Phoebus"""

    def __init__(self, color_renderer):
        self._color = color_renderer

    def _render_axis(self, parent_node, axis_name, axis_values):
        """Helper function to render individual axis"""
        axis_node = et.SubElement(parent_node, axis_name)

        # Render non-color attributes
        attribute_names = [
            'title', 'autoscale', 'minimum', 'maximum', 'show_grid'
        ]
        for attribute_name, attribute_value in zip(attribute_names,
                                                   axis_values):
            if attribute_value in (True, False):
                attribute_value = str(attribute_value).lower()
            et.SubElement(axis_node,
                          attribute_name).text = str(attribute_value)

        # Render color attribute separately
        color = axis_values[5]
        if color is not None:
            # Removes transparency for the axis color
            solid_color = Color((color.red, color.green, color.blue), None)
            self._color.render(axis_node, 'color', solid_color)

        # title, scale font
        for font, s in zip(axis_values[6:8], ('title', 'scale')):
            if font is not None:
                OpiFont().render(axis_node, f"{s}_font", font)

    def render(self, widget_node, tag_name, axes_model):
        """Does actual rendering"""
        # Render X-axis
        if axes_model[0][-1]:  # has_xaxis is True
            self._render_axis(widget_node, "x_axis", axes_model[0])

        # Create root node for y-axes
        y_axes_root_node = et.SubElement(widget_node, "y_axes")

        # Render y-axes
        for axis_values in axes_model[1:]:
            self._render_axis(y_axes_root_node, "y_axis", axis_values)
