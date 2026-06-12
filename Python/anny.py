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
        self.drag_start_pos = None

        self.init(
            "py-anny-mode",
            [
                ("render", self.render, "Render overlay"),
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
        self.current_stroke = None

        # Bind the select tool for start
        self.bind_select_tool()

    def show_ui(self, event):
        self.inspector.show()

    def bind_draw_tool(self):
        """
        Bind the mouse actions to the draw tool
        """
        crv.bind(
            "py-anny-mode", "global", "pointer-1--push", self.draw_start, "Start draw"
        )
        crv.bind("py-anny-mode", "global", "pointer-1--drag", self.draw_update, "Draw")
        crv.bind(
            "py-anny-mode", "global", "pointer-1--release", self.draw_end, "End draw"
        )

    def bind_select_tool(self):
        """
        Bind the mouse actions to the select tool
        """
        crv.bind(
            "py-anny-mode", "global", "pointer-1--push", self.select_start, "Select"
        )
        crv.bind(
            "py-anny-mode", "global", "pointer-1--drag", self.select_update, "Move"
        )
        crv.bind(
            "py-anny-mode", "global", "pointer-1--release", self.select_end, "Release"
        )

    def set_active_tool(self, tool_id):
        """
        Set the tool type we're using and bind it to mouse events
        """
        # Clear the current stroke
        if self.current_stroke:
            self.current_stroke.selected = False
            self.current_stroke = None
            self.drag_start_pos = None

        if tool_id == 0:
            # We are selecting
            self.bind_select_tool()
        else:
            self.active_stroke_type = self.stroke_types.get(tool_id, LineStroke)
            self.bind_draw_tool()

    def select_start(self, event):
        # Get frame (we store the annotation against the frame)
        frame = crv.frame()

        source_name = self.get_source_name(event)
        if not source_name:
            return

        # Image space position
        image_pos = crv.eventToImageSpace(source_name, event.pointer())

        # Find closest stoke to threshold
        THRESHOLD = 0.01

        # Deselect current stroke if needed
        if self.current_stroke:
            self.current_stroke.selected = False
            self.current_stroke = None
            self.drag_start_pos = None

        for stroke in self.annotations.strokes[frame]:
            dist = stroke.point_to_stroke_distance(image_pos)
            if dist < THRESHOLD:
                self.current_stroke = stroke
                self.current_stroke.selected = True
                self.drag_start_pos = image_pos

                break

    def select_update(self, event):
        if not self.current_stroke or not self.drag_start_pos:
            # We have nothing selected
            return
        source_name = self.get_source_name(event)

        if not source_name:
            # We have no source
            return

        # Starting position
        x1, y1 = self.drag_start_pos

        # Current position
        x2, y2 = crv.eventToImageSpace(source_name, event.pointer())

        # Calculate delta between start and current
        dx = x2 - x1
        dy = y2 - y1

        # Move to new location
        self.current_stroke.move(dx, dy)

        # Update our start position so the next move works
        self.drag_start_pos = (x2, y2)

    def select_end(self, event):
        self.drag_start_pos = None

    def draw_start(self, event):

        # Get frame (we store the annotation against the frame)
        frame = crv.frame()

        source_name = self.get_source_name(event)
        if not source_name:
            return

        # Image space position
        image_pos = crv.eventToImageSpace(source_name, event.pointer())

        if not self.current_stroke:
            self.current_stroke = self.active_stroke_type(
                start=image_pos,
                end=image_pos,
                source=source_name,
                width=self.inspector.ui.strokeWidthField.value(),
                opacity=self.inspector.ui.strokeOpacityField.value(),
                color=self.inspector.current_stroke_color,
            )
            self.annotations.strokes[frame].append(self.current_stroke)

    def draw_update(self, event):
        if self.current_stroke:
            self.current_stroke.end = crv.eventToImageSpace(
                self.current_stroke.source, event.pointer()
            )

    def draw_end(self, event):
        self.current_stroke = None

    def update_opacity(self):
        if self.current_stroke:
            self.current_stroke.opacity = float(
                self.inspector.ui.strokeOpacityField.value()
            )

    def update_width(self):
        if self.current_stroke:
            self.current_stroke.width = float(
                self.inspector.ui.strokeWidthField.value()
            )

    def get_source_name(self, event):
        """
        Get the name of the source under the mouse
        """

        # We need to get the source to convert the mouse position to image space
        source = crv.sourceAtPixel(event.pointer())
        if not source:
            return

        return source[0]["name"]

    def render(self, event):
        self.annotations.render(event)


def createMode():
    return AnnyMode()
