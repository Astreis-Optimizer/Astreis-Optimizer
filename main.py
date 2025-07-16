import functools
import sys
import os
import time
import ctypes
from PySide6.QtCore import QTimer, QThread, QObject, Signal
from PySide6.QtWidgets import QMainWindow, QProgressDialog, QMessageBox, QApplication
from PySide6.QtGui import QIcon
from gui.core.json_settings import Settings
from gui.core.json_themes import Themes
from gui.core.functions import Functions
from gui.uis.windows.main_window import *
from gui.uis.windows.main_window.functions_main_window import *
from gui.widgets import *
from gui.uis.windows.main_window.AstreisFunc import AstreisFunc
from gui.widgets.py_message_box import PyMessageBox, show_info_message, show_critical_message
import socket

print("--- Script Starting ---")

def check_single_instance(port=65432):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        s.listen(1)
        return s
    except socket.error:
        return None

def run_as_admin():
    if "--no-admin-check" in sys.argv:
        print("--- Skipping admin check due to --no-admin-check flag ---")
        return
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("--- Not running as admin, relaunching with elevated privileges ---")
        params = ' '.join([f'"{arg}"' for arg in sys.argv if arg != "--no-admin-check"] + ["--no-admin-check"])
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            print("--- Relaunched as admin, exiting current process ---")
            os._exit(0)
        except Exception as e:
            print(f"--- Failed to relaunch as admin: {e} ---")
            show_critical_message(None, "Admin Required",
                                  "This application requires Administrator privileges. Please run as Administrator and try again.")
            os._exit(1)
    else:
        print("--- Already running as admin ---")

os.environ["QT_FONT_DPI"] = "96"

option_functions = {
    "Make A Restore Point": AstreisFunc.make_restore_point,
    "Optimize Power Plan": AstreisFunc.optimize_astreis_power_plan,
    "Adjust Appearance": AstreisFunc.optimize_appearance,
    "Defragment Drives": AstreisFunc.optimize_defrag,
    "Disable Startup Apps": AstreisFunc.optimize_startup_apps,
    "Disable Unnecessary Services": AstreisFunc.optimize_services,
    "Optimize Registry": AstreisFunc.optimize_registry,
    "Classic Right Click Menu": AstreisFunc.enable_classic_right_click,
    "Disable Search Index": AstreisFunc.disable_search_index,
    "Open Desktop Utility": AstreisFunc.run_windows_utility,
    "Optimize CPU Performance": AstreisFunc.optimize_cpu_performance,
    "Disable Automatic Restart": AstreisFunc.disable_automatic_restart,
    "Disable Sleep Mode": AstreisFunc.disable_sleep_mode,
    "Disable Windows Defender": AstreisFunc.disable_windows_defender,
    "Disable Background Apps": AstreisFunc.disable_background_apps,
    "Disable Windows Update": AstreisFunc.disable_windows_update,

    "Clear Temporary Files": AstreisFunc.clean_temporary_files,
    "Clean Recycle Bin": AstreisFunc.empty_recycle_bin,
    "Clean Browser Cache": AstreisFunc.clean_all_browser_caches,
    "Clean System Logs": AstreisFunc.clean_all_logs,
    "Run Disk Cleanup": AstreisFunc.run_disk_cleanup,
    "Run Debloat Utility": AstreisFunc.run_debloat_utility,

    "Optimize DNS": AstreisFunc.optimize_dns,
    "Disable Metered Connection": AstreisFunc.disable_metered_connection,
    "Flush DNS Cache": AstreisFunc.flush_dns_cache,
    "Optimize Network Adapters": AstreisFunc.optimize_network_adapters,
    "Enable TCP Fast Open": AstreisFunc.enable_tcp_fast_open,
    "Disable IPv6": AstreisFunc.disable_ipv6,
    "Clear Microsoft Store Cache": AstreisFunc.clear_ms_store_cache,
    "Clear Event Logs": AstreisFunc.clear_event_logs,
    "Disable Firewall": AstreisFunc.disable_firewall,
    "Optimize Gaming": AstreisFunc.optimize_gaming,
    "Boost PC Pack": AstreisFunc.run_boost_pc_pack,
    "Reduce Ping Pack": AstreisFunc.run_reduce_ping_pack,
    "Clean Windows": AstreisFunc.clean_windows
}

