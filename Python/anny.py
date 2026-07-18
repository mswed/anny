from __future__ import annotations
import os
import tempfile
from pathlib import Path
import logging
from rv.rvtypes import MinorMode
import rv.commands as crv
from rv.qtutils import sessionWindow
from typing import Optional, TYPE_CHECKING
from utils import ImagePoint, Note, Source

from sg_integration import ShotGrid
from inspector import Inspector
from annotations import AnnotationLayer
from exporter import Exporter
from stroke_text import TextStroke
from stroke_freehand import FreehandStroke
from stroke_ellipse import EllipseStroke
from stroke_rect import RectStroke
from stroke_line import LineStroke
from pprint import pprint

if TYPE_CHECKING:
    from rv_stubs import Event

log = logging.getLogger(__name__)
log.setLevel("DEBUG")


class AnnyMode(MinorMode):
    def __init__(self) -> None:
        MinorMode.__init__(self)
        self.shotgrid = ShotGrid()
        self.inspector = Inspector(mode=self, parent=sessionWindow())
        self.annotations = AnnotationLayer()
        self.exporter = Exporter()
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
        self._capture_armed = False

        self.init(
            "py-anny-mode",
            [
                ("render", self.render, "Render overlay"),
                ("frame-changed", self.on_frame_changed, "Save frame"),
                (
                    "source-group-complete",
                    self.initialize_integration,
                    "Try to initialize SG integration",
                ),
                (
                    "key-down--delete",
                    self.delete_selected_stroke,
                    "Delete annotation",
                ),
                (
                    "key-down--=",
                    self.show_ui,
                    "Show UI",
                ),
                (
                    "key-down--'",
                    self.next_annotation,
                    "Next annotation",
                ),
                (
                    "key-down--;",
                    self.previous_annotation,
                    "Previous annotation",
                ),
            ],
            None,
            [
                (
                    "Anny Tools",  # For some reason this shows up on MacOS
                    [
                        ("Show UI", self.show_ui, "=", None),
                        ("Next Annotation", self.next_annotation, "'", None),
                        ("Previous Annotation", self.previous_annotation, ";", None),
                        ("_", None),
                        ("Export Frame", self.export_annotation, None, None),
                        (
                            "Export All Frames",
                            self.export_all_annotations,
                            None,
                            None,
                        ),
                        ("SG note", self.create_sg_note, None, None),
                    ],
                )
            ],
            "z",  # Set the binding priority so they take over, but still allow the timeline to scrub
        )

    # --- UI ---
    def show_ui(self, event: Event):
        """Show the Anny UI and bind the select tool to start

        Parameters
        ----------
        event : Event
            The RV event that called the action
        """
        # Bind the select tool for start
        self._bind_select_tool()
        self.inspector.show()

        # import sgtk
        #
        # print(">>>", sgtk.platform.current_engine())
        # crv.sendInternalEvent("external-sgtk-initialize")
        #
        # import sgtk
        #
        # engine = sgtk.platform.current_engine()
        # source = Source(crv.sourcesRendered()[0])
        # print(source.name)
        # print(source.node)
        # print(source.sg_data)
        # source_name = source["node"]
        # pprint(crv.properties(source_name))
        #
        # info = crv.getStringProperty(f"{source_name}.media.name")
        # print(">>>>", info)
        # info = crv.getStringProperty(f"{source_name}.media.movie")
        # print(">>>>", info)
        # info = crv.getStringProperty(f"{source_name}.tracking.info")
        # sg_data = {}
        # for i in range(0, len(info) - 1, 2):
        #     sg_data[info[i]] = info[i + 1]
        # pprint(sg_data)
        #
        # subject = "Moshe's note it is!"
        # shot_id = int(sg_data["shot"].split("|")[0].split("_")[1])
        # version_id = int(sg_data["id"])
        # note_links = [
        #     {"type": "Shot", "id": shot_id},
        #     {"type": "Version", "id": version_id},
        # ]
        # user = engine.context.user
        # content = "This is some note text"
        # pprint("--------- info --------------")
        # print(project_id)
        # print(subject)
        # print(note_links)
        # print(user)
        # print(content)
        # print("------------------------------")
        # data = {
        #     "project": {"type": "Project", "id": project_id},
        #     "subject": subject,
        #     "note_links": note_links,
        #     "user": user,
        #     "content": content,
        # }
        # sg = engine.shotgun
        # note = sg.create("Note", data)
        # img = "/home/mswed/arrow.png"
        # success = False
        # for _ in range(4):
        #     try:
        #         success = sg.upload("Note", note["id"], img, field_name="attachments")
        #         if success:
        #             break
        #     except Exception as e:
        #         print(e)
        #         pass

    def _update_ui_states(self, stroke_props: list[str]):
        """Enable and/or disable ui features based on the stroke type

        Parameters
        ----------
        stroke_props : list[str]
            List of stroke props

        """
        for prop, widgets in self.inspector.PROPERTY_WIDGETS.items():
            is_enabled = prop in stroke_props
            for w in widgets:
                getattr(self.inspector.ui, w).setEnabled(is_enabled)

    def _update_ui_values(self):
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
            self.inspector.current_stroke_color = (r, g, b, a)
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
            self.inspector.current_fill_color = (r, g, b, a)
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
            self.inspector.ui.strokeSmoothingField.setEnabled(True)
            self.inspector.ui.strokeSmoothingField.setValue(
                self.current_stroke.smoothing
            )
        else:
            self.inspector.ui.strokeSmoothingField.setEnabled(False)

    # --- Binding ---
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
            self._bind_select_tool()
        else:
            self.active_stroke_type = self.stroke_types.get(tool_id, LineStroke)
            self._bind_draw_tool()
            self._update_ui_states(self.active_stroke_type.editable_properties)

    def _bind_draw_tool(self):
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

    def _bind_select_tool(self):
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

    # --- Drawing ---
    def draw_start(self, event: Event):
        """The start of the stroke drawing process

        Parameters
        ----------
        event : Event
            The user clicked the mouse while a drawing tool is enabled

        """
        # Get frame (we store the annotation against the frame)
        frame = crv.frame()

        source = self._get_source(event)
        if not source:
            return

        # Start pose
        x, y = crv.eventToImageSpace(source.name, event.pointer())
        start_pos = ImagePoint(x, y, source=source)

        # End pose (we need a seperate point so we don't point to the same object)
        end_pos = ImagePoint(x, y, source=source)

        if not self.current_stroke:
            font = self.inspector.ui.fontCb.currentFont()
            font.setPointSize(self.inspector.ui.fontSizeField.value())

            self.current_stroke = self.active_stroke_type(
                start=start_pos,
                end=end_pos,
                source=source,
                width=self.inspector.ui.strokeWidthField.value(),
                opacity=self.inspector.ui.strokeOpacityField.value(),
                color=self.inspector.current_stroke_color,
                start_cap=self.inspector.ui.startCapCb.currentData(),
                end_cap=self.inspector.ui.endCapCb.currentData(),
                text=self.inspector.ui.textField.toPlainText(),
                fill_color=self.inspector.current_fill_color,
                fill_opacity=self.inspector.ui.fillOpacityField.value(),
                smoothing=self.inspector.ui.strokeSmoothingField.value(),
                font=font,
            )

            self.annotations.add_stroke(source, frame, self.current_stroke)

    def draw_update(self, event: Event):
        """
        The user is drawing a stroke

        Parameters
        ----------
        event : Event
            The mouse is dragging after a mouse click event

        """
        if self.current_stroke:
            image_x, image_y = crv.eventToImageSpace(
                self.current_stroke.source.name, event.pointer()
            )

            point = ImagePoint(image_x, image_y, source=self.current_stroke.source)
            self.current_stroke.update_draw(point)
            crv.redraw()

    def draw_end(self, event: Event):
        """The user finished drawing the stroke

        Parameters
        ----------
        event : Event
            The mouse click is released

        """
        if self.current_stroke:
            if not self.current_stroke.is_valid:
                frame = crv.frame()
                source = self.current_stroke.source
                self.annotations.delete_stroke(source, frame, self.current_stroke)

        self.current_stroke = None

    # --- Selection and Editing ---
    def select_start(self, event: Event):
        """Select a stroke

        Parameters
        ----------
        event : Event
            The event that called the selection process (mouse click in this case)

        """
        # Get frame (we store the annotation against the frame)
        frame = crv.frame()

        source = self._get_source(event)
        if not source:
            return

        # Image space position
        x, y = crv.eventToImageSpace(source.name, event.pointer())
        image_point = ImagePoint(x, y, source=source)

        # Deselect current stroke if needed
        if self.current_stroke:
            self.current_stroke.selected = False
            self.current_stroke.editing = False
            self.current_stroke = None
            self.drag_start_pos = None
            self.drag_type = ""

        for stroke in self.annotations.sources[source.node].strokes_at_frame(frame):
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

                self._update_ui_states(self.current_stroke.editable_properties)
                self._update_ui_values()

                break

    def select_update(self, event: Event):
        """Draging after a stroke selection moves the stroke

        Parameters
        ----------
        event : Event
            The user is dragging the stroke

        """
        if not self.current_stroke or not self.drag_start_pos:
            # We have nothing selected
            return

        source = self._get_source(event)
        if not source:
            return

        # Starting position
        starting_position = self.drag_start_pos

        # Current position
        x, y = crv.eventToImageSpace(source.name, event.pointer())
        current_position = ImagePoint(x, y, source=source)

        # Calculate delta between start and current
        dx = current_position.x - starting_position.x
        dy = current_position.y - starting_position.y

        # Move to new location
        self.current_stroke.move(dx, dy, move_type=self.drag_type)

        # Update our start position so the next move works
        self.drag_start_pos.x = current_position.x
        self.drag_start_pos.y = current_position.y

        crv.redraw()

    def select_end(self, event: Event):
        """When we're done dragging a stroke we disable the drag_start_pos attr

        Parameters
        ----------
        event : Event
            The user stopped dragging

        """
        self.drag_start_pos = None

    def delete_selected_stroke(self, event):
        frame = crv.frame()
        if self.current_stroke:
            source = self.current_stroke.source
            self.annotations.delete_stroke(source, frame, self.current_stroke)
            self.current_stroke = None

        crv.redraw()

    def clear_frame(self):
        """Clear the current frame of all strokes"""

        frame = crv.frame()
        current_sources = crv.sourcesRendered()
        for source in current_sources:
            s = Source(source)
            self.annotations.clear_frame(s, frame)

        self.current_stroke = None
        crv.redraw()

    # --- Navigation ---
    def next_annotation(self, event: Event):
        """Go to the next annotated frame

        Parameters
        ----------
        event : Event
            The next annotation menu item has been clicked

        """
        frame = crv.frame()
        source = crv.sourcesRendered()
        source_node = source[0]["node"]
        next_frame = self.annotations.get_next_frame(source_node, frame)
        crv.setFrame(next_frame)

    def previous_annotation(self, event: Event):
        """Go to the prvious annotated frame

        Parameters
        ----------
        event : Event
            The previous annotation menu item has been clicked

        """
        frame = crv.frame()
        source = crv.sourcesRendered()
        source_node = source[0]["node"]
        previous_frame = self.annotations.get_previous_frame(source_node, frame)
        crv.setFrame(previous_frame)

    # --- Exporting ---
    def export_annotation(self, event: Event):
        """Export a single annotated frame

        Parameters
        ----------
        event : Event
            The export annotation menu item has been clicked

        """
        save_path = self.inspector.get_save_path()
        if save_path:
            self.exporter.queue_frame(save_path, callback=self.on_export_complete)

    def export_all_annotations(self, event: Event):
        """
        Shows a dialog allowing the user to select an export dir
        Parameters
        ----------
        event : Event
            The export all annotation menu item has been clicked

        """
        save_dir = self.inspector.get_save_path("directory")
        source = Source(crv.sourcesRendered()[0])
        name = self._get_annotation_name(source)
        frames = self.annotations.get_annotated_frames(source)
        if save_dir:
            self.exporter.queue_all(
                save_dir=save_dir,
                file_name=name,
                frames=frames,
                callback=self.on_export_complete,
            )

    def on_export_complete(self, frames: list):
        """Called when the exported is finished exporting frames. Shows a confirmation dialog

        Parameters
        ----------
        frames : list
            List of frames that were exported

        """
        self.inspector.show_message("Frame export completed!")

    def _get_annotation_name(self, source: Source) -> str:
        """Get the base file name for an annotation export

        Parameters
        ----------
        source : Source
            The annotation source

        Returns
        -------
        str

            any_annotation if we don't have a shotgrid source or anny_shotgrid_version_name

        """
        if self.shotgrid.is_initialized() and source is not None:
            # Grab the annotation name from SG
            return f"anny_{source.version_name}"

        return "anny_annotation"

    def on_frame_changed(self, event: Event):
        """When the frame changes check if we need to capture it

        Parameters
        ----------
        event : Event
            The viewport frame has changed

        """
        self.exporter.on_frame_changed()

    # --- Production Integration ---
    def initialize_integration(self, event: Event):
        log.debug("Source load completed initializing SG")
        if self.shotgrid.has_sgtk():
            self.shotgrid.initialize()

    def create_sg_note(self, event: Event):
        source = Source(crv.sourcesRendered()[0])

        # We first create the SG note
        note_links = [
            {"type": "Shot", "id": source.shot_id},
            {"type": "Version", "id": source.version_id},
        ]

        note: Note = {
            "project": {"type": "Project", "id": source.project_id},
            "subject": "Temp subject",
            "note_links": note_links,
            "user": self.shotgrid.user,
            "content": "Note body",
        }

        self.shotgrid.create_note(note)

        # # We first need to export all of the annotations
        # save_dir = self.inspector.get_save_path("directory")
        # name = self._get_annotation_name(source)
        # frames = self.annotations.get_annotated_frames(source)
        # if save_dir:
        #     self.exporter.queue_all(
        #         save_dir=save_dir,
        #         file_name=name,
        #         frames=frames,
        #         callback=self.on_export_complete,
        #     )
        # pass

    def upload_to_sg(self, annotated_frames):
        print(annotated_frames)

    # --- Helpers ---
    def _get_source(self, event: Event) -> Optional[Source]:
        """Get the source name and node under the mouse. Used to convert clicks to image space

        Parameters
        ----------
        event : Event
            The rv event that called the function. In our case a mouse click

        Returns
        -------
        Optional[Source]
            Source name and node

        """
        # We need to get the source to convert the mouse position to image space
        source = crv.sourceAtPixel(event.pointer())
        if not source:
            return None

        return Source(source[0])

    # --- Rendering ---
    def render(self, event: Event):
        """Render all of the annotations in the layer and if the frame is marked for
        capture save it

        Parameters
        ----------
        event : Event
            RV's internal render event. RV calls it regularly, but we also force it using redraw() during export

        """
        # We first reject the event so the UI render can work
        event.reject()

        # Then we render
        self.annotations.render(event)
        if self.exporter.capture_pending:
            image = self.annotations.capture_frame_buffer(event)
            self.exporter.save_annotated_frame(image)

        # When a captrure is requeted we save the image
        if self.capture_frame:
            if self._capture_armed:
                # We are capturing the frame
                image = self.annotations.capture_frame_buffer(event)

                if image and self.save_to is not None:
                    save_path = str(self.save_to)
                    if save_path.lower().endswith((".jpg", ".jpeg")):
                        image.save(save_path, "JPG", 95)
                    else:
                        image.save(save_path, "PNG")
                    self.capture_frame = False

                if self._export_queue:
                    self._export_queue.pop(0)
                    self._advance_export()
                else:
                    self.save_dir = None
                    self.save_to = None

                self._capture_armed = False
            else:
                # We have a render delay arm the capture and queue a render
                self._capture_armed = True
                crv.redraw()


def createMode():
    return AnnyMode()
