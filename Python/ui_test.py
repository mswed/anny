from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QWidget
from flowLayout import FlowLayout
from multi_select import MultiSelect


class Window(QWidget):
    def __init__(self):
        super().__init__()

        model = [
            {
                "id": 1,
                "name": "Bob Johnson",
                "login": "bjohnson@zoop.com",
                "type": "HumanUser",
            },
            {
                "id": 2,
                "name": "Henry Boon",
                "login": "hboon@zoop.com",
                "type": "HumanUser",
            },
            {
                "id": 3,
                "name": "Elizabeth Oz",
                "login": "eoz@zoop.com",
                "type": "HumanUser",
            },
            {
                "id": 1,
                "name": "ANT_prod",
                "type": "Group",
            },
        ]

        icons = {
            "HumanUser": "/home/mswed/Documents/coding/anny/icons/user-solid-full.svg",
            "Group": "/home/mswed/Documents/coding/anny/icons/user-group-solid-full.svg",
        }

        layout = QVBoxLayout(self)
        multi = MultiSelect()
        multi.configure(
            model=model,
            record_name=self.display_name,
            record_id=self.record_id,
            record_type="type",
            icons=icons,
            placeholder="Search peopls and groups",
        )
        layout.addWidget(multi)
        btn = QPushButton("Submit")
        btn.clicked.connect(multi.selected_data)
        layout.addWidget(btn)

        self.setWindowTitle("Flow Layout")

    @staticmethod
    def display_name(data):
        if data.get("type") == "HumanUser":
            return f"{data['name']} ({data['login']})"
        else:
            return data["name"]

    @staticmethod
    def record_id(data):
        return f"{data['id']}-{data['type']}"
