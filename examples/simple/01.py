#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from opigen import Renderer
from opigen import widgets
from opigen.contrib import TextUpdate, Display

data = [('LS1_CA01:BPM_D1129', 'VA:LS1_CA01:BPM_D1129:X_RD',
         'VA:LS1_CA01:BPM_D1129:Y_RD'),
        ('LS1_CA01:BPM_D1144', 'VA:LS1_CA01:BPM_D1144:X_RD',
         'VA:LS1_CA01:BPM_D1144:Y_RD')]

# widget position, size controls
height = 25
hgap, vgap = 5, 5
w_name, w_xpos, w_ypos = [200, 60, 60]

# name column
x_name, y0 = 5, 5
# xpos column
x_xpos = x_name + w_name + hgap
# ypos column
x_ypos = x_xpos + w_xpos + hgap

# screen as the root node
screen = Display(800, 600, "BPM Readings")
# place widgets
for name, xpv, ypv in data:
    name_lbl = widgets.Label(x_name, y0, w_name, height, name)
    x_rd_text = TextUpdate(x_xpos, y0, w_xpos, height, xpv)
    y_rd_text = TextUpdate(x_ypos, y0, w_ypos, height, ypv)
    screen.add_children([name_lbl, x_rd_text, y_rd_text])
    # next row of widgets
    y0 += height + vgap

# render the screen
r = Renderer(screen)
r.to_opi("01.opi")  # for CS-Studio
r.to_bob("01.bob")  # for Phoebus
