"""Example of using a script in OPI."""

from opigen import Renderer
from opigen.contrib import Display
from opigen import widgets
from opigen.scripts import Script

# Create a new Display
display = Display(1200, 800, "XYPlot Example")

# This will be our trigger PV, it will be displayed in a text update box to show the value, and
# whenever it changes the script will trigger
trigger_pv = "sim://sine(-5, 5, 500, 0.01)"

# Create the text update box that shows the trigger PVs current value
text_box = widgets.TextUpdate(5, 5, 100, 25, trigger_pv)
display.add_child(text_box)

# Creating the rectangle - this is what will be updated by the script
rectangle = widgets.Rectangle(5, 35, 50, 50)
display.add_child(rectangle)

# Creating the script object by passing it the path to the script, indicating we want it embedded,
# and the script name.
# Note that the script name only shows in the OPI editor.
rectangle_script = Script(script_path="embedded_script.py",
                          embed=True,
                          name="Rectangle Changing Script")

# Once we have the script opbject, we add the PV. In this case, we just want a PV that triggers the
# script when it changes, and the changes are based on the current value of that PV.
rectangle_script.add_pv(process_variable=trigger_pv, trigger=True)

# Lastly, we add the script to the rectangle that we want it to modify.
rectangle.add_script(rectangle_script)

# Render the display to CS-Studio
renderer = Renderer(display)
renderer.to_opi("script_example.opi")
renderer.to_bob("script_example.bob")
