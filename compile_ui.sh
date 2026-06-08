#!/bin/bash
pyside6-uic "$1" -o "ui_$(basename $1 .ui).py"
# sed -i 's/from PySide6/from PySide2/g' "ui_$(basename $1 .ui).py"
# sed -i 's/import PySide6/import PySide2/g' "ui_$(basename $1 .ui).py"
