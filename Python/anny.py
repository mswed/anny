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

        # Get frame (we store the annotation against the frame)
        frame = crv.frame()

        # We need to get the source to convert the mouse position to image space
        source = crv.sourceAtPixel(event.pointer())
        if not source:
            return

        source_name = source[0]["name"]

        # Image space position
        image_pos = crv.eventToImageSpace(source_name, event.pointer())

        if not self.current_stroke:
            self.current_stroke = self.active_stroke_type(
                start=image_pos, end=image_pos, source=source_name
            )
            self.annotations.strokes[frame].append(self.current_stroke)

    def draw_update(self, event):
        if self.current_stroke:
            self.current_stroke.end = crv.eventToImageSpace(
                self.current_stroke.source, event.pointer()
            )

    def draw_end(self, event):
        self.current_stroke = None

    def render(self, event):
        self.annotations.render(event)


def createMode():
    return AnnyMode()