class MainWindow(QMainWindow, SetupMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = UI_MainWindow()
        self.ui.setup_ui(self)
        settings = Settings()
        self.settings = settings.items
        self.hide_grips = True
        self.current_left_tab = None
        self.setup_gui()
        self.ui.left_column.btn_close.clicked.connect(self.close_left_column)
        self.show()

    def close_left_column(self):
        if MainFunctions.left_column_is_visible(self):
            MainFunctions.toggle_left_column(self)
            self.ui.left_menu.deselect_all_tab()
            self.current_left_tab = None

    def btn_clicked(self):
        btn = self.setup_btns()
        btn_name = btn.objectName()
        if btn_name != "btn_settings" and btn_name != "btn_info":
            self.ui.left_menu.deselect_all_tab()
        if btn_name == "btn_home":
            self.ui.left_menu.select_only_one(btn_name)
            MainFunctions.set_page(self, self.ui.load_pages.page_1)
        elif btn_name == "btn_ai":
            self.ui.left_menu.select_only_one(btn_name)
            MainFunctions.set_page(self, self.ui.load_pages.page_2)
        elif btn_name == "btn_power":
            self.ui.left_menu.select_only_one(btn_name)
            MainFunctions.set_page(self, self.ui.load_pages.page_3)
        elif btn_name in ["btn_info", "btn_settings"]:
            is_visible = MainFunctions.left_column_is_visible(self)
            if self.current_left_tab == btn_name and is_visible:
                self.ui.left_menu.deselect_all_tab()
                MainFunctions.toggle_left_column(self)
                self.current_left_tab = None
            else:
                if not is_visible:
                    MainFunctions.toggle_left_column(self)
                self.ui.left_menu.select_only_one_tab(btn_name)
                self.current_left_tab = btn_name
                if btn_name == "btn_info":
                    MainFunctions.set_left_column_menu(
                        self,
                        menu=self.ui.left_column.menus.menu_2,
                        title="Info tab",
                        icon_path=Functions.set_svg_icon("icon_info.svg")
                    )
                elif btn_name == "btn_settings":
                    MainFunctions.set_left_column_menu(
                        self,
                        menu=self.ui.left_column.menus.menu_1,
                        title="Astreis Optimizer",
                        icon_path=Functions.set_svg_icon("icon_settings.svg")
                    )
        print(f"Button {btn_name}, clicked!")

    def btn_released(self):
        btn = self.setup_btns()
        print(f"Button {btn.objectName()}, released!")

    def switch_frame(self):
        current_index = self.frame_stacked_widget.currentIndex()
        if current_index < self.frame_stacked_widget.count() - 1:
            self.frame_stacked_widget.setCurrentIndex(current_index + 1)

    def prev_frame(self):
        current_index = self.frame_stacked_widget.currentIndex()
        if current_index > 0:
            self.frame_stacked_widget.setCurrentIndex(current_index - 1)

    def run_optimization_pack(self, pack_title, pack_function):
        print(f"--- running optimization called for {pack_title} ---")
        try:
            themes = Themes().items
            self.progress_dialog = QProgressDialog(f"Running {pack_title}...", "Cancel", 0, 100, self)
            print("--- Progress dialog created ---")
            self.progress_dialog.setWindowTitle("Optimization Progress")
            self.progress_dialog.setMinimumSize(500, 150)
            self.progress_dialog.setStyleSheet(f"""
                QProgressDialog {{
                    background-color: {themes['app_color']['dark_one']};
                    color: {themes['app_color']['text_foreground']};
                    border: 2px solid {themes['app_color']['context_color']};
                    border-radius: 10px;
                    font-family: 'Segoe UI';
                    font-size: 12pt;
                }}
                QProgressBar {{
                    background-color: {themes['app_color']['dark_two']};
                    color: {themes['app_color']['text_foreground']};
                    border: 2px solid {themes['app_color']['context_color']};
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                    font-size: 11pt;
                    min-height: 25px;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {themes['app_color']['context_color']},
                        stop:1 {themes['app_color']['context_hover']});
                    border-radius: 6px;
                    margin: 2px;
                }}
                QPushButton {{
                    background-color: {themes['app_color']['context_color']};
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 11pt;
                    min-width: 80px;
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
                QLabel {{
                    color: {themes['app_color']['text_foreground']};
                    font-size: 11pt;
                    font-weight: bold;
                    padding: 5px;
                }}
            """)
            self.progress_dialog.setModal(True)
            self.progress_dialog.setAutoClose(False)
            self.progress_dialog.setAutoReset(False)
            self.progress_dialog.canceled.connect(self.on_pack_cancel)
            self.pack_optimization_results = []
            self.progress_dialog.forceShow()
            QApplication.processEvents()
            print("--- Progress dialog shown ---")
            self.pack_optimization_thread = QThread(self)
            self.pack_optimization_worker = OptimizationWorker([(pack_title, "Optimization Pack")], {pack_title: pack_function})
            self.pack_optimization_worker.moveToThread(self.pack_optimization_thread)
            self.pack_optimization_worker.progress_update.connect(self.on_pack_progress_update)
            self.pack_optimization_worker.result_ready.connect(self.on_pack_result_ready)
            self.pack_optimization_thread.started.connect(self.pack_optimization_worker.run)
            self.pack_optimization_worker.finished.connect(self.on_pack_optimization_finished)
            self.pack_optimization_worker.finished.connect(self.pack_optimization_thread.quit)
            self.pack_optimization_worker.finished.connect(self.pack_optimization_worker.deleteLater)
            self.pack_optimization_thread.finished.connect(self.pack_optimization_thread.deleteLater)
            print("--- Starting optimization thread ---")
            self.pack_optimization_thread.start()
        except Exception as e:
            print(f"--- Error in run_optimization_pack for {pack_title}: {str(e)} ---")
            show_critical_message(self, "Error", f"Failed to run {pack_title}: {str(e)}")

    def on_pack_progress_update(self, value, text):
        print(f"--- Progress update: {value}% - {text} ---")
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(value)
            self.progress_dialog.setLabelText(text)
            QApplication.processEvents()

    def on_pack_result_ready(self, result, success):
        print(f"--- Result ready: {result} (success: {success}) ---")
        self.pack_optimization_results.append(result)

    def on_pack_cancel(self):
        print("--- Cancelling optimization pack ---")
        if hasattr(self, 'pack_optimization_worker'):
            self.pack_optimization_worker.stop()
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setLabelText("Cancelling...")
            self.progress_dialog.setEnabled(False)
            QApplication.processEvents()

    def on_pack_optimization_finished(self):
        print("--- Pack optimization finished ---")
        if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
            self.progress_dialog.close()
        QTimer.singleShot(100, self.show_pack_completion_dialog)

    def show_pack_completion_dialog(self):
        print("--- Showing pack completion dialog ---")
        themes = Themes().items
        msg_box = PyMessageBox(self)
        msg_box.setWindowTitle("Optimization Complete")
        msg_box.setMinimumSize(600, 400)
        result_text = "Optimization task completed:\n\n" + ("\n".join(self.pack_optimization_results) or "No results available")
        msg_box.setText(result_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        print(f"--- Completion dialog text: {result_text} ---")
        msg_box.show()
        QApplication.processEvents()

    def optimize_selected(self):
        try:
            print("--- Starting optimize_selected ---")
            themes = Themes().items
            scroll_layouts = [
                (self.optimize_pc_scroll_layout, "Optimize PC"),
                (self.clean_pc_scroll_layout, "Clean PC"),
                (self.optimize_internet_scroll_layout, "Optimize Internet"),
            ]
            selected_options = []
            for scroll_layout, category in scroll_layouts:
                if not scroll_layout:
                    print(f"No layout for {category}")
                    continue
                print(f"Processing layout: {category}, count: {scroll_layout.count()}")
                for i in range(scroll_layout.count()):
                    item = scroll_layout.itemAt(i)
                    if not item:
                        print(f"No item at index {i} in {category}")
                        continue
                    frame = item.widget()
                    if not frame:
                        print(f"No widget at index {i} in {category}")
                        continue
                    layout = frame.layout()
                    if not layout:
                        print(f"No layout for frame at index {i} in {category}")
                        continue
                    toggle_layout = layout.itemAt(layout.count() - 1)
                    if not toggle_layout or not toggle_layout.layout():
                        print(f"No toggle layout at index {i} in {category}")
                        continue
                    toggle = toggle_layout.layout().itemAt(1).widget()
                    title = layout.itemAt(0).widget().text()
                    print(f"Found option: {title} in {category}, checked: {toggle.isChecked()}")
                    if toggle.isChecked() and (title, category) not in selected_options:
                        selected_options.append((title, category))
            if selected_options:
                print(f"Optimizing: {', '.join([f'{title} ({cat})' for title, cat in selected_options])}")
                self.progress_dialog = QProgressDialog("Running optimizations...", "Cancel", 0, 100, self)
                self.progress_dialog.setWindowTitle("Optimization Progress")
                self.progress_dialog.setMinimumSize(500, 150)
                self.progress_dialog.setStyleSheet(f"""
                    QProgressDialog {{
                        background-color: {themes['app_color']['dark_one']};
                        color: {themes['app_color']['text_foreground']};
                        border: 2px solid {themes['app_color']['context_color']};
                        border-radius: 10px;
                        font-family: 'Segoe UI';
                        font-size: 12pt;
                    }}
                    QProgressBar {{
                        background-color: {themes['app_color']['dark_two']};
                        color: {themes['app_color']['text_foreground']};
                        border: 2px solid {themes['app_color']['context_color']};
                        border-radius: 8px;
                        text-align: center;
                        font-weight: bold;
                        font-size: 11pt;
                        min-height: 25px;
                    }}
                    QProgressBar::chunk {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 {themes['app_color']['context_color']},
                            stop:1 {themes['app_color']['context_hover']});
                        border-radius: 6px;
                        margin: 2px;
                    }}
                    QPushButton {{
                        background-color: {themes['app_color']['context_color']};
                        color: #FFFFFF;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: bold;
                        font-size: 11pt;
                        min-width: 80px;
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
                    QLabel {{
                        color: {themes['app_color']['text_foreground']};
                        font-size: 11pt;
                        font-weight: bold;
                        padding: 5px;
                    }}
                """)
                self.progress_dialog.setModal(True)
                self.progress_dialog.setAutoClose(False)
                self.progress_dialog.setAutoReset(False)
                self.progress_dialog.canceled.connect(self.on_cancel)
                self.optimization_thread = QThread(self)
                self.optimization_worker = OptimizationWorker(selected_options, option_functions)
                self.optimization_worker.moveToThread(self.optimization_thread)
                self.optimization_worker.progress_update.connect(self.on_progress_update)
                self.optimization_worker.result_ready.connect(self.on_result_ready)
                self.optimization_thread.started.connect(self.optimization_worker.run)
                self.optimization_worker.finished.connect(self.on_optimization_finished)
                self.optimization_worker.finished.connect(self.optimization_thread.quit)
                self.optimization_worker.finished.connect(self.optimization_worker.deleteLater)
                self.optimization_thread.finished.connect(self.optimization_thread.deleteLater)
                self.optimization_results = []
                print("--- Starting optimization thread for optimize_selected ---")
                self.progress_dialog.forceShow()
                QApplication.processEvents()
                self.optimization_thread.start()
            else:
                print("No options selected")
                show_info_message(self, "No Options Selected", "Please select at least one optimization option.")
        except Exception as e:
            print(f"--- Error in optimize_selected: {str(e)} ---")
            show_critical_message(self, "Error", f"An error occurred in optimize_selected: {str(e)}")

    def on_progress_update(self, value, text):
        print(f"--- Progress update: {value}% - {text} ---")
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(value)
            self.progress_dialog.setLabelText(text)
            QApplication.processEvents()

    def on_result_ready(self, result, success):
        print(f"--- Result ready: {result} (success: {success}) ---")
        self.optimization_results.append(result)

    def on_cancel(self):
        print("--- Cancelling optimization ---")
        if hasattr(self, 'optimization_worker'):
            self.optimization_worker.stop()
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setLabelText("Cancelling...")
            self.progress_dialog.setEnabled(False)
            QApplication.processEvents()

    def on_optimization_finished(self):
        print("--- Optimization finished ---")
        if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
            self.progress_dialog.close()
        QTimer.singleShot(100, self.show_completion_dialog)

    def show_completion_dialog(self):
        print("--- Showing completion dialog ---")
        themes = Themes().items
        msg_box = PyMessageBox(self)
        msg_box.setWindowTitle("Optimization Complete")
        msg_box.setMinimumSize(600, 400)
        result_text = "Optimization tasks completed:\n\n" + ("\n".join(self.optimization_results) or "No results available")
        msg_box.setText(result_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        print(f"--- Completion dialog text: {result_text} ---")
        msg_box.show()
        QApplication.processEvents()

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def toggle_advanced(self, button):
        if hasattr(self, 'advanced_scroll_area') and self.advanced_scroll_area.isVisible():
            self.advanced_scroll_area.setVisible(False)
            button.setText("Advanced")
        else:
            self.advanced_scroll_area.setVisible(True)
            button.setText("Basic")

    def setup_ai(self):
        self.input_field.returnPressed.connect(
            lambda: AstreisFunc.send_message(self.input_field, self.scroll_layout, self.themes))
        self.send_button.clicked.connect(
            lambda: AstreisFunc.send_message(self.input_field, self.scroll_layout, self.themes))

class OptimizationWorker(QObject):
    finished = Signal()
    result_ready = Signal(str, bool)
    progress_update = Signal(int, str)

    def __init__(self, selected_options, option_functions):
        super().__init__()
        self.selected_options = selected_options
        self.option_functions = option_functions
        self._running = True

    def stop(self):
        self._running = False
        print("--- Worker stopped ---")

    def run(self):
        print("--- Worker started ---")
        total_options = len(self.selected_options)
        for i, (title, category) in enumerate(self.selected_options):
            if not self._running:
                print(f"--- Worker stopped at {title} ---")
                break
            print(f"--- Worker: Processing {title} ({category}) ---")
            self.progress_update.emit(0, f"Starting: {title}...")
            QApplication.processEvents()
            if title in self.option_functions:
                try:
                    print(f"--- Worker: Calling {title} function ---")
                    time.sleep(0.5)  # Simulate work to ensure progress bar is visible
                    success, message = self.option_functions[title]()
                    print(f"--- Worker: {title} completed (success: {success}, message: {message}) ---")
                    if success:
                        result_msg = f"{title}: {message}"
                    else:
                        result_msg = f"{title}: Skipped - {message}"
                    self.result_ready.emit(result_msg, success)
                except Exception as e:
                    print(f"--- Worker: {title} failed with error: {str(e)} ---")
                    result_msg = f"{title}: Skipped due to error - {str(e)}"
                    self.result_ready.emit(result_msg, False)
                self.progress_update.emit(100, f"Completed: {title}")
                QApplication.processEvents()
            else:
                print(f"--- Worker: {title} not found in option_functions ---")
                result_msg = f"{title}: Skipped - Function not found"
                self.result_ready.emit(result_msg, False)
                self.progress_update.emit(100, f"Completed: {title}")
                QApplication.processEvents()
        print("--- Worker: All tasks completed ---")
        self.progress_update.emit(100, "Optimization Complete")
        self.finished.emit()

if __name__ == "__main__":
    instance_socket = check_single_instance()
    if not instance_socket:
        print("--- Another instance is already running, exiting ---")
        sys.exit(0)
    run_as_admin()
    try:
        print("--- Creating QApplication ---")
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon("icon.ico"))
        print("--- Creating MainWindow ---")
        window = MainWindow()
        print("--- Starting event loop (app.exec()) ---")
        exit_code = app.exec()
        print(f"--- Event loop finished with exit code: {exit_code} ---")
        instance_socket.close()
        sys.exit(exit_code)
    except Exception as e:
        print(f"--- An unhandled exception occurred: {e} ---")
        import traceback
        traceback.print_exc()
        show_critical_message(None, "Fatal Error", f"A fatal error occurred and the application must close:\n\n{e}")
        input("Press Enter to exit...")
    finally:
        print("--- Script Exiting ---")
        time.sleep(2)