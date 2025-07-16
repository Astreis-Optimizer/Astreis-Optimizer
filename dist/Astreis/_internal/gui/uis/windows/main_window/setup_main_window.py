from PySide6 import QtCore, QtGui, QtWidgets
from gui.widgets.py_table_widget.py_table_widget import PyTableWidget
from .functions_main_window import *
import sys
import os
from gui.core.json_settings import Settings
from gui.core.json_themes import Themes
from gui.widgets import *
from .ui_main import UI_MainWindow
import psutil
import platform
import cpuinfo
import wmi
from .AstreisFunc import AstreisFunc
from gui.widgets.py_message_box import show_info_message

class _ToolTip(QWidget):
    style_tooltip = """ 
    QLabel {{		
        background-color: {_dark_one};	
        color: {_text_foreground};
        padding-left: 10px;
        padding-right: 10px;
        border-radius: 17px;
        border: 0px solid transparent;
        font: 800 9pt "Segoe UI";
    }}
    """

    def __init__(self, parent, tooltip, dark_one, text_foreground):
        style = self.style_tooltip.format(_dark_one=dark_one, _text_foreground=text_foreground)
        self.setObjectName("label_tooltip")
        self.setStyleSheet(style)
        self.setMinimumHeight(34)
        self.setParent(parent)
        self.setText(tooltip)
        self.adjustSize()
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)

class PyToggle(QCheckBox):
    def __init__(
            self,
            width=50,
            bg_color="#777",
            circle_color="#DDD",
            active_color="#00BCFF",
            animation_curve=QEasingCurve.OutBounce
    ):
        QCheckBox.__init__(self)
        self.setFixedSize(width, 28)
        self.setCursor(Qt.PointingHandCursor)
        self._bg_color = bg_color
        self._circle_color = circle_color
        self._active_color = active_color
        self._position = 3
        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setEasingCurve(animation_curve)
        self.animation.setDuration(500)
        self.stateChanged.connect(self.setup_animation)

    @Property(float)
    def position(self):
        return self._position

    @position.setter
    def position(self, pos):
        self._position = pos
        self.update()

    def setup_animation(self, value):
        self.animation.stop()
        if value:
            self.animation.setEndValue(self.width() - 26)
        else:
            self.animation.setEndValue(4)
        self.animation.start()

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setFont(QFont("Segoe UI", 9))
        p.setPen(Qt.NoPen)
        rect = QRect(0, 0, self.width(), self.height())
        if not self.isChecked():
            p.setBrush(QColor(self._bg_color))
            p.drawRoundedRect(0, 0, rect.width(), 28, 14, 14)
            p.setBrush(QColor(self._circle_color))
            p.drawEllipse(self._position, 3, 22, 22)
        else:
            p.setBrush(QColor(self._active_color))
            p.drawRoundedRect(0, 0, rect.width(), 28, 14, 14)
            p.setBrush(QColor(self._circle_color))
            p.drawEllipse(self._position, 3, 22, 22)
        p.end()

