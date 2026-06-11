#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from opigen.widgets import ActionButton, TextEntry
from opigen.enums import BasicStyle
from opigen.contrib import Display, TextEntry as MyTextEntry
from opigen import Renderer

d = Display()
btn1 = ActionButton(100, 100, 100, 40, "Classic", BasicStyle.CLASSIC)
btn2 = ActionButton(100, 200, 100, 40, "Native", BasicStyle.NATIVE)
text1 = TextEntry(100, 300, 100, 40, "loc://x(0)", BasicStyle.NATIVE)
text2 = MyTextEntry(100, 400, 100, 40, "loc://y(0)")
d.add_child(btn1)
d.add_child(btn2)
d.add_child(text1)
d.add_child(text2)

Renderer(d).to_bob("style.bob")
Renderer(d).to_opi("style.opi")
