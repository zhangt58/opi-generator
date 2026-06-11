"""Example of using the XYPlot widget to create a graph in CS-Studio and Phoebus."""

from opigen import Renderer
from opigen.contrib import Display
from opigen.colors import Color
from opigen.widgets import XYPlot


class Colors:
    """Enumerator for graph colors"""
    RED = Color((234, 67, 53), alpha=128)
    BLUE = Color((66, 133, 244), alpha=128)
    GREEN = Color((69, 168, 83), alpha=128)


# Create a new Display
display = Display(1200, 800, "XYPlot Example")

# Initialize an XYPlot widget with given dimensions
graph = XYPlot(0, 0, 1200, 800, show_toolbar=True)

# Set title for the X-Axis, axis index 0 is the x-axis
graph.set_axis_title("X-Axis", 0)

# Add traces (data series) to the graph
# Adding the y pv without adding an x pv automatically asigns data to be on integers on the x-axis
graph.add_trace("sim://sineWaveform(10, 30, 50, 1)",
                legend="Sinewave 1",
                trace_color=Colors.RED)
graph.add_trace("sim://sineWaveform(2, 15, 50, 1)",
                legend="Sinewave 2",
                trace_color=Colors.GREEN)

# Configure the first Y-Axis, index 1
graph.set_axis_title("Y-Axis for Sinewave Readings", 1)
graph.set_axis_scale(-4, 1.5, 1)
graph.set_axis_color(Colors.RED, 1)

# Add another Y-Axis and a trace to it, its at y-axis index 1, axis index 2
graph.add_y_axis()
graph.add_trace("sim://sawtoothWaveform(20, 20, 50, 1)",
                legend="Sawtooth Wave",
                trace_color=Colors.BLUE,
                y_axis=1)
graph.set_axis_title("Y-Axis for Sawtooth Readings", 2)
graph.set_axis_scale(-1.5, 4, 2)
graph.set_axis_color(Colors.BLUE, 2)

# Add the graph to the display
display.add_child(graph)

# Render the display to CS-Studio
renderer = Renderer(display)
renderer.to_opi("xyplot_example.opi")
renderer.to_bob("xyplot_example.bob")
