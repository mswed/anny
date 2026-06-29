from rv.rvtypes import *
import rv.commands as crv
from rv.extra_commands import *
import os
from utils import SourceName, SourceNode, ImagePoint
from pprint import pprint

from inspector import Inspector
from annotations import (
    AnnotationLayer,
    LineStroke,
    RectStroke,
)
from stroke_text import TextStroke
from stroke_freehand import FreehandStroke
from stroke_ellipse import EllipseStroke


class AnnyMode(MinorMode):
    def __init__(self) -> None:
        MinorMode.__init__(self)
        self.inspector = Inspector(mode=self)
        self.annotations = AnnotationLayer()
        self.current_stroke = None
        self.drag_start_pos = None
        self.drag_type = ""
        self.stroke_types = {
            1: FreehandStroke,
            2: LineStroke,
            3: RectStroke,
            4: EllipseStroke,
            5: TextStroke,
        }
        self.capture_frame = False
        self._export_queue = []
        self.frames_to_save = 0
        self.save_dir = None
        self.save_to = None

        self.init(
            "py-anny-mode",
            [
                ("render", self.render, "Render overlay"),
                ("frame-changed", self.on_frame_changed, "Save frame"),
                (
                    "key-down--delete",
                    self.delete_selected_stroke,
                    "Delete annotation",
                ),
            ],
            None,
            [
                (
                    "Anny",
                    [
                        ("Show UI", self.show_ui, "=", None),
                        ("Next Annotation", self.next_annotation, "'", None),
                        ("Previous Annotation", self.previous_annotation, ";", None),
                        ("Export Frame", self.export_annotation, None, None),
                        ("Export All Frames", self.export_all_annotations, None, None),
                    ],
                )
            ],
            "py-anny-mode",  # Needed to set the mode to override other mode binding
            -10,  # set the override value (default is 0)
        )

    def show_ui(self, event):
        # Bind the select tool for start
        self.bind_select_tool()
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

    def set_active_tool(self, tool_id: int):
        """
        Set the tool type we're using and bind it to mouse events based on the stroke_types dict


        Parameters
        ----------
        tool_id : int
            The tool id (0 is select)

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

    def update_ui(self):
        """
        Update the UI with the selected stroke info
        """
        if not self.current_stroke:
            return

        props = self.current_stroke.editable_properties
        if "width" in props:
            # Update width
            self.inspector.ui.strokeWidthField.setValue(self.current_stroke.width)

        if "color" in props:
            # Update color
            r, g, b, a = self.current_stroke.color
            self.inspector.ui.strokeColorBtn.setStyleSheet(
                f"background-color: rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, 255); border: none;"
            )

        if "opacity" in props:
            # Update opacity
            self.inspector.ui.strokeOpacityField.setValue(self.current_stroke.opacity)

        # Update caps
        if "start_cap" in props:
            self.inspector.ui.startCapCb.setCurrentIndex(
                self.inspector.ui.startCapCb.findData(self.current_stroke.start_cap)
            )
        if "end_cap" in props:
            self.inspector.ui.endCapCb.setCurrentIndex(
                self.inspector.ui.endCapCb.findData(self.current_stroke.end_cap)
            )

        if "fill_color" in props:
            # Update fill color
            r, g, b, a = self.current_stroke.fill_color
            self.inspector.ui.fillColorBtn.setStyleSheet(
                f"background-color: rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, 255); border: none;"
            )

        if "fill_opacity" in props:
            # Update fill opacity
            self.inspector.ui.fillOpacityField.setValue(
                self.current_stroke.fill_opacity
            )

        if "text" in props:
            # Update text
            self.inspector.ui.textField.setText(self.current_stroke.text)

        if "smoothing" in props:
            # Update smoothing
            self.inspector.ui.strokeSmoothingField.setValue(
                self.current_stroke.smoothing
            )

    def select_start(self, event):
        # Get frame (we store the annotation against the frame)
        frame = crv.frame()

        source_name, source_node = self.get_source_name(event)
        if not source_name:
            return

        # Image space position
        x, y = crv.eventToImageSpace(source_name, event.pointer())
        image_point = ImagePoint(x, y, source=source_name)

        # Deselect current stroke if needed
        if self.current_stroke:
            self.current_stroke.selected = False
            self.current_stroke.editing = False
            self.current_stroke = None
            self.drag_start_pos = None
            self.drag_type = ""

        for stroke in self.annotations.sources[source_node].strokes_at_frame(frame):
            if stroke.detect_handle_selection(image_point, "start"):
                self.drag_type = "start"
            elif stroke.detect_handle_selection(image_point, "end"):
                self.drag_type = "end"
            elif stroke.detect_selection(image_point):
                self.drag_type = "stroke"
            else:
                continue

            if self.drag_type != "":
                self.current_stroke = stroke
                self.current_stroke.selected = True
                self.drag_start_pos = image_point

                self.update_ui()

                break

    def select_update(self, event):
        if not self.current_stroke or not self.drag_start_pos:
            # We have nothing selected
            return
        source_name, source_node = self.get_source_name(event)

        if not source_name:
            # We have no source
            return

        # Starting position
        starting_position = self.drag_start_pos

        # Current position
        x, y = crv.eventToImageSpace(source_name, event.pointer())
        current_position = ImagePoint(x, y, source=source_name)

        # Calculate delta between start and current
        dx = current_position.x - starting_position.x
        dy = current_position.y - starting_position.y

        # Move to new location
        self.current_stroke.move(dx, dy, move_type=self.drag_type)

        # Update our start position so the next move works
        self.drag_start_pos.x = current_position.x
        self.drag_start_pos.y = current_position.y

        crv.redraw()

    def select_end(self, event):
        self.drag_start_pos = None

    def draw_start(self, event):

        # Get frame (we store the annotation against the frame)
        frame = crv.frame()

        source_name, source_node = self.get_source_name(event)
        if not source_name:
            return

        # Start pose
        x, y = crv.eventToImageSpace(source_name, event.pointer())
        start_pos = ImagePoint(x, y, source=source_name)

        # End pose (we need a seperate point so we don't point to the same object)
        end_pos = ImagePoint(x, y, source=source_name)

        if not self.current_stroke:
            self.current_stroke = self.active_stroke_type(
                start=start_pos,
                end=end_pos,
                source=source_name,
                width=self.inspector.ui.strokeWidthField.value(),
                opacity=self.inspector.ui.strokeOpacityField.value(),
                color=self.inspector.current_stroke_color,
                start_cap=self.inspector.ui.startCapCb.currentData(),
                end_cap=self.inspector.ui.endCapCb.currentData(),
                text=self.inspector.ui.textField.toPlainText(),
                fill_color=self.inspector.current_fill_color,
                fill_opacity=self.inspector.ui.fillOpacityField.value(),
                smoothing=self.inspector.ui.strokeSmoothingField.value(),
            )

            self.annotations.add_stroke(source_node, frame, self.current_stroke)

    def draw_update(self, event):
        if self.current_stroke:
            image_x, image_y = crv.eventToImageSpace(
                self.current_stroke.source, event.pointer()
            )

            point = ImagePoint(image_x, image_y, source=self.current_stroke.source)
            self.current_stroke.update_draw(point)
            crv.redraw()

    def draw_end(self, event):
        self.current_stroke = None

    def get_source_name(self, event):
        """Get the source name under the mouse. Used to convert clicks to image space

        Parameters
        ----------
        event : crv.Event
            The rv event that called the function. In our case a mouse click

        Returns
        -------
        String
            Source name

        """
        # We need to get the source to convert the mouse position to image space
        source = crv.sourceAtPixel(event.pointer())
        if not source:
            return

        return SourceName(source[0]["name"]), SourceNode(source[0]["node"])

    def delete_selected_stroke(self, event):
        frame = crv.frame()
        if self.current_stroke:
            source = self.current_stroke.source
            self.annotations.delete_stroke(source, frame, self.current_stroke)
            self.current_stroke = None

        crv.redraw()

    def clear_frame(self):
        # source = self.get_source_name()
        frame = crv.frame()
        current_sources = crv.sourcesRendered()
        for source in current_sources:
            self.annotations.clear_frame(source["name"], frame)

        self.current_stroke = None
        crv.redraw()

    def unbind(self):
        """
        Unbind all mouse actions so other modes can take over
        """
        crv.unbind(
            "py-anny-mode",
            "global",
            "pointer-1--push",
        )
        crv.unbind(
            "py-anny-mode",
            "global",
            "pointer-1--drag",
        )
        crv.unbind(
            "py-anny-mode",
            "global",
            "pointer-1--release",
        )

    def next_annotation(self, event):
        frame = crv.frame()
        source = crv.sourcesRendered()
        source_name = source[0]["node"]
        next_frame = self.annotations.get_next_frame(source_name, frame)
        crv.setFrame(next_frame)

    def previous_annotation(self, event):
        frame = crv.frame()
        source = crv.sourcesRendered()
        source_name = source[0]["node"]
        previous_frame = self.annotations.get_previous_frame(source_name, frame)
        crv.setFrame(previous_frame)

    def export_annotation(self, event):
        self.save_to = self.inspector.get_save_path()
        if self.save_to:
            # Cancel any batch exports
            self._export_queue = []
            self._capture_current_frame(batch=False)

    def export_all_annotations(self, event):
        self.save_dir = self.inspector.get_save_path("directory")
        if self.save_dir:
            os.makedirs(self.save_dir, exist_ok=True)
            source = crv.sourcesRendered()
            source_name = source[0]["node"]
            self._export_queue = self.annotations.get_annotated_frames(source_name)
            self._advance_export()

    def _advance_export(self):
        if not self._export_queue:
            return

        target = self._export_queue[0]
        if crv.frame() == target:
            # We are already on the right frame, just capture
            self._capture_current_frame()
        else:
            # We need to move to the target frame
            crv.setFrame(target)

    def _capture_current_frame(self, batch=True):
        if batch:
            self.save_to = self.save_dir / f"annotation.{crv.frame()}.jpg"
        self.capture_frame = True
        crv.redraw()

    def on_frame_changed(self, event):
        if self._export_queue and crv.frame() == self._export_queue[0]:
            self._capture_current_frame()

    def render(self, event):
        self.annotations.render(event)
        if self.capture_frame:
            image = self.annotations.capture_frame_buffer(event)
            image.save(str(self.save_to))
            self.capture_frame = False

            if self._export_queue:
                self._export_queue.pop(0)
                self._advance_export()
            else:
                self.save_dir = None
                self.save_to = None


def createMode():
    return AnnyMode()
