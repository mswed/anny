from rv.rvtypes import *
from rv.commands import *
from rv.extra_commands import *


class AnnyMode(MinorMode):
    def __init__(self) -> None:
        MinorMode.__init__(self)

        self.init(
            "py-anny-mode",
            [
                ("key-down-->", self.faster, "speed up fps"),
                ("key-down--<", self.slower, "slow down fps"),
            ],
            None,
            [
                (
                    "Anny",
                    [
                        ("Increase FPS", self.faster, "=", None),
                        ("Decrease FPS", self.slower, "-", None),
                    ],
                )
            ],
        )

    def faster(self, event):
        setFPS(fps() * 1.5)
        displayFeedback(f"{fps()}fps", 2.0)

    def slower(self, event):
        setFPS(fps() * 1.0 / 1.5)
        displayFeedback(f"{fps()}fps", 2.0)


def createMode():
    return AnnyMode()
