from importlib.util import find_spec
import time
from utils import Note, SGResult

try:
    from tank_vendor.shotgun_api3 import ShotgunError
except ImportError:
    ShotgunError = Exception


class ShotGrid:
    def __init__(self) -> None:
        self.engine = None
        self.sg = None
        self.users = []
        self.groups = []
        self.tags = []

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
        if self.is_initialized():
            return
        try:
            import sgtk

            self.engine = sgtk.platform.current_engine()
            self.sg = self.engine.shotgun
            users = self.get_active_users()
            if users["ok"]:
                self.users = users["data"]
            groups = self.get_groups()
            if groups["ok"]:
                self.groups = groups["data"]
            tags = self.get_tags()
            if tags["ok"]:
                self.tags = tags["data"]
        except Exception as e:
            return

    def get_active_users(self) -> SGResult:
        if self.sg is None:
            return {"ok": False, "message": "No ShotGrid connection found", "data": []}

        try:
            users = self.sg.find(
                "HumanUser", [["sg_status_list", "is", "act"]], ["name", "login"]
            )
        except ShotgunError as e:
            return {"ok": False, "message": str(e), "data": []}

        return {"ok": True, "message": "", "data": users}

    def get_groups(self) -> SGResult:
        if self.sg is None:
            return {"ok": False, "message": "No ShotGrid connection found", "data": []}

        try:
            groups = self.sg.find("Group", [], ["code"])
        except ShotgunError as e:
            return {"ok": False, "message": str(e), "data": []}

        return {"ok": True, "message": "", "data": groups}

    def get_tags(self) -> SGResult:
        if self.sg is None:
            return {"ok": False, "message": "No ShotGrid connection found", "data": []}

        try:
            tags = self.sg.find("Tag", [], ["name"])
        except ShotgunError as e:
            return {"ok": False, "message": str(e), "data": []}

        return {"ok": True, "message": "", "data": tags}

    def get_active_status_list(self, entity_type: str, project_id: int) -> SGResult:
        if self.sg is None:
            return {"ok": False, "message": "No ShotGrid connection found", "data": []}

        try:
            schema = self.sg.schema_field_read(
                entity_type, "sg_status_list", {"type": "Project", "id": project_id}
            )
            sg_status_list = schema.get("sg_status_list", {})
            properties = sg_status_list.get("properties", {})
            active_values = properties.get("display_values", {}).get("value", {})
            hidden_values = properties.get("hidden_values", {}).get("value", [])
            for v in hidden_values:
                active_values.pop(v)

            # Convert the dict to a list so we maintain our standard SG Result dict
            active_values = [(k, v) for k, v in active_values.items()]

            return {"ok": True, "message": "", "data": sorted(active_values)}

        except ShotgunError as e:
            return {"ok": False, "message": str(e), "data": []}

    def get_field_valid_values(self, entity_type: str, field_name: str) -> SGResult:
        """Get valid dropdown values for a ShotGrid field

        Parameters
        ----------
        entity_type : str
            The entity we're looking at
        field_name : str
            The field we're interested in

        Returns
        -------
        SGResult
            ok: True if we got the field valid values, else False
            message: empty if we got the values, else error message
            data: list of valid values if any were found, else empty list


        """
        if self.sg is None:
            return {"ok": False, "message": "No ShotGrid connection found", "data": []}

        try:
            schema = self.sg.schema_field_read(entity_type)
            field = schema.get(field_name)
            if field is None:
                return {
                    "ok": False,
                    "message": f"Field {field_name} not found on {entity_type}",
                    "data": [],
                }

            properties = field.get("properties")
            valid_values = properties.get("valid_values", {}).get("value", [])
            return {"ok": True, "message": "", "data": valid_values}

        except ShotgunError as e:
            return {"ok": False, "message": str(e), "data": []}

    def set_version_status(self, version_id: int, status: str):
        if self.sg is None:
            return {"ok": False, "message": "No ShotGrid connection found", "data": []}

        try:
            res = self.sg.update("Version", version_id, {"sg_status_list": status})
            return {"ok": True, "message": "", "data": [res]}
        except ShotgunError as e:
            return {"ok": False, "message": str(e), "data": []}

    def create_note(self, note: Note) -> SGResult:
        if self.sg is None:
            return {"ok": False, "message": "No ShotGrid connection found", "data": []}

        try:
            res = self.sg.create("Note", note)
            return {"ok": True, "message": "", "data": [res]}
        except ShotgunError as e:
            return {"ok": False, "message": str(e), "data": []}

    def upload_annotation(self, note_id: int, path: str) -> SGResult:
        if not self.sg:
            return {"ok": False, "message": "No ShotGrid connection found", "data": []}

        errors = []
        for attempt in range(4):
            try:
                self.sg.upload(
                    "Note",
                    note_id,
                    path,
                    field_name="attachments",
                )
                return {
                    "ok": True,
                    "message": f"{path} uploaded succesfully",
                    "data": [],
                }
            except ShotgunError as e:
                errors.append(str(e))
                if attempt < 3:
                    time.sleep(2**attempt)

        return {"ok": False, "message": errors[-1], "data": []}
