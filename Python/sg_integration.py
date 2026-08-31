from importlib.util import find_spec
import time
import logging
from utils import Note, SGResult

try:
    from tank_vendor.shotgun_api3 import ShotgunError
except ImportError:
    ShotgunError = Exception

log = logging.getLogger(__name__)


class ShotGrid:
    """ShotGrid connection class"""

    def __init__(self) -> None:
        self.engine = None
        self.sg = None
        self.users = []
        self.groups = []
        self.tags = []
        self._has_sgtk = None

    @property
    def user(self) -> dict:
        """Get the current shotgrid user if we can find one

        Returns
        -------
        dict
            The user info or an empty dict

        """
        if self.engine:
            return self.engine.context.user
        return {}

    def has_sgtk(self) -> bool:
        """Checks to see if we have sgtk in our path

        Returns
        -------
        bool
            True if we have SGTK else False
        """

        # Cache our SGTK state
        if self._has_sgtk is None:
            self._has_sgtk = find_spec("sgtk") is not None
            if not self._has_sgtk:
                log.info(
                    "SGTK module not found. Make sure you've enabled the shotgrid mode under packages"
                )
        return self._has_sgtk

    def is_initialized(self) -> bool:
        """Check to see if we have a ShotGrid connection

        Returns
        -------
        bool
            True if we successfully initialized the connection, else False

        """
        return self.engine is not None and self.sg is not None

    def initialize(self):
        """Initialize a ShotGrid connection"""

        if self.is_initialized():
            return
        try:
            import sgtk

            self.engine = sgtk.platform.current_engine()
            if self.engine is None:
                # We did not get an engine, Anny will try again later
                return

            self.sg = self.engine.shotgun
            self.refresh_cached_data()
        except Exception as e:
            log.error(str(e))
            return

    def refresh_cached_data(self):
        """Fetch fresh users/groups/tags data from shotgrid"""

        users = self.get_active_users()
        if users["ok"]:
            self.users = users["data"]
        groups = self.get_groups()
        if groups["ok"]:
            self.groups = groups["data"]
        tags = self.get_tags()
        if tags["ok"]:
            self.tags = tags["data"]

    def get_active_users(self) -> SGResult:
        """Get a list of all active ShotGrid users

        Returns
        -------
        SGResult
            ok: True if we got the users, else False
            message: empty if we got the users, else error message
            data: list of active users if any were found, else empty list
        """

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
        """Get a list of all ShotGrid groups

        Returns
        -------
        SGResult
            ok: True if we got the groups, else False
            message: empty if we got the groups, else error message
            data: list of groups if any were found, else empty list
        """
        if self.sg is None:
            return {"ok": False, "message": "No ShotGrid connection found", "data": []}

        try:
            groups = self.sg.find("Group", [], ["code"])
        except ShotgunError as e:
            return {"ok": False, "message": str(e), "data": []}

        return {"ok": True, "message": "", "data": groups}

    def get_tags(self) -> SGResult:
        """Get a list of all ShotGrid tags

        Returns
        -------
        SGResult
            ok: True if we got the tags, else False
            message: empty if we got the tags, else error message
            data: list of tags if any were found, else empty list
        """
        if self.sg is None:
            return {"ok": False, "message": "No ShotGrid connection found", "data": []}

        try:
            tags = self.sg.find("Tag", [], ["name"])
        except ShotgunError as e:
            return {"ok": False, "message": str(e), "data": []}

        return {"ok": True, "message": "", "data": tags}

    def get_active_status_list(self, entity_type: str, project_id: int) -> SGResult:
        """Get a list of active status lists per entity, per project

        Parameters
        ----------
        entity_type : str
            The type of entity the status is set on
        project_id : int
            The project we are working on

        Returns
        -------
        SGResult
            ok: True if we got status values, else False
            message: empty if we got status values, else error message
            data: list of status values if any were found, else empty list

        """
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
                active_values.pop(v, None)

            # Convert the dict to a list so we maintain our standard SG Result dict
            active_values = sorted(active_values.items(), key=lambda s: s[1])

            return {"ok": True, "message": "", "data": active_values}

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

            valid_values = (
                field.get("properties", {}).get("valid_values", {}).get("value", [])
            )
            return {"ok": True, "message": "", "data": valid_values}

        except ShotgunError as e:
            return {"ok": False, "message": str(e), "data": []}

    def set_version_status(self, version_id: int, status: str) -> SGResult:
        """Set the current version status

        Parameters
        ----------
        version_id : int
            The version id to set the status on
        status : str
            The status code to set

        Returns
        -------
        SGResult
            ok: True if the status was set, else False
            message: empty if we set the status, else error message
            data: version object with updated status if we updated the version, else empty list

        """
        if self.sg is None:
            return {"ok": False, "message": "No ShotGrid connection found", "data": []}

        try:
            res = self.sg.update("Version", version_id, {"sg_status_list": status})
            return {"ok": True, "message": "", "data": [res]}
        except ShotgunError as e:
            return {"ok": False, "message": str(e), "data": []}

    def create_note(self, note: Note) -> SGResult:
        """Create a note in ShotGrid

        Parameters
        ----------
        note : Note
            The note fields and their values

        Returns
        -------
        SGResult
            ok: True if the note was created, else False
            message: empty if created the note, else error message
            data: note object if we created the note, else empty list
        """

        if self.sg is None:
            return {"ok": False, "message": "No ShotGrid connection found", "data": []}

        try:
            res = self.sg.create("Note", note)
            return {"ok": True, "message": "", "data": [res]}
        except ShotgunError as e:
            return {"ok": False, "message": str(e), "data": []}

    def upload_annotation(self, note_id: int, path: str) -> SGResult:
        """Upload an annotated frame to ShotGrid

        Parameters
        ----------
        note_id : int
            The note to put the annotation against
        path : str
            The path to the annotated frame on disk

        Returns
        -------
        SGResult
            ok: True if the annotation was created, else False
            message: empty if created the annotation, else error message
            data: note object if we created the annotation, else empty list

        """
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
            except (ShotgunError, OSError) as e:
                errors.append(str(e))
                if attempt < 3:
                    time.sleep(2**attempt)

        return {"ok": False, "message": errors[-1], "data": []}
