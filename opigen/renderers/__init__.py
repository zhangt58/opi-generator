from .css import render as css_render
from .css.render import get_opi_renderer
from .phoebus import render as phoebus_render
from .phoebus.render import get_opi_renderer as get_bob_renderer


class Renderer:

    def __init__(self, display, auto_resize: bool = False, **kws):
        if auto_resize and hasattr(display, "set_opt_size"):
            display.set_opt_size(**kws)
        self._bob_renderer = get_bob_renderer(display)
        self._opi_renderer = get_opi_renderer(display)

    def to_opi(self, filepath: str):
        self._opi_renderer.write_to_file(filepath)

    def to_bob(self, filepath: str):
        self._bob_renderer.write_to_file(filepath)


__all__ = [
    "css_render", "get_opi_renderer", "phoebus_render", "get_bob_renderer",
    "Renderer"
]
