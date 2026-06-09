from rv.rvtypes import *
import rv.commands as crv
from rv.extra_commands import *

from inspector import Inspector
from annotations import AnnotationLayer, LineStroke


class AnnyMode(MinorMode):
    def __init__(self) -> None:
        MinorMode.__init__(self)
        self.inspector = Inspector(mode=self)
        self.annotations = AnnotationLayer()
        self.current_stroke = None

        self.init(
            "py-anny-mode",
            [
                ("render", self.render, "Render overlay"),
                ("pointer-1--push", self.draw_start, "Mouse down"),
                ("pointer-1--drag", self.draw_update, "Mouse drag"),
                ("pointer-1--release", self.draw_end, "Mouse up"),
            ],
            None,
            [
                (
                    "Anny",
                    [
                        ("Show UI", self.show_ui, "=", None),
                    ],
                )
            ],
        )

        self.stroke_types = {1: LineStroke}

    def show_ui(self, event):
        self.inspector.show()

    def set_active_tool(self, tool_id):
        self.active_stroke_type = self.stroke_types.get(tool_id, LineStroke)

    def draw_start(self, event):
        print("entering draw start")
        # Get frame
        frame = crv.frame()
        x, y = event.pointer()

        print("current storke is", self.current_stroke)
        if not self.current_stroke:
            self.current_stroke = self.active_stroke_type(start=(x, y), end=(x, y))
            self.annotations.strokes[frame].append(self.current_stroke)

    def draw_update(self, event):
        x, y = event.pointer()
        self.current_stroke.end = (x, y)

    def draw_end(self, event):
        x, y = event.pointer()
        self.current_stroke.end = (x, y)
        self.current_stroke = None
        print("at end current stroke is", self.current_stroke)

    def render(self, event):
        self.annotations.render(event)


def createMode():
    return AnnyMode()
