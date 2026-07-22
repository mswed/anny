from importlib.util import find_spec
from typing import Optional, Any
import time
from utils import Note
from pprint import pprint

try:
    from tank_vendor.shotgun_api3 import ShotgunError
except ImportError:
    ShotgunError = Exception


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

    def get_active_users(self) -> dict[str, Any]:
        if self.sg is None:
            return {"ok": False, "message": "No ShotGrid connection found"}

        users = self.sg.find(
            "HumanUser", [["sg_status_list", "is", "act"]], ["name", "login"]
        )
        groups = self.sg.find("Group", [], ["code"])

        pprint(users)
        pprint(groups)

    def create_note(self, note: Note) -> dict:
        if self.sg is None:
            return {"ok": False, "message": "No ShotGrid connection found"}

        try:
            res = self.sg.create("Note", note)
            return {"ok": True, "message": res}
        except ShotgunError as e:
            return {"ok": False, "message": str(e)}

    def upload_annotation(self, note_id: int, path: str) -> dict[str, Any]:
        if not self.sg:
            return {"ok": False, "message": "No ShotGrid connection found"}

        errors = []
        for attempt in range(4):
            try:
                self.sg.upload(
                    "Note",
                    note_id,
                    path,
                    field_name="attachments",
                )
                return {"ok": True, "message": f"{path} uploaded succesfully"}
            except ShotgunError as e:
                errors.append(str(e))
                if attempt < 3:
                    time.sleep(2**attempt)

        return {"ok": False, "message": [errors[-1]]}
