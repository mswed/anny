print("=== ANNY LOADING ===")  # add this at the very top

from rv.rvtypes import *
from rv.commands import *
from rv.extra_commands import *

from inspector import Inspector


class AnnyMode(MinorMode):
    def __init__(self) -> None:
        MinorMode.__init__(self)
        self.inspector = Inspector()

        self.init(
            "py-anny-mode",
            [
                ("key-down-->", self.show_ui, "speed up fps"),
                ("key-down--<", self.slower, "slow down fps"),
            ],
            None,
            [
                (
                    "Anny",
                    [
                        ("Show UI", self.show_ui, "=", None),
                        ("Decrease FPS", self.slower, "-", None),
                    ],
                )
            ],
        )

    def show_ui(self, event):
        self.inspector.show()

    def slower(self, event):
        setFPS(fps() * 1.0 / 1.5)
        displayFeedback(f"{fps()}fps", 2.0)


def createMode():
    return AnnyMode()
