from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from gui.core.functions import Functions

class PyTitleBar(QWidget):
    def __init__(
        self,
        parent,
        app_parent,
        logo_image,
        bg_one,
        bg_two,
        bg_three,
        bg_four,
        icon_color,
        icon_color_hover,
        icon_color_pressed,
        icon_color_active,
        context_color,
        dark_one,
        title_color,
        title_size,
        is_custom_title_bar
    ):
        super().__init__()
        self.parent = parent
        self.app_parent = app_parent
        self.logo_image = logo_image
        self.bg_one = bg_one
        self.bg_two = bg_two
        self.bg_three = bg_three
        self.bg_four = bg_four
        self.icon_color = icon_color
        self.icon_color_hover = icon_color_hover
        self.icon_color_pressed = icon_color_pressed
        self.icon_color_active = icon_color_active
        self.context_color = context_color
        self.dark_one = dark_one
        self.title_color = title_color
        self.title_size = title_size
        self.is_custom_title_bar = is_custom_title_bar
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumHeight(40)
        self.setMaximumHeight(40)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.bg_one};
                color: {self.title_color};
            }}
        """)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(0)
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap(Functions.set_svg_icon(self.logo_image)))
        self.layout.addWidget(self.logo)
        self.layout.addStretch()
        self.title = QLabel("Astreis - The All In One PC Optimizer")
        self.title.setStyleSheet(f"""
            font: bold {self.title_size}pt 'Segoe UI';
            color: {self.title_color};
        """)
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.minimize_btn = QPushButton()
        self.minimize_btn.setIcon(QIcon(Functions.set_svg_icon("icon_minimize.svg")))
        self.minimize_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.bg_one};
                border: none;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {self.bg_two};
            }}
            QPushButton:pressed {{
                background-color: {self.bg_three};
            }}
        """)
        self.minimize_btn.clicked.connect(lambda: self.parent.showMinimized())
        self.layout.addWidget(self.minimize_btn)
        self.maximize_btn = QPushButton()
        self.maximize_btn.setIcon(QIcon(Functions.set_svg_icon("icon_maximize.svg")))
        self.maximize_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.bg_one};
                border: none;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {self.bg_two};
            }}
            QPushButton:pressed {{
                background-color: {self.bg_three};
            }}
        """)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.layout.addWidget(self.maximize_btn)
        self.close_btn = QPushButton()
        self.close_btn.setIcon(QIcon(Functions.set_svg_icon("icon_close.svg")))
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.bg_one};
                border: none;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {self.bg_two};
            }}
            QPushButton:pressed {{
                background-color: {self.bg_three};
            }}
        """)
        self.close_btn.clicked.connect(lambda: self.parent.close())
        self.layout.addWidget(self.close_btn)

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized() 