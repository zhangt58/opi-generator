import re
import lxml.etree as et
from opigen import actions
from . import text

EXIT_SCRIPT = """
from org.csstudio.display.builder.runtime.toolkit import ToolkitRepresentation

# 1. Fetch the top-level display model hosting this widget
model = widget.getTopDisplayModel()

# 2. Grab the toolkit runtime reference managing that model
toolkit = ToolkitRepresentation.getToolkit(model)

# 3. Instruct the window manager to close that specific view safely
toolkit.closeWindow(model)"""


class OpiAction(object):
    """Base class for action renderers."""

    def __init__(self, text_renderer):
        self.text = text_renderer
        self._action_type = self.ACTION_TYPE

    def render(self, actions_node, action_model):
        action_node = et.SubElement(actions_node, "action")
        action_node.set("type", self.ACTION_TYPE)
        for key, value in vars(action_model).items():
            if all(re.match(rf"^{w}", key) is None for w in ("phoebus", "_")):
                self.text.render(action_node, key, value)
        return action_node


class OpiWritePv(OpiAction):
    """Renderer for write PV actions."""

    ACTION_TYPE = "WRITE_PV"


class OpiExecuteCommand(OpiAction):
    """Renderer for execute command actions."""

    ACTION_TYPE = "EXECUTE_CMD"


class OpiOpen(OpiAction):
    """Renderer for open OPI actions."""

    ACTION_TYPE = "OPEN_DISPLAY"
    MACRO_ERROR = "Invalid macro {}:{} (error {})"

    def render(self, actions_node, action_model):
        action_node = super(OpiOpen, self).render(actions_node, action_model)
        macros_node = et.SubElement(action_node, "macros")
        parent_macros_node = et.SubElement(macros_node, "include_parent_macros")
        parent_macros_node.text = (
            "true" if action_model.get_parent_macros() else "false"
        )
        for key, value in action_model.get_macros().items():
            try:
                key_node = et.SubElement(macros_node, key)
                key_node.text = str(value)
            except (TypeError, ValueError) as e:
                raise ValueError(self.MACRO_ERROR.format(key, value, e))
        return action_node


class OpiExit(OpiAction):
    """Render for exit OPI actions."""

    ACTION_TYPE = "EXECUTE_JAVASCRIPT"

    def render(self, actions_node, action_model):
        """Render an exit action.

        Args:
            actions_node to be parent of the action
            action_model representing the exit action
        """
        # In CSS exit happens to use javascript.  Add properties to help with
        # rendering.
        action_model._action_type = "EXECUTE_JAVASCRIPT"
        action_model.embedded = True
        # Render the javascript
        action_node = super(OpiExit, self).render(actions_node, action_model)
        n = et.SubElement(action_node, "scriptText")
        n.text = et.CDATA(EXIT_SCRIPT)


class OpiActions(object):
    """Renderer for actions."""

    ACTION_MAPPING = {
        actions.ExecuteCommand: OpiExecuteCommand,
        actions.WritePv: OpiWritePv,
        actions.Exit: OpiExit,
        actions.OpenOpi: OpiOpen,
    }

    def render(self, widget_node, tag_name, actions_model):
        if actions_model:
            actions_node = et.SubElement(widget_node, tag_name)
            hook_first = "true" if actions_model.get_hook_first() else "false"
            hook_all = "true" if actions_model.get_hook_all() else "false"
            actions_node.set("hook", hook_first)
            actions_node.set("hook_all", hook_all)
            for action_model in actions_model:
                action_class = OpiActions.ACTION_MAPPING[type(action_model)]
                renderer = action_class(text.OpiText())
                renderer.render(actions_node, action_model)
