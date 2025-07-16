# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================
from qt_core import *
from gui.core.json_themes import Themes

# =============================================================================
# CUSTOM MESSAGE BOX CLASS
# =============================================================================
class PyMessageBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        themes = Themes().items

        self.setStyleSheet(f"""
            QMessageBox {{
                background-color: {themes['app_color']['dark_one']};
                border: 2px solid {themes['app_color']['context_color']};
                border-radius: 10px;
            }}
            QMessageBox QLabel {{
                color: {themes['app_color']['text_foreground']};
                font-family: "Segoe UI";
                font-size: 11pt;
                padding: 10px;
            }}
            QPushButton {{
                background-color: {themes['app_color']['context_color']};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-family: "Segoe UI";
                font-weight: bold;
                font-size: 11pt;
                min-width: 100px;
                min-height: 30px;
            }}
            QPushButton:hover {{
                background-color: {themes['app_color']['context_hover']};
            }}
            QPushButton:pressed {{
                background-color: {themes['app_color']['context_pressed']};
            }}
            QPushButton:disabled {{
                background-color: #555555;
                color: #FFFFFF;
            }}
        """)

    def show(self):
        self.exec()

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================
def show_info_message(parent, title, text):
    msg_box = PyMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.show()

def show_critical_message(parent, title, text):
    msg_box = PyMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.show() 