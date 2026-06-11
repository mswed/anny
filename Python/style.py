ANNY_STYLESHEET = """
    QDialog, QWidget {
        background-color: #2b2b2b;
        color: #cccccc;
        font-size: 11px;
    }
    
    QGroupBox {
        border: 1px solid #444;
        border-radius: 3px;
        margin-top: 8px;
        color: #aaaaaa;
        font-size: 11px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 8px;
        padding: 0 3px;
    }
    
    QToolButton {
        background-color: #3a3a3a;
        border: 1px solid #555;
        border-radius: 3px;
        padding: 2px;
        color: #cccccc;
    }
    QToolButton:hover {
        background-color: #484848;
        border: 1px solid #666;
    }
    QToolButton:checked {
        background-color: #4a90d9;
        border: 1px solid #357abd;
        color: white;
    }
    
    QDoubleSpinBox, QSpinBox {
        background-color: #3a3a3a;
        border: 1px solid #555;
        border-radius: 3px;
        color: #cccccc;
        padding: 1px 3px;
    }
    QDoubleSpinBox:hover, QSpinBox:hover {
        border: 1px solid #777;
    }
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
    QSpinBox::up-button, QSpinBox::down-button {
        background-color: #444;
        border: none;
        width: 14px;
    }
    QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover,
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
        background-color: #555;
    }
    
    QLabel {
        color: #cccccc;
        background: transparent;
        border: none;
    }
    
    QPushButton {
        background-color: #3a3a3a;
        border: 1px solid #555;
        border-radius: 3px;
        color: #cccccc;
        padding: 3px 8px;
    }
    QPushButton:hover {
        background-color: #484848;
        border: 1px solid #666;
    }
    QPushButton:pressed {
        background-color: #2a2a2a;
    }
"""
