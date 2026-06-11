#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from opigen import colors, fonts, rules, widgets
from opigen.renderers import Renderer
import os

# Read the color and font data CSStudio configuration files
example_dir = os.path.dirname(os.path.realpath(__file__))
colors.parse_color_file(os.path.join(example_dir, 'color.def'))
fonts.parse_font_file(os.path.join(example_dir, 'font.def'))

# Create the root widget
d = widgets.Display(800, 600)
# Add a rectangle.
w = widgets.Rectangle(5, 5, 700, 500)
w.set_bg_color(colors.WHITE)
w.set_fg_color(colors.YELLOW_LED_OFF)
d.add_child(w)

# Add a grouping container.
group = widgets.GroupingContainer(20, 20, 600, 400, "Group")

# Add two action buttons to the grouping container.
ab = widgets.ActionButton(30, 30, 60, 24, 'hello')
ab.add_write_pv('loc://greeting', 'opigen')
group.add_child(ab)
ab2 = widgets.ActionButton(30, 60, 60, 24, 'ls')
ab2.add_shell_command('ls')
group.add_child(ab2)

# Add a rule to the grouping container.
group.add_rule(
    rules.GreaterThanRule('visible', 'loc://visible(100)', 300))
d.add_child(group)

# Add a label with fonts and colour from the config files
l = widgets.Label(100, 450, 200, 20, "Label")
l.add_rule(
    rules.SelectionRule(
        "text", "loc://greeting",
        "Update Text",
        [("true", "pvStr0")],
        out_exp="true",
    ))
l.set_font(fonts.FINE_PRINT)
d.add_child(l)

# Write the OPI file.
Renderer(d, auto_resize=True).to_bob("02.bob")
