from importlib.util import find_spec
from typing import Optional
from utils import Note


class ShotGrid:
    def __init__(self) -> None:
        self.engine = None
        self.sg = None

    @property
    def user(self) -> dict:
        if self.engine:
            return self.engine.context.user
        return {}

    def has_sgtk(self):
        spec = find_spec("sgtk")
        if spec:
            return True

        print(
            "SGTK module not found. Make sure you've enabled the shotgrid mode under packages"
        )
        return False

    def is_initialized(self):
        return self.engine is not None and self.sg is not None

    def initialize(self):
        if self.has_sgtk():
            import sgtk

            self.engine = sgtk.platform.current_engine()
            self.sg = self.engine.shotgun

    def create_note(self, note: Note) -> Optional[dict]:
        if self.sg is None:
            return

        try:
            res: dict = self.sg.create("Note", note)
            return res
        except Exception as e:
            print(e)
            return None

    def upload_annotation(self, note, path):
        if not self.sg:
            return

        success = False
        for _ in range(4):
            try:
                success = self.sg.upload(
                    "Note", note["id"], path, field_name="attachments"
                )
                if success:
                    break
            except Exception as e:
                print(e)
                pass
