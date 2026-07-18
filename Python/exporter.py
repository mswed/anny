import os
from typing import Callable, Optional
from pathlib import Path
import rv.commands as crv
from PySide6 import QtGui


class Exporter:
    """
    Class for Anny export operations. Can queue the export of a single or multiple annotated frames. The workflow is this:
    Anny calles for export -> Exporter queues frames -> requestes a frame capture for the first frame -> Anny captures the frame buffer ->
    exporter saves the frame and moves to the next frame or calls a callback if the export is finished
    """

    def __init__(self) -> None:
        self._export_queue = []
        self._is_batch = False
        self._save_dir = None
        self._name = None
        self._save_path = None
        self._exported_files = []
        self._on_export_complete = None

        # Two step capture process, first we mark for capture
        # Then we arm the capture after the first render
        self.capture_pending = False
        self.capture_armed = False

    def queue_frame(
        self, path: Path, callback: Optional[Callable[[list[str]], None]] = None
    ):
        """
        Queue a frame to be captured. The actual capturing happens in the render event.

        Parameters
        ----------
        path : Path
            Path to save the frame
        callback : Optional[Callable[[list[str]], None]]
            Optional callback to run once the export is complete

        """
        self._reset()
        self._save_path = path
        self._on_export_complete = callback
        self._request_capture()

    def queue_all(
        self,
        save_dir: Path,
        file_name: str,
        frames: list[int],
        callback: Optional[Callable[[list[str]], None]] = None,
    ):
        """Queue all annotated frames. Because of the way RV loop works we can't simpley iterate over the frames.
        instead we process one frame at a time and then move to the next one

        Parameters
        ----------
        save_dir : Path
            Directory to save the annotations (user defined)
        file_name : str
            Either anny_annotation or if SG is available the version name
        frames : list[int]
            List of annotated frames
        callback : Optional[Callable[[list[str]], None]]
            Optional callback to run once the export is complete

        """
        self._reset()
        os.makedirs(save_dir, exist_ok=True)
        self._save_dir = save_dir
        self._name = file_name
        self._export_queue = frames
        self._is_batch = True
        self._on_export_complete = callback

        self._process_next()

    def save_annotated_frame(self, image: QtGui.QImage):
        """Save the captured image and continue processing the remaining frames

        Parameters
        ----------
        image : QtGui.QImage
            The captured frame buffer image (passed from Anny's render function for captured frames)
        """
        if image and self._save_path is not None:
            save_path = str(self._save_path)
            if save_path.lower().endswith((".jpg", ".jpeg")):
                image.save(save_path, "JPG", 95)
            else:
                image.save(save_path, "PNG")
            self._exported_files.append(save_path)
            self.capture_pending = False

            if self._is_batch:
                # In batch mode keep processing the queue.
                # The process function will finish the export if needed
                self._export_queue.pop(0)
                self._process_next()
            else:
                # For a single frame export finish the export
                self._finish()

    def on_frame_changed(self):
        """
        When the frame changes check if we need to capture it. This is called by Anny on frame change.
        """
        if self._export_queue and crv.frame() == self._export_queue[0]:
            # We are expporting a frame AND the current frame matches the one we want to export
            self._request_capture()

    def _process_next(self):
        """Advance in the export queue.
        If the queue is empty the process is finished.
        If we are already on the correct frame we simply capture item
        otherwise we move to the target frame which will trigger a render
        """
        if not self._export_queue:
            self._finish()
            return

        target = self._export_queue[0]
        if crv.frame() == target:
            # We are already on the right frame, just capture
            self._request_capture()
        else:
            # We need to move to the target frame. This triggers
            # a frame changed event and on_frame_changed is called to
            # request the capture
            crv.setFrame(target)

    def _request_capture(self):
        """Tell Anny's render function that it needs to capture the frame"""
        if self._is_batch and self._save_dir is not None and self._name is not None:
            self._save_path = self._build_export_path(self._save_dir, self._name)

        self.capture_pending = True
        crv.redraw()

    def _build_export_path(self, save_dir: Path, name: str) -> Path:
        """Build the full export path for batch export

        Parameters
        ----------
        save_dir : Path
            The save direcotry
        name : str
            The base name for the image as provided by Any

        Returns
        -------
        Path
            The full save path for the annotated frame

        """
        return save_dir / f"annotation_{name}.{crv.frame()}.png"

    def _finish(self):
        """Finish the export by calling the optional call back and reseting the Exporter's state"""
        if self._on_export_complete:
            self._on_export_complete(self._exported_files)

        self._reset()

    def _reset(self):
        """Reset all the Exporter state so the next export operation will work"""
        self._export_queue = []
        self._is_batch = False
        self._save_dir = None
        self._name = None
        self._save_path = None
        self._exported_files = []
        self._on_export_complete = None

        self.capture_pending = False
