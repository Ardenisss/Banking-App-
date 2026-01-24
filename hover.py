# hover.py
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.properties import ListProperty


class HoverMixin:
    normal_color = ListProperty([0, 0.45, 0, 1])  # default
    hover_color = ListProperty([1, 0, 0, 1])      # on-hover (red)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure colors are applied initially
        if not hasattr(self, "color"):
            self.color = self.normal_color
        Window.bind(mouse_pos=self._on_mouse_pos)

    def _on_mouse_pos(self, window, pos):
        # guard: widget not added to window yet
        if not self.get_root_window():
            return
        # convert global mouse to local widget coords
        inside = self.collide_point(*self.to_widget(*pos))
        self.color = self.hover_color if inside else self.normal_color


class HoverLabel(HoverMixin, Label):
    """Label that changes color on hover. Use for non-button text (clicks via on_touch_down)."""
    pass


class HoverButton(ButtonBehavior, HoverLabel):
    """Clickable label (behaves like button) with hover color support."""
    # inherits on_press/on_release from ButtonBehavior and look from HoverLabel
    pass
