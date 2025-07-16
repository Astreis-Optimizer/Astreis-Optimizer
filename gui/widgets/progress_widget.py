# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================
from gui.core.qt_core import *
from gui.core.json_settings import Settings

# =============================================================================
# PROGRESS WIDGET CLASS
# =============================================================================
class ProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.themes = self.settings.items
        
        self.setup_ui()
        
    # =============================================================================
    # UI SETUP METHODS
    # =============================================================================
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.progress_container = QWidget()
        self.progress_container.setObjectName("progress_container")
        self.progress_container.setStyleSheet(f"""
            #progress_container {{
                background-color: {self.themes['app_color']['dark_one']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        self.progress_layout = QVBoxLayout(self.progress_container)
        self.progress_layout.setContentsMargins(10, 10, 10, 10)
        self.progress_layout.setSpacing(10)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {self.themes['app_color']['dark_two']};
                border-radius: 4px;
                text-align: center;
                color: {self.themes['app_color']['text_foreground']};
            }}
            QProgressBar::chunk {{
                background-color: {self.themes['app_color']['context_color']};
                border-radius: 4px;
            }}
        """)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        self.status_label = QLabel("Preparing...")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {self.themes['app_color']['text_foreground']};
                font-size: 12px;
            }}
        """)
        
        self.progress_layout.addWidget(self.progress_bar)
        self.progress_layout.addWidget(self.status_label)
        
        self.layout.addWidget(self.progress_container)
        
    # =============================================================================
    # PROGRESS CONTROL METHODS
    # =============================================================================
    def update_progress(self, value, status_text=None):
        self.progress_bar.setValue(value)
        if status_text:
            self.status_label.setText(status_text)
            
    def show_progress(self):
        self.show()
        
    def hide_progress(self):
        self.hide()
        
    def reset(self):
        self.progress_bar.setValue(0)
        self.status_label.setText("Preparing...") 