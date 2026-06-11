from opigen import Renderer, colors
from opigen.rules import SelectionRule
from opigen.scripts import Script
from opigen.contrib import TextUpdate, Display

def main_rule():
    # Create a page
    screen = Display(name="Rule Example")
    # Add a TextUpdate widget
    my_pv = "sim://flipflop(1)"
    widget = TextUpdate(5, 5, 50, 20, my_pv)
    screen.add_child(widget)
    # Use a rule to change the background color
    rule = SelectionRule(
            # the widget attribute to change
            "background_color",
            # PV as the trigger on value changes
            my_pv,
            # the rule description
            "Change background color",
            # a list of enumerated cases
            [(1, colors.GREEN), (0, colors.RED)],
            # fallback attribute value
            else_val=colors.WHITE
    )
    rule.add_pv("loc://dummy_pv(1)", trigger=False)
    widget.add_rule(rule)
    # Generate the OPI file
    Renderer(screen).to_bob("page-rule.bob")

def main_script():
    # Create a page
    screen = Display(name="Script Example")
    # Add a TextUpdate widget
    my_pv = "sim://flipflop(1)"
    widget = TextUpdate(5, 5, 50, 20, my_pv)
    screen.add_child(widget)
    # Use a script to change the background color
    SCRIPT_TEXT = """
from org.csstudio.display.builder.runtime.script import PVUtil
from org.csstudio.display.builder.model.properties import WidgetColor

v = PVUtil.getDouble(pvs[0])
color = None
if v == 1.0:
    color = WidgetColor(0, 255, 0, 255) # Green
elif v == 0.0:
    color = WidgetColor(255, 0, 0, 255) # Red
if color is not None:
    widget.setPropertyValue("background_color", color)
"""
    script = Script(script_text=SCRIPT_TEXT)
    script.add_pv(my_pv)
    widget.add_script(script)
    # Generate the OPI file
    Renderer(screen).to_bob("page-script.bob")


if __name__ == "__main__":
    main_rule()
    main_script()