class SetupMainWindow:
    add_left_menus = [
        {
            "btn_icon": "icon_settings.svg",
            "btn_id": "btn_settings",
            "btn_text": "Settings",
            "btn_tooltip": "Open settings",
            "show_top": False,
            "is_active": False
        },
        {
            "btn_icon": "icon_info.svg",
            "btn_id": "btn_info",
            "btn_text": "Information",
            "btn_tooltip": "Open informations",
            "show_top": False,
            "is_active": False
        },
        {
            "btn_icon": "icon_home.svg",
            "btn_id": "btn_home",
            "btn_text": "Home",
            "btn_tooltip": "Home page",
            "show_top": True,
            "is_active": True
        },
        {
            "btn_icon": "icon_chat.svg",
            "btn_id": "btn_ai",
            "btn_text": "AI Chatbot",
            "btn_tooltip": "AI Chatbot page",
            "show_top": True,
            "is_active": False
        },
        {
            "btn_icon": "icon_power.svg",
            "btn_id": "btn_power",
            "btn_text": "Optimize PC",
            "btn_tooltip": "Open Optimizations",
            "show_top": True,
            "is_active": False
        }
    ]

    add_title_bar_menus = []

    def setup_btns(self):
        if self.ui.title_bar.sender() is not None:
            return self.ui.title_bar.sender()
        elif self.ui.left_menu.sender() is not None:
            return self.ui.left_menu.sender()
        elif self.ui.left_column.sender() is not None:
            return self.ui.left_column.sender()

    def create_tab_header(self, icon_path, title, close_callback=None):
        themes = self.themes["app_color"]
        settings = self.settings["font"]
        frame = QFrame()
        frame.setMinimumHeight(40)
        frame.setMaximumHeight(40)
        frame.setStyleSheet(f"background-color: {themes['bg_two']}; border-radius: 10px;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(5)
        icon_label = QLabel()
        icon_label.setMinimumSize(24, 24)
        icon_label.setMaximumSize(24, 24)
        icon_label.setPixmap(QtGui.QPixmap(icon_path).scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(icon_label)
        layout.addSpacing(5)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {themes['text_title']}; font: {settings['title_size']}pt '{settings['family']}'; background: none;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label, 1)
        close_btn = QPushButton()
        close_btn.setMinimumSize(24, 24)
        close_btn.setMaximumSize(24, 24)
        close_btn.setStyleSheet("QPushButton {background: transparent; border: none;} QPushButton:hover {background-color: #3c4454; border-radius: 5px;}")
        close_btn.setIcon(QtGui.QIcon(Functions.set_svg_icon("icon_close.svg")))
        close_btn.setIconSize(QtCore.QSize(16, 16))
        close_btn.setToolTip("Unlock Premium Features!")
        def show_subscription_box():
            show_info_message(
                frame,
                "Premium Features",
                "<b>Unlock Premium Features!</b><br><br>"
                "Get access to advanced optimization tools and exclusive features with our premium subscription."
            )
        close_btn.clicked.connect(show_subscription_box)
        layout.addWidget(close_btn)
        return frame

    def create_pack_frame(self, option, themes):
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {themes['app_color']['dark_three']}; border-radius: 10px;")
        frame.setMinimumHeight(100)
        pack_layout = QHBoxLayout(frame)
        pack_layout.setContentsMargins(10, 5, 10, 5)
        icon_label = QLabel()
        icon_label.setMinimumSize(32, 32)
        icon_label.setPixmap(QtGui.QPixmap(Functions.set_svg_icon(option["icon"])).scaled(32, 32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        pack_layout.addWidget(icon_label)
        text_layout = QVBoxLayout()
        title_label = QLabel(option["title"])
        title_label.setStyleSheet(f"color: {themes['app_color']['text_foreground']}; font: bold 12pt 'Segoe UI';")
        title_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        text_layout.addWidget(title_label)
        desc_label = QLabel(option["desc"])
        desc_label.setStyleSheet(f"color: {themes['app_color']['text_description']}; font: 10pt 'Segoe UI';")
        desc_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)
        pack_layout.addLayout(text_layout)
        pack_layout.addStretch()
        pack_button = QPushButton("Optimize")
        pack_button.setMinimumSize(100, 40)
        pack_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {themes['app_color']['context_color']};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font: bold 12pt 'Segoe UI';
            }}
            QPushButton:hover {{
                background-color: {themes['app_color']['context_hover']};
                color: #FFFFFF;
            }}
            QPushButton:pressed {{
                background-color: {themes['app_color']['context_pressed']};
                color: #FFFFFF;
            }}
        """)
        if "command" in option and callable(option["command"]):
            pack_button.clicked.connect(option["command"])
        else:
            pack_button.clicked.connect(lambda: self.optimize_selected())
        pack_layout.addWidget(pack_button)
        return frame

    def setup_gui(self):
        settings = Settings()
        self.settings = settings.items
        themes = Themes()
        self.themes = themes.items
        self.setWindowTitle("Astreis - The All In One PC Optimizer")
        if self.settings["custom_title_bar"]:
            self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.ui.title_bar.setStyleSheet(
                f"font: bold {self.settings['font']['title_size'] + 8}pt '{self.settings['font']['family']}'; color: {self.themes['app_color']['text_title']};"
            )
            self.ui.title_bar.set_title("Astreis - All In One PC Optimizer")
        else:
            self.ui.title_bar.set_title("")
        if self.settings["custom_title_bar"]:
            self.left_grip = PyGrips(self, "left", self.hide_grips)
            self.right_grip = PyGrips(self, "right", self.hide_grips)
            self.top_grip = PyGrips(self, "top", self.hide_grips)
            self.bottom_grip = PyGrips(self, "bottom", self.hide_grips)
            self.top_left_grip = PyGrips(self, "top_left", self.hide_grips)
            self.top_right_grip = PyGrips(self, "top_right", self.hide_grips)
            self.bottom_left_grip = PyGrips(self, "bottom_left", self.hide_grips)
            self.bottom_right_grip = PyGrips(self, "bottom_right", self.hide_grips)
        self.ui.left_menu.add_menus(SetupMainWindow.add_left_menus)
        self.ui.left_menu.clicked.connect(self.btn_clicked)
        self.ui.left_menu.released.connect(self.btn_released)
        self.ui.title_bar.add_menus(SetupMainWindow.add_title_bar_menus)
        self.ui.title_bar.clicked.connect(self.btn_clicked)
        self.ui.title_bar.released.connect(self.btn_released)
        self.ui.left_column.clicked.connect(self.btn_clicked)
        self.ui.left_column.released.connect(self.btn_released)
        MainFunctions.set_page(self, self.ui.load_pages.page_1)
        MainFunctions.set_left_column_menu(
            self,
            menu=self.ui.left_column.menus.menu_1,
            title="Astreis Optimizer",
            icon_path=Functions.set_svg_icon("icon_settings.svg")
        )
        self.ui.left_column.menus.menu_1.layout().setAlignment(QtCore.Qt.AlignTop)
        self.ui.left_column.menus.menu_2.layout().setAlignment(QtCore.Qt.AlignTop)
        right_header = self.create_tab_header(
            Functions.set_svg_icon("icon_info.svg"),
            "Advertisements",
            self.close_right_column if hasattr(self, 'close_right_column') else None
        )
        self.ui.right_column.main_layout.insertWidget(0, right_header)
        page_1_layout = self.ui.load_pages.page_1.layout()
        self.ui.load_pages.homeTitle.setStyleSheet(
            f"font: bold {self.settings['font']['title_size'] + 14}pt '{self.settings['font']['family']}'; color: {self.themes['app_color']['text_title']}; padding-top: 5px;"
        )
        self.ui.load_pages.aiTitle.setStyleSheet(
            f"font: bold {self.settings['font']['text_size']}pt '{self.settings['font']['family']}'; color: {self.themes['app_color']['text_title']}; padding-top: 5px;"
        )
        spacer = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding)
        page_1_layout.addItem(spacer)
        info_frame = QFrame()
        info_frame.setMinimumSize(600, 250)
        info_frame.setStyleSheet(
            "background-color: #2A2E37; border: 2px solid #0078D4; border-radius: 10px; padding: 20px;")
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_frame.setFrameShadow(QFrame.Raised)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 5)
        shadow.setColor(QtGui.QColor(0, 0, 0, 100))
        info_frame.setGraphicsEffect(shadow)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(15)
        info_layout.setContentsMargins(20, 20, 20, 20)
        cpu_info = cpuinfo.get_cpu_info()
        processor_label = QLabel(f"Processor: {cpu_info.get('brand_raw', 'Unknown')}")
        processor_label.setStyleSheet(
            f"font: {self.settings['font']['text_size']}pt '{self.settings['font']['family']}'; color: #FFFFFF; padding: 5px;")
        info_layout.addWidget(processor_label)
        ram = psutil.virtual_memory()
        ram_label = QLabel(f"RAM: {ram.total // (1024 ** 3)} GB")
        ram_label.setStyleSheet(
            f"font: {self.settings['font']['text_size']}pt '{self.settings['font']['family']}'; color: #FFFFFF; padding: 5px;")
        info_layout.addWidget(ram_label)
        total_storage = 0
        primary_drive = None
        primary_mountpoint = None
        for partition in psutil.disk_partitions():
            try:
                disk = psutil.disk_usage(partition.mountpoint)
                total_storage += disk.total
                if platform.system() == "Windows":
                    app_drive = os.path.splitdrive(sys.executable)[0]
                    if partition.mountpoint.startswith(app_drive):
                        primary_drive = disk
                        primary_mountpoint = partition.mountpoint
                else:
                    if partition.mountpoint == '/':
                        primary_drive = disk
                        primary_mountpoint = partition.mountpoint
            except:
                continue
        storage_label = QLabel(
            f"Storage: {total_storage // (1024 ** 3)} GB (Free on {primary_mountpoint if primary_mountpoint else '/'} : {primary_drive.free // (1024 ** 3) if primary_drive else 0} GB)"
        )
        storage_label.setStyleSheet(
            f"font: {self.settings['font']['text_size']}pt '{self.settings['font']['family']}'; color: #FFFFFF; padding: 5px;")
        info_layout.addWidget(storage_label)
        try:
            w = wmi.WMI()
            gpu = w.Win32_VideoController()[0]
            graphics_label = QLabel(f"Graphics Card: {gpu.Name}")
            graphics_label.setStyleSheet(
                f"font: {self.settings['font']['text_size']}pt '{self.settings['font']['family']}'; color: #FFFFFF; padding: 5px;")
            info_layout.addWidget(graphics_label)
            gpu_memory_label = QLabel(f"Graphics Memory: {gpu.AdapterRAM // (1024 ** 3)} GB")
            gpu_memory_label.setStyleSheet(
                f"font: {self.settings['font']['text_size']}pt '{self.settings['font']['family']}'; color: #FFFFFF; padding: 5px;")
            info_layout.addWidget(gpu_memory_label)
        except:
            graphics_label = QLabel("Graphics Card: Not Available")
            graphics_label.setStyleSheet(
                f"font: {self.settings['font']['text_size']}pt '{self.settings['font']['family']}'; color: #FFFFFF; padding: 5px;")
            info_layout.addWidget(graphics_label)
            gpu_memory_label = QLabel("Graphics Memory: Not Available")
            gpu_memory_label.setStyleSheet(
                f"font: {self.settings['font']['text_size']}pt '{self.settings['font']['family']}'; color: #FFFFFF; padding: 5px;")
            info_layout.addWidget(gpu_memory_label)
        page_1_layout.addWidget(info_frame, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        page_2_layout = self.ui.load_pages.page_2.layout()
        ai_title_label = QLabel("Astreis Chatbot")
        ai_title_label.setStyleSheet(
            f"font: bold {self.settings['font']['title_size'] + 14}pt '{self.settings['font']['family']}'; color: {self.themes['app_color']['text_title']}; padding-top: 5px;"
        )
        page_2_layout.addWidget(ai_title_label, alignment=QtCore.Qt.AlignCenter)
        self.ui.load_pages.aiTitle.setStyleSheet(
            f"font: bold {self.settings['font']['text_size']}pt '{self.settings['font']['family']}'; color: {self.themes['app_color']['text_title']}; padding-top: 5px;"
        )
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_area.setWidget(scroll_content)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.themes['app_color']['dark_one']};
                border: 2px solid {self.themes['app_color']['context_color']};
                border-radius: 12px;
                padding: 15px;
            }}
            QScrollArea QWidget {{
                background-color: {self.themes['app_color']['dark_two']};
                color: {self.themes['app_color']['text_foreground']};
            }}
            QScrollBar:vertical {{
                background: {self.themes['app_color']['dark_one']};
                width: 12px;
                margin: 2px 0 2px 0;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.themes['app_color']['context_color']};
                min-height: 40px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.themes['app_color']['context_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
                border: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 5)
        shadow.setColor(QtGui.QColor(86, 138, 242, 180))
        self.scroll_area.setGraphicsEffect(shadow)
        self.scroll_area.setMinimumHeight(400)
        self.scroll_area.setMaximumHeight(600)
        page_2_layout.addWidget(self.scroll_area, stretch=1)
        self.input_frame = QFrame()
        self.input_frame.setMinimumSize(0, 60)
        self.input_frame.setStyleSheet(f"background-color: {self.themes['app_color']['dark_three']}; border-radius: 10px;")
        input_layout = QHBoxLayout(self.input_frame)
        input_layout.setContentsMargins(10, 5, 10, 5)
        self.input_field = QLineEdit()
        self.input_field.setMinimumHeight(40)
        self.input_field.setStyleSheet(
            f"QLineEdit {{ background-color: {self.themes['app_color']['dark_one']}; color: {self.themes['app_color']['text_foreground']}; border-radius: 8px; padding: 5px; font: 12pt 'Segoe UI'; }}"
        )
        self.input_field.setPlaceholderText("Ask Astreis a question...")
        input_layout.addWidget(self.input_field)
        self.send_button = QPushButton()
        self.send_button.setMinimumSize(40, 40)
        self.send_button.setStyleSheet(
            f"QPushButton {{ background-color: {self.themes['app_color']['context_color']}; border-radius: 8px; }} QPushButton:hover {{ background-color: {self.themes['app_color']['context_hover']}; }}")
        self.send_button.setIcon(QtGui.QIcon(Functions.set_svg_icon("icon_send.svg")))
        self.input_field.returnPressed.connect(
            lambda: AstreisFunc.send_message(self.input_field, self.scroll_layout, self.themes))
        self.send_button.clicked.connect(
            lambda: AstreisFunc.send_message(self.input_field, self.scroll_layout, self.themes))
        input_layout.addWidget(self.send_button)
        self.clear_chat_button = QPushButton()
        self.clear_chat_button.setMinimumSize(40, 40)
        self.clear_chat_button.setStyleSheet(
            f"QPushButton {{ background-color: {self.themes['app_color']['context_color']}; border-radius: 8px; }} QPushButton:hover {{ background-color: {self.themes['app_color']['context_hover']}; }}")
        self.clear_chat_button.setIcon(QtGui.QIcon(Functions.set_svg_icon("icon_close.svg")))
        self.clear_chat_button.setToolTip("Clear Chat History")
        def clear_chat_ui():
            AstreisFunc.clear_history()
            while self.scroll_layout.count():
                child = self.scroll_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        self.clear_chat_button.clicked.connect(clear_chat_ui)
        input_layout.addWidget(self.clear_chat_button)
        page_2_layout.addWidget(self.input_frame, alignment=QtCore.Qt.AlignBottom)
        page_3_layout = self.ui.load_pages.page_3.layout()
        title_label = QLabel("Optimize PC")
        title_label.setStyleSheet(
            f"font: bold {self.settings['font']['title_size'] + 14}pt '{self.settings['font']['family']}'; color: {self.themes['app_color']['text_title']}; padding-top: 5px;"
        )
        page_3_layout.addWidget(title_label, alignment=QtCore.Qt.AlignCenter)
        packs_scroll_area = QScrollArea()
        packs_scroll_area.setWidgetResizable(True)
        packs_scroll_content = QWidget()
        packs_scroll_layout = QVBoxLayout(packs_scroll_content)
        packs_scroll_layout.setContentsMargins(15, 15, 15, 15)
        packs_scroll_layout.setSpacing(10)
        packs_scroll_area.setWidget(packs_scroll_content)
        packs_scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.themes['app_color']['dark_one']};
                border: 2px solid {self.themes['app_color']['context_color']};
                border-radius: 12px;
                padding: 15px;
            }}
            QScrollArea QWidget {{
                background-color: {self.themes['app_color']['dark_two']};
                color: {self.themes['app_color']['text_foreground']};
            }}
            QScrollBar:vertical {{
                background: {self.themes['app_color']['dark_one']};
                width: 12px;
                margin: 2px 0 2px 0;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.themes['app_color']['context_color']};
                min-height: 40px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.themes['app_color']['context_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
                border: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 5)
        shadow.setColor(QtGui.QColor(86, 138, 242, 180))
        packs_scroll_area.setGraphicsEffect(shadow)
        packs_scroll_area.setMinimumHeight(300)
        pack_options = [
            {
                "title": "Optimize Gaming & PC",
                "desc": "Optimize PC for gaming performance.",
                "icon": "icon_game.svg",
                "command": AstreisFunc.optimize_gaming
            },
            {
                "title": "Quickly Boost PC",
                "desc": "Boost your PC's performance - Do Once A Week.",
                "icon": "icon_speed.svg",
                "command": AstreisFunc.run_boost_pc_pack
            },
            {
                "title": "Improve Internet",
                "desc": "Decrease Network Ping, Latency and Improve network speed.",
                "icon": "icon_network.svg",
                "command": AstreisFunc.run_reduce_ping_pack
            },
            {
                "title": "Clean Windows",
                "desc": "Clean up temporary files, logs, caches and more.",
                "icon": "icon_clean.svg",
                "command": AstreisFunc.clean_windows
            }
        ]
        for option in pack_options:
            frame = self.create_pack_frame(option, self.themes)
            packs_scroll_layout.addWidget(frame)
        page_3_layout.addWidget(packs_scroll_area, stretch=1)
        advanced_frame = QFrame()
        advanced_frame.setStyleSheet(f"background: transparent;")
        advanced_frame.setMinimumSize(0, 60)
        advanced_layout = QHBoxLayout(advanced_frame)
        advanced_layout.setContentsMargins(10, 5, 10, 5)
        advanced_layout.setAlignment(QtCore.Qt.AlignCenter)
        show_advanced_button = QPushButton("Show Advanced")
        show_advanced_button.setMinimumSize(150, 40)
        show_advanced_button.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: #FFFFFF;
                border: none;
                font: bold 14pt 'Segoe UI';
                padding: 5px;
            }}
            QPushButton:hover {{
                color: {self.themes['app_color']['context_hover']};
            }}
            QPushButton:pressed {{
                color: {self.themes['app_color']['context_pressed']};
            }}
        """)
        def slide_to_page_4():
            anim = QPropertyAnimation(self.ui.load_pages.page_4, b"geometry")
            anim.setEasingCurve(QEasingCurve.InOutQuad)
            anim.setDuration(500)
            start_rect = self.ui.load_pages.page_4.geometry()
            start_rect.moveTop(self.ui.central_widget.height())
            end_rect = self.ui.load_pages.page_4.geometry()
            end_rect.moveTop(0)
            anim.setStartValue(start_rect)
            anim.setEndValue(end_rect)
            anim.start()
            MainFunctions.set_page(self, self.ui.load_pages.page_4)
        show_advanced_button.clicked.connect(slide_to_page_4)
        advanced_layout.addWidget(show_advanced_button)
        page_3_layout.addWidget(advanced_frame, alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        page_4_layout = self.ui.load_pages.page_4.layout()
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        self.prev_button = PyIconButton(
            icon_path=Functions.set_svg_icon("icon_arrow_left.svg"),
            parent=self,
            app_parent=self.ui.central_widget,
            tooltip_text="Previous Page",
            width=40,
            height=40,
            dark_one=self.themes["app_color"]["dark_one"],
            text_foreground=self.themes["app_color"]["text_foreground"],
            context_color=self.themes["app_color"]["context_color"]
        )
        self.prev_button.clicked.connect(self.prev_frame)
        top_layout.addWidget(self.prev_button)
        self.switch_button = PyIconButton(
            icon_path=Functions.set_svg_icon("icon_arrow_right.svg"),
            parent=self,
            app_parent=self.ui.central_widget,
            tooltip_text="Next Page",
            width=40,
            height=40,
            dark_one=self.themes["app_color"]["dark_one"],
            text_foreground=self.themes["app_color"]["text_foreground"],
            context_color=self.themes["app_color"]["context_color"]
        )
        self.switch_button.clicked.connect(self.switch_frame)
        top_layout.addWidget(self.switch_button)
        self.frame_stacked_widget = QStackedWidget()
        self.optimize_pc_widget = QWidget()
        self.clean_pc_widget = QWidget()
        self.optimize_internet_widget = QWidget()
        self.frame_stacked_widget.addWidget(self.optimize_pc_widget)
        self.frame_stacked_widget.addWidget(self.clean_pc_widget)
        self.frame_stacked_widget.addWidget(self.optimize_internet_widget)
        optimize_pc_layout = QVBoxLayout(self.optimize_pc_widget)
        clean_pc_layout = QVBoxLayout(self.clean_pc_widget)
        optimize_internet_layout = QVBoxLayout(self.optimize_internet_widget)
        optimize_pc_label = QLabel("Optimize PC")
        optimize_pc_label.setStyleSheet(
            f"font: bold {self.settings['font']['title_size'] + 14}pt '{self.settings['font']['family']}'; color: {self.themes['app_color']['text_title']}; padding-top: 5px;"
        )
        optimize_pc_layout.addWidget(optimize_pc_label, alignment=QtCore.Qt.AlignCenter)
        clean_pc_label = QLabel("Clean PC")
        clean_pc_label.setStyleSheet(
            f"font: bold {self.settings['font']['title_size'] + 14}pt '{self.settings['font']['family']}'; color: {self.themes['app_color']['text_title']}; padding-top: 5px;"
        )
        clean_pc_layout.addWidget(clean_pc_label, alignment=QtCore.Qt.AlignCenter)
        optimize_internet_label = QLabel("Optimize Internet")
        optimize_internet_label.setStyleSheet(
            f"font: bold {self.settings['font']['title_size'] + 14}pt '{self.settings['font']['family']}'; color: {self.themes['app_color']['text_title']}; padding-top: 5px;"
        )
        optimize_internet_layout.addWidget(optimize_internet_label, alignment=QtCore.Qt.AlignCenter)
        self.optimize_pc_scroll_area = QScrollArea()
        self.optimize_pc_scroll_area.setWidgetResizable(True)
        optimize_pc_scroll_content = QWidget()
        self.optimize_pc_scroll_layout = QGridLayout(optimize_pc_scroll_content)
        self.optimize_pc_scroll_layout.setContentsMargins(15, 15, 15, 15)
        self.optimize_pc_scroll_layout.setSpacing(10)
        self.optimize_pc_scroll_area.setWidget(optimize_pc_scroll_content)
        self.optimize_pc_scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.themes['app_color']['dark_one']};
                border: 2px solid {self.themes['app_color']['context_color']};
                border-radius: 12px;
                padding: 15px;
            }}
            QScrollArea QWidget {{
                background-color: {self.themes['app_color']['dark_two']};
                color: {self.themes['app_color']['text_foreground']};
            }}
            QScrollBar:vertical {{
                background: {self.themes['app_color']['dark_one']};
                width: 12px;
                margin: 2px 0 2px 0;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.themes['app_color']['context_color']};
                min-height: 40px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.themes['app_color']['context_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
                border: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        optimize_shadow = QGraphicsDropShadowEffect()
        optimize_shadow.setBlurRadius(25)
        optimize_shadow.setOffset(0, 5)
        optimize_shadow.setColor(QtGui.QColor(86, 138, 242, 180))
        self.optimize_pc_scroll_area.setGraphicsEffect(optimize_shadow)
        self.optimize_pc_scroll_area.setMinimumHeight(400)
        optimize_pc_layout.addWidget(self.optimize_pc_scroll_area)
        self.clean_pc_scroll_area = QScrollArea()
        self.clean_pc_scroll_area.setWidgetResizable(True)
        clean_pc_scroll_content = QWidget()
        self.clean_pc_scroll_layout = QGridLayout(clean_pc_scroll_content)
        self.clean_pc_scroll_layout.setContentsMargins(15, 15, 15, 15)
        self.clean_pc_scroll_layout.setSpacing(10)
        self.clean_pc_scroll_area.setWidget(clean_pc_scroll_content)
        self.clean_pc_scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.themes['app_color']['dark_one']};
                border: 2px solid {self.themes['app_color']['context_color']};
                border-radius: 12px;
                padding: 15px;
            }}
            QScrollArea QWidget {{
                background-color: {self.themes['app_color']['dark_two']};
                color: {self.themes['app_color']['text_foreground']};
            }}
            QScrollBar:vertical {{
                background: {self.themes['app_color']['dark_one']};
                width: 12px;
                margin: 2px 0 2px 0;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.themes['app_color']['context_color']};
                min-height: 40px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.themes['app_color']['context_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
                border: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        clean_shadow = QGraphicsDropShadowEffect()
        clean_shadow.setBlurRadius(25)
        clean_shadow.setOffset(0, 5)
        clean_shadow.setColor(QtGui.QColor(86, 138, 242, 180))
        self.clean_pc_scroll_area.setGraphicsEffect(clean_shadow)
        self.clean_pc_scroll_area.setMinimumHeight(400)
        clean_pc_layout.addWidget(self.clean_pc_scroll_area)
        self.optimize_internet_scroll_area = QScrollArea()
        self.optimize_internet_scroll_area.setWidgetResizable(True)
        optimize_internet_scroll_content = QWidget()
        self.optimize_internet_scroll_layout = QGridLayout(optimize_internet_scroll_content)
        self.optimize_internet_scroll_layout.setContentsMargins(15, 15, 15, 15)
        self.optimize_internet_scroll_layout.setSpacing(10)
        self.optimize_internet_scroll_area.setWidget(optimize_internet_scroll_content)
        self.optimize_internet_scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.themes['app_color']['dark_one']};
                border: 2px solid {self.themes['app_color']['context_color']};
                border-radius: 12px;
                padding: 15px;
            }}
            QScrollArea QWidget {{
                background-color: {self.themes['app_color']['dark_two']};
                color: {self.themes['app_color']['text_foreground']};
            }}
            QScrollBar:vertical {{
                background: {self.themes['app_color']['dark_one']};
                width: 12px;
                margin: 2px 0 2px 0;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.themes['app_color']['context_color']};
                min-height: 40px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.themes['app_color']['context_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
                border: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        internet_shadow = QGraphicsDropShadowEffect()
        internet_shadow.setBlurRadius(25)
        internet_shadow.setOffset(0, 5)
        internet_shadow.setColor(QtGui.QColor(86, 138, 242, 180))
        self.optimize_internet_scroll_area.setGraphicsEffect(internet_shadow)
        self.optimize_internet_scroll_area.setMinimumHeight(400)
        optimize_internet_layout.addWidget(self.optimize_internet_scroll_area)
        optimize_pc_options = [
            {
                "title": "Make A Restore Point",
                "desc": "Create a restore point for the current system state",
                "warn": "Highly Recomended!",
                "desc_color": "default",
                "warn_color": "green"
            },
            {
                "title": "Optimize Power Plan",
                "desc": "Set power plan to high performance for maximum performance",
                "warn": "⚠️Heat Warning",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Adjust Appearance",
                "desc": "Disable visual effects for better performance",
                "warn": "⚠️Visual Changes",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Defragment Drives",
                "desc": "Defragment all hard drives for better performance",
                "warn": "⚠️SSD Warning - Will skip SSD drives",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Disable Startup Apps",
                "desc": "Disable non-essential apps from starting with Windows",
                "warn": "⚠️Feature Breaking - Creates registry backups",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Disable Unnecessary Services",
                "desc": "Disables a list of safe-to-disable services like Fax, Xbox services, etc.",
                "warn": "⚠️Can break some functionality",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Optimize Registry",
                "desc": "Clean and optimize the Windows registry for improved performance",
                "warn": "",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Disable Search Index",
                "desc": "Disable Search Indexing",
                "warn": "⚠️You won't be able to search web on search",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Classic Right Click Menu",
                "desc": "Return Classic Right Click Menu from Windows 10",
                "warn": "",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Optimize CPU Performance",
                "desc": "Maximize CPU scheduling and disable power management",
                "warn": "⚠️Overheating Risk",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Disable Background Apps",
                "desc": "Stop all background apps to free system resources",
                "warn": "⚠️May Break Apps",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Disable Windows Update",
                "desc": "Disable automatic updates to prevent interruptions",
                "warn": "⚠️Updates will not be installed automatically",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Disable Automatic Restart",
                "desc": "Prevent automatic restart after crashes or errors",
                "warn": "",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Disable Sleep Mode",
                "desc": "Disable sleep mode to keep the computer awake",
                "warn": "",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Disable Windows Defender",
                "desc": "Disable Windows Defender to reduce CPU and disk usage",
                "warn": "⚠️High Security Risk",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Open Desktop Utility",
                "desc": "Runs the best Desktop Utility @ChrisTitus",
                "warn": "",
                "desc_color": "default",
                "warn_color": "yellow"
            }
        ]
        clean_pc_options = [
            {
                "title": "Clear Temporary Files",
                "desc": "Remove temporary files to free up disk space",
                "warn": "Recommended Once A Week!",
                "desc_color": "default",
                "warn_color": "green"
            },
            {
                "title": "Clean Recycle Bin",
                "desc": "Cleans/Empties Recycle Bin",
                "warn": "⚠️Check Recycle Bin",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Clean Browser Cache",
                "desc": "Cleans Browser Cache and History",
                "warn": "",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Clean System Logs",
                "desc": "Remove system logs to free up space",
                "warn": "",
                "desc_color": "default",
                "warn_color": "red"
            },
            {
                "title": "Run Disk Cleanup",
                "desc": "Perform disk cleanup to optimize storage",
                "warn": "Recommended once a week",
                "desc_color": "default",
                "warn_color": "green"
            },
            {
                "title": "Run Debloat Utility",
                "desc": "Run Windows Debloat Utility @Raphire",
                "warn": "",
                "desc_color": "default",
                "warn_color": "red"
            }
        ]
        optimize_internet_options = [
            {
                "title": "Optimize DNS",
                "desc": "Switch to a faster DNS server (e.g., Google DNS)",
                "warn": "",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Flush DNS Cache",
                "desc": "Clear DNS cache for faster browsing",
                "warn": "Recommended once a Week",
                "desc_color": "default",
                "warn_color": "green"
            },
            {
                "title": "Optimize Network Adapters",
                "desc": "Tune network settings for better speed",
                "warn": "",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Enable TCP Fast Open",
                "desc": "Improve network performance by enabling TCP Fast Open",
                "warn": "",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Clear Microsoft Store Cache",
                "desc": "Clears cached files from the Microsoft Store",
                "warn": "",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Clear Event Logs",
                "desc": "Clear event logs to improve internet performance",
                "warn": "",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Disable Metered Connection",
                "desc": "Turn off metered connection limits",
                "warn": "⚠️May increase data usage",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Disable IPv6",
                "desc": "Disable IPv6 protocol for improved performance",
                "warn": "⚠️Be Cautious",
                "desc_color": "default",
                "warn_color": "yellow"
            },
            {
                "title": "Disable Firewall",
                "desc": "Disables Firewall",
                "warn": "⚠️Security Risk",
                "desc_color": "default",
                "warn_color": "yellow"
            }
        ]
        for i, option in enumerate(optimize_pc_options):
            frame = QFrame()
            frame.setStyleSheet(f"background-color: {self.themes['app_color']['dark_three']}; border-radius: 10px;")
            frame.setFixedWidth(300)
            inner_layout = QVBoxLayout(frame)
            inner_layout.setContentsMargins(10, 5, 10, 5)
            title_label = QLabel(option["title"])
            title_label.setStyleSheet(f"color: {self.themes['app_color']['text_foreground']}; font: bold 12pt 'Segoe UI';")
            inner_layout.addWidget(title_label)
            desc_color = self.themes['app_color']['text_description']
            if "desc_color" in option and option["desc_color"].lower() == "yellow":
                desc_color = self.themes['app_color']['yellow']
            desc_label = QLabel(option["desc"])
            desc_label.setStyleSheet(f"color: {desc_color}; font: 10pt 'Segoe UI';")
            desc_label.setWordWrap(True)
            inner_layout.addWidget(desc_label)
            if "warn" in option:
                warn_label = QLabel(option["warn"])
                warn_color = self.themes['app_color']['text_description']
                if option.get("warn_color", "").lower() == "yellow":
                    warn_color = self.themes['app_color']['yellow']
                elif option.get("warn_color", "").lower() == "green":
                    warn_color = self.themes['app_color']['green']
                warn_label.setStyleSheet(f"color: {warn_color}; font: 10pt 'Segoe UI';")
                warn_label.setWordWrap(True)
                inner_layout.addWidget(warn_label)
            toggle = PyToggle(
                width=50,
                bg_color=self.themes["app_color"]["dark_two"],
                circle_color="#DDD",
                active_color=self.themes["app_color"]["context_color"]
            )
            toggle_layout = QHBoxLayout()
            toggle_layout.addStretch()
            toggle_layout.addWidget(toggle)
            inner_layout.addLayout(toggle_layout)
            self.optimize_pc_scroll_layout.addWidget(frame, i // 2, i % 2)
        for i, option in enumerate(clean_pc_options):
            frame = QFrame()
            frame.setStyleSheet(f"background-color: {self.themes['app_color']['dark_three']}; border-radius: 10px;")
            frame.setFixedWidth(300)
            inner_layout = QVBoxLayout(frame)
            inner_layout.setContentsMargins(10, 5, 10, 5)
            title_label = QLabel(option["title"])
            title_label.setStyleSheet(f"color: {self.themes['app_color']['text_foreground']}; font: bold 12pt 'Segoe UI';")
            inner_layout.addWidget(title_label)
            desc_color = self.themes['app_color']['text_description']
            if "desc_color" in option and option["desc_color"].lower() == "yellow":
                desc_color = self.themes['app_color']['yellow']
            desc_label = QLabel(option["desc"])
            desc_label.setStyleSheet(f"color: {desc_color}; font: 10pt 'Segoe UI';")
            desc_label.setWordWrap(True)
            inner_layout.addWidget(desc_label)
            if "warn" in option:
                warn_label = QLabel(option["warn"])
                warn_color = self.themes['app_color']['text_description']
                if option.get("warn_color", "").lower() == "yellow":
                    warn_color = self.themes['app_color']['yellow']
                elif option.get("warn_color", "").lower() == "green":
                    warn_color = self.themes['app_color']['green']
                warn_label.setStyleSheet(f"color: {warn_color}; font: 10pt 'Segoe UI';")
                warn_label.setWordWrap(True)
                inner_layout.addWidget(warn_label)
            toggle = PyToggle(
                width=50,
                bg_color=self.themes["app_color"]["dark_two"],
                circle_color="#DDD",
                active_color=self.themes["app_color"]["context_color"]
            )
            toggle_layout = QHBoxLayout()
            toggle_layout.addStretch()
            toggle_layout.addWidget(toggle)
            inner_layout.addLayout(toggle_layout)
            self.clean_pc_scroll_layout.addWidget(frame, i // 2, i % 2)
        for i, option in enumerate(optimize_internet_options):
            frame = QFrame()
            frame.setStyleSheet(f"background-color: {self.themes['app_color']['dark_three']}; border-radius: 10px;")
            frame.setFixedWidth(300)
            inner_layout = QVBoxLayout(frame)
            inner_layout.setContentsMargins(10, 5, 10, 5)
            title_label = QLabel(option["title"])
            title_label.setStyleSheet(f"color: {self.themes['app_color']['text_foreground']}; font: bold 12pt 'Segoe UI';")
            inner_layout.addWidget(title_label)
            desc_color = self.themes['app_color']['text_description']
            if "desc_color" in option and option["desc_color"].lower() == "yellow":
                desc_color = self.themes['app_color']['yellow']
            desc_label = QLabel(option["desc"])
            desc_label.setStyleSheet(f"color: {desc_color}; font: 10pt 'Segoe UI';")
            desc_label.setWordWrap(True)
            inner_layout.addWidget(desc_label)
            if "warn" in option:
                warn_label = QLabel(option["warn"])
                warn_color = self.themes['app_color']['text_description']
                if option.get("warn_color", "").lower() == "yellow":
                    warn_color = self.themes['app_color']['yellow']
                elif option.get("warn_color", "").lower() == "green":
                    warn_color = self.themes['app_color']['green']
                warn_label.setStyleSheet(f"color: {warn_color}; font: 10pt 'Segoe UI';")
                warn_label.setWordWrap(True)
                inner_layout.addWidget(warn_label)
            toggle = PyToggle(
                width=50,
                bg_color=self.themes["app_color"]["dark_two"],
                circle_color="#DDD",
                active_color=self.themes["app_color"]["context_color"]
            )
            toggle_layout = QHBoxLayout()
            toggle_layout.addStretch()
            toggle_layout.addWidget(toggle)
            inner_layout.addLayout(toggle_layout)
            self.optimize_internet_scroll_layout.addWidget(frame, i // 2, i % 2)
        page_4_layout.addLayout(top_layout)
        page_4_layout.addWidget(self.frame_stacked_widget)
        optimize_btn = QPushButton("Optimize")
        optimize_btn.setMinimumSize(150, 50)
        optimize_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.themes["app_color"]["context_color"]};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 14pt;
                font-weight: bold;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {self.themes['app_color']['context_hover']};
                color: #FFFFFF;
            }}
            QPushButton:pressed {{
                background-color: {self.themes['app_color']['context_pressed']};
                color: #FFFFFF;
            }}
        """)
        optimize_btn.clicked.connect(lambda: self.optimize_selected())
        page_4_layout.addWidget(optimize_btn, alignment=QtCore.Qt.AlignCenter)