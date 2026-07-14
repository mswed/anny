import os
import rv.commands as crv


class Exporter:
    def __init__(self) -> None:
        self._export_queue = []
        self._is_batch = False
        self._save_dir = None
        self._name = None
        self._save_path = None
        self._exported_files = []
        self._on_export_complete = None

        self.capture_pending = False

    def queue_frame(self, path, callback=None):
        """
        Queue a frame to be captured. The actual capturing happens in the render event.

        Parameters
        ----------
        path : str
            Path to save

        """
        self._reset()
        self._save_path = path
        self._on_export_complete = callback
        self._request_capture()

    def queue_all(self, save_dir, file_name, frames, callback):
        """
        Queue a all annotated frames to be exported to a directory. Due to the way RV processes it's loop
        we can not simply loop over the frame list. Instead we create a queue and
        advance through it one frame at a time

        Parameters
        ----------
        event : Event
            The export all annotation menu item has been clicked

        """
        print("queuing all frames")
        self._reset()
        os.makedirs(save_dir, exist_ok=True)
        self._save_dir = save_dir
        self._name = file_name
        self._export_queue = frames
        self._is_batch = True
        self._on_export_complete = callback
        print("Queued")

        self._process_next()

    def save_annotated_frame(self, image):
        if image and self._save_path is not None:
            save_path = str(self._save_path)
            if save_path.lower().endswith((".jpg", ".jpeg")):
                image.save(save_path, "JPG", 95)
            else:
                image.save(save_path, "PNG")
            self._exported_files.append(save_path)
            self.capture_pending = False

            if self._is_batch:
                self._export_queue.pop(0)
                self._process_next()
            else:
                self._finish()

    def _finish(self):
        print("export is done should be calling callback")
        if self._on_export_complete:
            self._on_export_complete(self._exported_files)

        self._reset()

    def on_frame_changed(self):
        """When the frame changes check if we need to capture it

        Parameters
        ----------
        event : Event
            The viewport frame has changed

        """
        if self._export_queue and crv.frame() == self._export_queue[0]:
            # We are expporting a frame AND the current frame matches the one we want to export
            self._request_capture()

    def _process_next(self):
        """Advance in the export queue. If we are already on the correct frame we simply capture item
        otherwise we move to the target frame which will trigger a render
        """
        print("processing next")
        if not self._export_queue:
            print("no queue")
            self._finish()
            return

        target = self._export_queue[0]
        print("target is", target)
        if crv.frame() == target:
            # We are already on the right frame, just capture
            self._request_capture()
        else:
            # We need to move to the target frame. This triggers
            # a frame changed event and on_frame_changed is called to
            # request the capture
            crv.setFrame(target)

    def _request_capture(self):
        print("requesting capture", self._is_batch, self._save_dir, self._name)
        if self._is_batch and self._save_dir is not None and self._name is not None:
            self._save_path = self._build_export_path(self._save_dir, self._name)

        self.capture_pending = True
        print("set to capture")
        crv.redraw()

    def _build_export_path(self, save_dir, name):
        return save_dir / f"annotation_{name}.{crv.frame()}.png"

    def _reset(self):
        self._export_queue = []
        self._is_batch = False
        self._save_dir = None
        self._name = None
        self._save_path = None
        self._exported_files = []
        self._on_export_complete = None

        self.capture_pending = False
