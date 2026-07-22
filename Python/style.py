ANNY_STYLESHEET = """
    QDialog, QWidget {
        background-color: #262220;
        color: #d8d2cc;
        font-size: 11px;
    }

    QGroupBox {
        border: 1px solid #3c3633;
        border-radius: 4px;
        margin-top: 8px;
        color: #b3aaa2;
        font-size: 11px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 8px;
        padding: 0 3px;
    }

    QToolButton {
        background-color: #383330;
        border: 1px solid #4a433f;
        border-radius: 3px;
        padding: 2px;
        color: #d8d2cc;
    }
    QToolButton:hover {
        background-color: #443e3a;
        border: 1px solid #5d544f;
    }
    QToolButton:checked {
        background-color: #e0922f;
        border: 1px solid #f0a542;
        color: #1f1b19;
    }

    QDoubleSpinBox, QSpinBox, QComboBox, QFontComboBox, QTextEdit {
        background-color: #383330;
        border: 1px solid #4a433f;
        border-radius: 3px;
        color: #ece7e2;
        padding: 1px 3px;
        selection-background-color: #e0922f;
        selection-color: #1f1b19;
    }
    QComboBox, QFontComboBox {
        padding: 1px 18px 1px 3px;
    }
    QDoubleSpinBox:hover, QSpinBox:hover,
    QComboBox:hover, QFontComboBox:hover, QTextEdit:hover {
        border: 1px solid #6b615b;
    }
    QDoubleSpinBox:focus, QSpinBox:focus,
    QComboBox:focus, QFontComboBox:focus, QTextEdit:focus {
        border: 1px solid #e0922f;
    }

    /* --- spinbox stepper buttons --- */
    QDoubleSpinBox::up-button, QSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        background-color: #46403c;
        border: none;
        border-top-right-radius: 3px;
        width: 16px;
    }
    QDoubleSpinBox::down-button, QSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        background-color: #46403c;
        border: none;
        border-bottom-right-radius: 3px;
        width: 16px;
    }
    QDoubleSpinBox::up-button:hover, QSpinBox::up-button:hover,
    QDoubleSpinBox::down-button:hover, QSpinBox::down-button:hover {
        background-color: #564e49;
    }

    /* --- spinbox arrows (the missing sub-controls) --- */
    QDoubleSpinBox::up-arrow, QSpinBox::up-arrow {
        image: url(:/icons//up-arrow.svg);
        width: 9px;
        height: 9px;
    }
    QDoubleSpinBox::down-arrow, QSpinBox::down-arrow {
        image: url(:/icons/down-arrow.svg);
        width: 9px;
        height: 9px;
    }

    /* --- combo box dropdown --- */
    QComboBox::drop-down, QFontComboBox::drop-down {
        border: none;
        width: 16px;
    }
    QComboBox QAbstractItemView, QFontComboBox QAbstractItemView {
        background-color: #383330;
        color: #d8d2cc;
        border: 1px solid #4a433f;
        selection-background-color: #e0922f;
        selection-color: #1f1b19;
        outline: none;
    }

    QLabel {
        color: #c9c2bb;
        background: transparent;
        border: none;
    }

    QPushButton {
        background-color: #383330;
        border: 1px solid #4a433f;
        border-radius: 3px;
        color: #d8d2cc;
        padding: 3px 8px;
    }
    QPushButton:hover {
        background-color: #443e3a;
        border: 1px solid #5d544f;
    }
    QPushButton:pressed {
        background-color: #2c2825;
    }

    QWidget:disabled {
        color: #6b645e;
    }

    QToolButton:disabled {
        background-color: #2c2825;
        border: 1px solid #3a3431;
        color: #6b645e;
    }
    QToolButton:checked:disabled {
        background-color: #7a5527;
        border: 1px solid #8a6230;
        color: #463a2c;
    }

    QDoubleSpinBox:disabled, QSpinBox:disabled,
    QComboBox:disabled, QFontComboBox:disabled, QTextEdit:disabled {
        background-color: #2c2825;
        border: 1px solid #3a3431;
        color: #6b645e;
    }

    QDoubleSpinBox::up-button:disabled, QSpinBox::up-button:disabled,
    QDoubleSpinBox::down-button:disabled, QSpinBox::down-button:disabled {
        background-color: #332e2b;
    }

    QPushButton:disabled {
        background-color: #2c2825;
        border: 1px solid #3a3431;
        color: #6b645e;
    }

    QLabel:disabled {
        color: #6b645e;
    }

    /* --- tabs --- */
    QTabWidget::pane {
        border: 1px solid #3c3633;
        border-radius: 4px;
        top: -1px;                        /* pull the pane up so tabs sit on its edge */
    }

    QTabBar::tab {
        background-color: #2c2825;
        color: #b3aaa2;
        border: 1px solid #3c3633;
        border-bottom: none;              /* tabs open into the content below */
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        padding: 5px 14px;
        margin-right: 2px;
    }

    QTabBar::tab:selected {
        background-color: #262220;        /* matches the pane/dialog background */
        color: #ece7e2;
        border: 1px solid #3c3633;
        border-bottom: none;
    }

    QTabBar::tab:!selected {
        margin-top: 2px;                  /* unselected tabs sit slightly recessed */
        background-color: #221e1c;
    }

    QTabBar::tab:!selected:hover {
        background-color: #332e2b;
        color: #d8d2cc;
    }
"""
