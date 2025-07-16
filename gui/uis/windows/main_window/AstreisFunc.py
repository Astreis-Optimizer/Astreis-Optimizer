# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================
import os
import shutil
import subprocess
import winreg
import psutil
import sqlite3
from win32com.shell import shell, shellcon
from groq import Groq
from gui.core.qt_core import *
import dns.resolver
import ctypes
import sys
import wmi
import win32com.client
import win32api
import win32con
import win32security
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import struct
import time
import datetime
import tempfile
import glob
import re
# Path
from pathlib import Path

# =============================================================================
# ASTREIS FUNCTIONALITY CLASS
# =============================================================================
class AstreisFunc:
    _chat_history = []

    def __init__(self):
        pass

    # =============================================================================
    # CHAT HISTORY MANAGEMENT
    # =============================================================================
    @staticmethod
    def clear_history():
        AstreisFunc._chat_history = []

    @staticmethod
    def get_history():
        return AstreisFunc._chat_history.copy()

    # =============================================================================
    # AI CHAT FUNCTIONALITY
    # =============================================================================
    @staticmethod
    def send_message(input_field, scroll_layout, themes):
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QLabel, QScrollArea
        from groq import Groq
        client = Groq(api_key='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')
        user_input = input_field.text()
        if not user_input.strip():
            return
        user_message = QLabel(f"You: {user_input}")
        user_message.setStyleSheet(
            f"font: 12pt 'Segoe UI'; color: {themes['app_color']['text_description']}; "
            "background-color: #343B48; border-radius: 10px; padding: 10px; margin: 5px;"
        )
        user_message.setWordWrap(True)
        scroll_layout.addWidget(user_message)
        AstreisFunc._chat_history.append({"role": "user", "content": user_input})
        messages = [
            {
                "role": "system",
                "content": "You are Astreis, a friendly and expert AI assistant integrated into the Astreis PC Optimizer application. Your goal is to help users with PC optimization. Provide clear, concise, and practical advice. You can answer questions about improving computer performance, managing resources, and troubleshooting common issues for Windows systems."
            }
        ]
        messages.extend(AstreisFunc._chat_history[-10:])
        ai_response = QLabel("AI: ")
        ai_response.setStyleSheet(
            f"font: bold 12pt 'Segoe UI'; color: {themes['app_color']['text_description']}; "
            "background-color: #2A2F3B; border-radius: 10px; padding: 10px; margin: 5px;"
        )
        ai_response.setWordWrap(True)
        scroll_layout.addWidget(ai_response)
        try:
            completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=messages,
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )
            full_response = ""
            response_chunks = [chunk.choices[0].delta.content or "" for chunk in completion]
            def stream_text(index=0):
                nonlocal full_response
                try:
                    if index < len(response_chunks):
                        full_response += response_chunks[index]
                        ai_response.setText(f"AI: {full_response}")
                        scroll_area = scroll_layout.parent()
                        while scroll_area and not isinstance(scroll_area, QScrollArea):
                            scroll_area = scroll_area.parent()
                        if scroll_area:
                            scroll_area.verticalScrollBar().setValue(scroll_area.verticalScrollBar().maximum())
                        QTimer.singleShot(50, lambda: stream_text(index + 1))
                    else:
                        AstreisFunc._chat_history.append({"role": "assistant", "content": full_response})
                except RuntimeError:
                    print("AI response label was deleted during streaming. Halting.")
            QTimer.singleShot(50, lambda: stream_text())
        except Exception as e:
            ai_response.setText("AI: Error connecting to the service.")
            print(f"[ERROR] {e}")
        input_field.clear()
        scroll_area = scroll_layout.parent()
        while scroll_area and not isinstance(scroll_area, QScrollArea):
            scroll_area = scroll_area.parent()
        if scroll_area:
            scroll_area.verticalScrollBar().setValue(scroll_area.verticalScrollBar().maximum())

    @staticmethod
    def optimize_startup_apps():
        print("Disabling startup applications...")
        startup_keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        ]

        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        disabled_count = 0
        key_details = []

        for hkey, subkey_path in startup_keys:
            try:
                # Backup the key first
                key_name = "HKCU" if hkey == winreg.HKEY_CURRENT_USER else "HKLM"
                backup_file = os.path.join(backup_dir, f"startup_{key_name}_run_backup_{int(time.time())}.reg")
                subprocess.run(['reg', 'export', f'{"HKEY_CURRENT_USER" if hkey == winreg.HKEY_CURRENT_USER else "HKEY_LOCAL_MACHINE"}\\{subkey_path}', backup_file, '/y'], check=True)
                print(f"Backed up {key_name}\\{subkey_path} to {backup_file}")

                # Clear the keys
                with winreg.OpenKey(hkey, subkey_path, 0, winreg.KEY_ALL_ACCESS) as regkey:
                    while True:
                        try:
                            value_name, _, _ = winreg.EnumValue(regkey, 0)
                            winreg.DeleteValue(regkey, value_name)
                            disabled_count += 1
                            print(f"Disabled startup item: {value_name}")
                        except OSError:
                            break # No more values
                    key_details.append(f"{key_name}\\{subkey_path}")

            except FileNotFoundError:
                print(f"Startup key not found: {subkey_path}")
                continue
            except Exception as e:
                print(f"Error processing startup key {subkey_path}: {e}")
                return (False, f"Error processing startup key: {e}")

        if disabled_count > 0:
            return (True, f"Disabled {disabled_count} startup items. Backups created in the backups folder.")
        else:
            return (True, "No startup items found to disable.")

    @staticmethod
    def optimize_services():
        print("Disabling unnecessary services using low-level API...")

        services_to_disable = [
            ("diagtrack", "Connected User Experiences and Telemetry"),
            ("dmwappushservice", "Device Management Wireless Application Protocol (WAP) Push message Routing Service"),
            ("Fax", "Fax Service"),
            ("Spooler", "Print Spooler"),
            ("RemoteRegistry", "Remote Registry"),
            ("TabletInputService", "Touch Keyboard and Handwriting Panel"),
            ("WbioSrvc", "Windows Biometric Service"),
            ("StiSvc", "Windows Image Acquisition (WIA)"),
            ("iphlpsvc", "IP Helper"),
            ("AJRouter", "AllJoyn Router Service"),
            ("wisvc", "Windows Insider Service"),
            ("PcaSvc", "Program Compatibility Assistant Service"),
            ("WerSvc", "Windows Error Reporting Service"),
            ("DoSvc", "Delivery Optimization"),
            ("TermService", "Remote Desktop Service"),
            ("XboxGipSvc", "Xbox Accessory Management Service"),
            ("XblAuthManager", "Xbox Live Auth Manager"),
            ("XboxNetApiSvc", "Xbox Live Networking Service"),
        ]

        disabled_count = 0
        failed_services = []
        scm_handle = None

        try:
            scm_handle = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)

            for service_name, display_name in services_to_disable:
                service_handle = None
                try:
                    service_handle = win32service.OpenService(scm_handle, service_name, win32service.SERVICE_CHANGE_CONFIG)
                    win32service.ChangeServiceConfig(
                        service_handle,
                        win32service.SERVICE_NO_CHANGE,
                        win32service.SERVICE_DISABLED,
                        win32service.SERVICE_NO_CHANGE,
                        None, None, 0, None, None, None, None
                    )
                    print(f"Successfully set {display_name} to disabled.")
                    disabled_count += 1
                except Exception as e:
                    if isinstance(e, win32service.error) and e.winerror == 1060:
                        print(f"Service not found, skipping: {display_name} ({service_name})")
                    else:
                        print(f"Could not disable service {display_name}: {e}")
                        failed_services.append(display_name)
                finally:
                    if service_handle:
                        win32service.CloseServiceHandle(service_handle)

        except Exception as e:
            print(f"Failed to open Service Control Manager: {e}")
            return (False, "Failed to access Service Control Manager. See console for details.")
        finally:
            if scm_handle:
                win32service.CloseServiceHandle(scm_handle)

        if not failed_services:
            return (True, f"Successfully disabled {disabled_count} services. A restart is required for changes to take full effect.")
        elif disabled_count > 0:
            return (True, f"Partially completed: Disabled {disabled_count} services. See console for details.")
        else:
            return (False, "Operation failed. See console for details.")

    @staticmethod
    def make_restore_point():
        print("Creating a system restore point...")
        try:
            # Command to create a system restore point using PowerShell
            command = 'powershell.exe -Command "Checkpoint-Computer -Description AstreisRestorePoint -RestorePointType MODIFY_SETTINGS"'

            # Execute the command
            result = subprocess.run(command, check=True, capture_output=True, text=True, shell=True)

            print(f"Restore point creation stdout: {result.stdout}")
            if result.stderr:
                print(f"Restore point creation stderr: {result.stderr}")

            # Check if the command was successful. A zero return code indicates success.
            if result.returncode == 0:
                return (True, "System restore point 'AstreisRestorePoint' created successfully.")
            else:
                return (False, "Failed to create restore point. The System Restore service might be disabled.")

        except subprocess.CalledProcessError as e:
            # This catches errors where the command returns a non-zero exit code
            error_message = f"Failed to create restore point. Error: {e.stderr}"
            print(error_message)
            return (False, "Failed to create restore point. The System Restore service might be disabled.")
        except Exception as e:
            # This catches other exceptions like file not found if powershell isn't in path
            error_message = f"An unexpected error occurred: {e}"
            print(error_message)
            return (False, "An unexpected error occurred while creating restore point.")

    # =============================================================================
    # POWER MANAGEMENT UTILITIES
    # =============================================================================
    @staticmethod
    def get_available_power_settings(guid):
        """Get list of available power settings for a given GUID"""
        try:
            result = subprocess.run(['powercfg', '/query', guid], capture_output=True, text=True, check=True)
            available_settings = []
            current_group = None

            for line in result.stdout.splitlines():
                if line.strip().startswith('Subgroup GUID:'):
                    # Extract subgroup name
                    if 'SUB_PROCESSOR' in line:
                        current_group = 'SUB_PROCESSOR'
                    elif 'SUB_DISK' in line:
                        current_group = 'SUB_DISK'
                    elif 'SUB_VIDEO' in line:
                        current_group = 'SUB_VIDEO'
                    elif 'SUB_SYSTEM' in line:
                        current_group = 'SUB_SYSTEM'
                    elif 'SUB_BUTTONS' in line:
                        current_group = 'SUB_BUTTONS'
                    elif 'SUB_USB' in line:
                        current_group = 'SUB_USB'
                    elif 'SUB_GRAPHICS' in line:
                        current_group = 'SUB_GRAPHICS'
                    elif 'SUB_MEMORY' in line:
                        current_group = 'SUB_MEMORY'
                    elif 'SUB_INTERNET' in line:
                        current_group = 'SUB_INTERNET'
                    elif 'SUB_MULTIMEDIA' in line:
                        current_group = 'SUB_MULTIMEDIA'
                    elif 'SUB_WIRELESSADAPTER' in line:
                        current_group = 'SUB_WIRELESSADAPTER'
                elif line.strip().startswith('Power Setting GUID:') and current_group:
                    # Extract setting name
                    setting_match = re.search(r'Power Setting GUID: ([0-9a-f-]+)', line, re.IGNORECASE)
                    if setting_match:
                        setting_guid = setting_match.group(1)
                        # Try to get the friendly name
                        try:
                            name_result = subprocess.run(['powercfg', '/q', guid, setting_guid],
                                                       capture_output=True, text=True, check=True)
                            for name_line in name_result.stdout.splitlines():
                                if 'Friendly Name:' in name_line:
                                    setting_name = name_line.split('Friendly Name:')[1].strip()
                                    available_settings.append((current_group, setting_name, setting_guid))
                                    break
                        except:
                            pass

            return available_settings
        except Exception as e:
            print(f"Error getting available settings: {e}")
            return []

    @staticmethod
    def optimize_defrag():
        try:
            print("Starting drive defragmentation analysis...")

            drives = []
            ssd_drives = []

            for partition in psutil.disk_partitions():
                if partition.device and 'ntfs' in partition.fstype.lower():
                    drive_letter = partition.device[0]
                    # Check if it's an SSD
                    try:
                        result = subprocess.run(
                            ['powershell', '-Command', f"(Get-PhysicalDisk -DeviceNumber (Get-Partition -DriveLetter {drive_letter}).DiskNumber).MediaType"],
                            capture_output=True, text=True, check=True, timeout=10
                        )
                        if 'ssd' in result.stdout.lower():
                            ssd_drives.append(drive_letter)
                    except Exception:
                        # Fallback for older systems or if powershell fails
                        try:
                            result = subprocess.run(['wmic', 'diskdrive', 'get', 'MediaType'],
                                                 capture_output=True, text=True, check=True, timeout=10)
                            if 'ssd' in result.stdout.lower():
                                ssd_drives.append(drive_letter)
                        except:
                            pass # Assume HDD if detection fails
                    drives.append(drive_letter)

            if not drives:
                return (False, "No NTFS drives found to defragment.")

            results = []
            defrag_performed = False

            for drive in drives:
                if drive in ssd_drives:
                    results.append(f"Drive {drive}: Skipped (SSD)")
                    print(f"[INFO] Skipping SSD drive {drive}")
                    continue

                print(f"Analyzing drive {drive}:")
                try:
                    analysis_result = subprocess.run(['defrag', f'{drive}:', '/A'], capture_output=True, text=True, timeout=60)
                    if "You do not need to defragment this volume" in analysis_result.stdout:
                        results.append(f"Drive {drive}: No defragmentation needed")
                        print(f"[OK] Drive {drive}: No defragmentation needed")
                        continue

                    if "It is recommended that you defragment this volume" in analysis_result.stdout:
                        print(f"Defragmenting drive {drive}:")
                        defrag_result = subprocess.run(['defrag', f'{drive}:', '/D'], capture_output=True, text=True, timeout=300)
                        defrag_performed = True
                        if defrag_result.returncode == 0:
                            results.append(f"Drive {drive}: Defragmentation successful")
                            print(f"[OK] Drive {drive}: Defragmentation successful")
                        else:
                            results.append(f"Drive {drive}: Defragmentation completed with warnings")
                            print(f"[WARNING] Drive {drive}: Defragmentation completed with warnings")
                    else:
                        results.append(f"Drive {drive}: Analysis complete, no action taken")
                        print(f"[INFO] Drive {drive}: Analysis complete, no action taken")

                except subprocess.TimeoutExpired:
                    results.append(f"Drive {drive}: Operation timed out")
                    print(f"[WARNING] Timeout on drive {drive}")
                except Exception as e:
                    results.append(f"Drive {drive}: An error occurred")
                    print(f"[ERROR] Unexpected error with drive {drive}: {e}")

            final_message = "Defragmentation Report:\n" + "\n".join(results)
            return (True, final_message)

        except Exception as e:
            print(f"Error in optimize_defrag: {str(e)}")
            return (False, f"An error occurred during defragmentation setup: {e}")

    @staticmethod
    def optimize_appearance():
        try:
            print("Starting appearance optimization...")

            import winreg
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            dwmapi = ctypes.windll.dwmapi

            SPI_SETUIEFFECTS = 0x103F
            SPI_SETCOMBOBOXANIMATION = 0x1006
            SPI_SETLISTBOXSMOOTHSCROLLING = 0x1007
            SPI_SETGRADIENTCAPTIONS = 0x1008
            SPI_SETMENUANIMATION = 0x1009
            SPI_SETSELECTIONFADE = 0x1015
            SPI_SETTOOLTIPANIMATION = 0x1016
            SPI_SETCURSORSHADOW = 0x101B
            SPI_SETICONSHADOW = 0x101C
            SPI_SETDROPSHADOW = 0x1025
            SPI_SETBLOCKSENDINPUTRESETS = 0x1026
            SPI_SETSHOWIMEUI = 0x1027
            SPI_SETMOUSESONAR = 0x101D
            SPI_SETMOUSECLICKLOCK = 0x101E
            SPI_SETMOUSEVANISH = 0x1021
            SPI_SETFLATMENU = 0x1022
            SPI_SETDOCKMOVING = 0x1023
            SPI_SETACTIVEWINDOWTRACKING = 0x1001
            SPI_SETACTIVEWNDTRKZORDER = 0x100C
            SPI_SETACTIVEWNDTRKTIMEOUT = 0x2002
            SPI_SETANIMATION = 0x0049
            SPI_SETCARETWIDTH = 0x2007
            SPI_SETCARETBROWSING = 0x2009
            SPI_SETCLEARTYPE = 0x1049
            SPI_SETDESKWALLPAPER = 0x0014
            SPI_SETDRAGFULLWINDOWS = 0x0025
            SPI_SETDRAGHEIGHT = 0x004D
            SPI_SETDRAGWIDTH = 0x004C
            SPI_SETFASTTASKSWITCH = 0x0024
            SPI_SETFONTSMOOTHING = 0x004B
            SPI_SETFONTSMOOTHINGCONTRAST = 0x2005
            SPI_SETFONTSMOOTHINGORIENTATION = 0x2012
            SPI_SETFONTSMOOTHINGTYPE = 0x200B
            SPI_SETFOREGROUNDFLASHCOUNT = 0x2000
            SPI_SETFOREGROUNDLOCKTIMEOUT = 0x2001
            SPI_SETGRIDGRANULARITY = 0x0013
            SPI_SETICONMETRICS = 0x002E
            SPI_SETICONTITLELOGFONT = 0x0022
            SPI_SETICONTITLEWRAP = 0x001A
            SPI_SETKEYBOARDCUES = 0x100B
            SPI_SETKEYBOARDPREF = 0x0045
            SPI_SETLOWPOWERACTIVE = 0x0055
            SPI_SETLOWPOWERTIMEOUT = 0x0054
            SPI_SETMENUDROPALIGNMENT = 0x001C
            SPI_SETMINIMIZEDMETRICS = 0x002C
            SPI_SETMOUSE = 0x0004
            SPI_SETMOUSEBUTTONSWAP = 0x0021
            SPI_SETMOUSECLICKLOCKTIME = 0x2008
            SPI_SETMOUSEDOUBLECLICKTIME = 0x0015
            SPI_SETMOUSEDOUBLECLICKWIDTH = 0x0030
            SPI_SETMOUSEDRAGOUTTHRESHOLD = 0x0045
            SPI_SETMOUSEHOVERHEIGHT = 0x0064
            SPI_SETMOUSEHOVERTIME = 0x0066
            SPI_SETMOUSEHOVERWIDTH = 0x0063
            SPI_SETMOUSESPEED = 0x0071
            SPI_SETMOUSETRAILS = 0x005D
            SPI_SETMOUSEWHEELROUTING = 0x201C
            SPI_SETNONCLIENTMETRICS = 0x002A
            SPI_SETPENWINDOWS = 0x0031
            SPI_SETSCREENSAVEACTIVE = 0x0011
            SPI_SETSCREENSAVERRUNNING = 0x0061
            SPI_SETSCREENSAVETIMEOUT = 0x000F
            SPI_SETSERIALKEYS = 0x003F
            SPI_SETSHOWSOUNDS = 0x0039
            SPI_SETSNAPTODEFBUTTON = 0x0060
            SPI_SETSOUNDSENTRY = 0x0041
            SPI_SETSTICKYKEYS = 0x003B
            SPI_SETSYSTEMLANGUAGEBAR = 0x1050
            SPI_SETTHREADLOCALINPUTSETTINGS = 0x104F
            SPI_SETTOGGLEKEYS = 0x0035
            SPI_SETWHEELSCROLLCHARS = 0x006D
            SPI_SETWHEELSCROLLLINES = 0x0069
            SPI_SETWORKAREA = 0x002F

            SPIF_UPDATEINIFILE = 0x01
            SPIF_SENDCHANGE = 0x02

            user32.SystemParametersInfoW(SPI_SETUIEFFECTS, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETCOMBOBOXANIMATION, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETLISTBOXSMOOTHSCROLLING, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETGRADIENTCAPTIONS, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETMENUANIMATION, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETSELECTIONFADE, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETTOOLTIPANIMATION, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETCURSORSHADOW, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETICONSHADOW, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETDROPSHADOW, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETMOUSESONAR, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETMOUSECLICKLOCK, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETMOUSEVANISH, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETFLATMENU, 1, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETDOCKMOVING, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETACTIVEWINDOWTRACKING, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETACTIVEWNDTRKZORDER, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETACTIVEWNDTRKTIMEOUT, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETANIMATION, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETDRAGFULLWINDOWS, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETFONTSMOOTHING, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            user32.SystemParametersInfoW(SPI_SETCLEARTYPE, 0, None, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)

            try:
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
            except Exception as e:
                print(f"Registry modification failed: {e}")

            try:
                key_path = r"Software\Microsoft\Windows\DWM"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "EnableAeroPeek", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(key, "AlwaysHibernateThumbnails", 0, winreg.REG_DWORD, 0)
            except Exception as e:
                print(f"DWM registry modification failed: {e}")

            try:
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, "IconsOnly", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(key, "ListviewAlphaSelect", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(key, "ListviewShadow", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(key, "TaskbarAnimations", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(key, "ListviewWatermark", 0, winreg.REG_DWORD, 0)
            except Exception as e:
                print(f"Explorer registry modification failed: {e}")

            print("Appearance optimization completed successfully")
            return (True, "Appearance optimized for performance.")

        except Exception as e:
            print(f"Error in optimize_appearance: {str(e)}")
            return (False, f"An error occurred: {e}")

    @staticmethod
    def optimize_astreis_power_plan():
        try:
            print("Starting power plan optimization...")
            power_plan_name = "Astreis Power Plan"
            high_perf_guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"

            # First, check if the power plan already exists
            print("Checking for existing power plan...")
            result = subprocess.run(['powercfg', '/list'], capture_output=True, text=True, check=True)
            guid = None

            for line in result.stdout.splitlines():
                if power_plan_name in line:
                    print(f"Found existing power plan: {line}")
                    match = re.search(r'GUID: ([0-9a-f-]+)', line, re.IGNORECASE)
                    if match:
                        guid = match.group(1)
                        print(f"Extracted GUID: {guid}")
                        break

            # If not found, create it by duplicating the high performance plan
            if not guid:
                print("Power plan not found, creating new one...")
                result = subprocess.run(['powercfg', '/duplicatescheme', high_perf_guid], capture_output=True, text=True, check=True)
                print(f"Duplicate result: {result.stdout}")

                # Extract GUID from the duplicate result
                for line in result.stdout.splitlines():
                    if 'GUID:' in line:
                        match = re.search(r'GUID: ([0-9a-f-]+)', line, re.IGNORECASE)
                        if match:
                            guid = match.group(1)
                            print(f"Created new power plan with GUID: {guid}")
                            break

                # If still no GUID, try listing again
                if not guid:
                    print("GUID not found in duplicate result, checking list again...")
                    result = subprocess.run(['powercfg', '/list'], capture_output=True, text=True, check=True)
                    for line in result.stdout.splitlines():
                        if power_plan_name in line:
                            match = re.search(r'GUID: ([0-9a-f-]+)', line, re.IGNORECASE)
                            if match:
                                guid = match.group(1)
                                print(f"Found GUID in second list: {guid}")
                                break

            if guid:
                print(f"Configuring power plan with GUID: {guid}")
                # Rename the power plan
                subprocess.run(['powercfg', '/changename', guid, power_plan_name], check=True)
                print("Power plan renamed successfully")

                # Configure power plan settings - only use the most essential and widely-supported settings
                essential_settings = [
                    # Core processor settings (most important for performance)
                    ('SUB_PROCESSOR', 'PROCTHROTTLEMAX', '100'),
                    ('SUB_PROCESSOR', 'PROCTHROTTLEMIN', '50'),
                    ('SUB_PROCESSOR', 'PERFBOOSTMODE', '1'),
                    ('SUB_PROCESSOR', 'CPMAXCORES', '100'),
                    ('SUB_PROCESSOR', 'LATENCYHINTPERF', '1'),
                    ('SUB_PROCESSOR', 'IDLESCALING', '0'),
                    ('SUB_PROCESSOR', 'PERFINCTHRESHOLD', '90'),
                    ('SUB_PROCESSOR', 'CPMINCORES', '100'),
                    ('SUB_PROCESSOR', 'SCHEDPOLICY', '5'),

                    # Core system settings
                    ('SUB_DISK', 'DISKIDLE', '0'),
                    ('SUB_VIDEO', 'VIDEOIDLE', '0'),
                    ('SUB_BUTTONS', 'PBUTTONACTION', '3'),
                    ('SUB_SYSTEM', 'AWAYMODE', '0'),
                    ('SUB_USB', 'USBSUSPEND', '0'),
                ]

                print("Applying essential power plan settings...")
                successful_settings = 0
                total_settings = len(essential_settings)

                for group, setting, value in essential_settings:
                    try:
                        subprocess.run(['powercfg', '/setacvalueindex', guid, group, setting, value],
                                     capture_output=True, check=True)
                        subprocess.run(['powercfg', '/setdcvalueindex', guid, group, setting, value],
                                     capture_output=True, check=True)
                        successful_settings += 1
                        print(f"[OK] Applied {group}/{setting} = {value}")
                    except subprocess.CalledProcessError as e:
                        print(f"[WARNING] Skipped {group}/{setting} (not available on this system)")
                    except Exception as e:
                        print(f"[WARNING] Error with {group}/{setting}: {e}")

                print(f"Successfully applied {successful_settings}/{total_settings} essential settings")

                # Try some additional settings that might be available
                optional_settings = [
                    ('SUB_PROCESSOR', 'PERFAUTONOMOUS', '1'),
                    ('SUB_PROCESSOR', 'PERFCHECK', '1'),
                    ('SUB_BUTTONS', 'LIDACTION', '0'),
                    ('SUB_BUTTONS', 'SBUTTONACTION', '0'),
                    ('SUB_SYSTEM', 'SLEEPIDLETIMEOUT', '0'),
                    ('SUB_GRAPHICS', 'GPUPowerPolicy', '0'),
                    ('SUB_MEMORY', 'MEMLATENCY', '0'),
                ]

                print("Applying optional power plan settings...")
                for group, setting, value in optional_settings:
                    try:
                        subprocess.run(['powercfg', '/setacvalueindex', guid, group, setting, value],
                                     capture_output=True, check=True)
                        subprocess.run(['powercfg', '/setdcvalueindex', guid, group, setting, value],
                                     capture_output=True, check=True)
                        print(f"[OK] Applied optional {group}/{setting} = {value}")
                    except subprocess.CalledProcessError:
                        pass  # Silently skip optional settings
                    except Exception as e:
                        print(f"[WARNING] Error with optional {group}/{setting}: {e}")

                # Activate the power plan
                print("Activating power plan...")
                subprocess.run(['powercfg', '/setactive', guid], check=True)
                print(f"Astreis Power Plan {guid} configured and activated successfully")
                return (True, "Astreis Power Plan configured and activated.")
            else:
                print("Failed to create or find Astreis Power Plan - no GUID obtained")
                return (False, "Failed to create or find Astreis Power Plan.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing powercfg command: {e}")
            print(f"Command output: {e.stdout if hasattr(e, 'stdout') else 'No output'}")
            print(f"Command error: {e.stderr if hasattr(e, 'stderr') else 'No error'}")
            return (False, f"A powercfg command failed: {e}")
        except Exception as e:
            print(f"Unexpected error in optimize_astreis_power_plan: {str(e)}")
            return (False, f"An unexpected error occurred: {e}")

    @staticmethod
    def optimize_registry():
        print("optimize_registry: Starting")
        try:
            backup_dir = os.path.expanduser("~/Astreis_Registry_Backups")
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # e.g., 20250626_1623
            print(f"optimize_registry: Creating backups with timestamp {timestamp}")
            backup_path_hklm = os.path.join(backup_dir, f"registry_hklm_backup_{timestamp}.reg")
            backup_path_hkcu = os.path.join(backup_dir, f"registry_hkcu_backup_{timestamp}.reg")
            backup_path_hkcr = os.path.join(backup_dir, f"registry_hkcr_backup_{timestamp}.reg")
            subprocess.run(["reg", "save", "HKLM", backup_path_hklm], check=False)
            subprocess.run(["reg", "save", "HKCU", backup_path_hkcu], check=False)
            subprocess.run(["reg", "save", "HKCR", backup_path_hkcr], check=False)
            if not (os.path.exists(backup_path_hklm) and os.path.exists(backup_path_hkcu) and os.path.exists(
                    backup_path_hkcr)):
                print("optimize_registry: Backup creation failed due to permissions")
                return (False, "Skipped: Insufficient permissions to create backups. Run as Administrator.")
            invalid_entries = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "InvalidApp"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "InvalidApp"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce", "TempApp"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce", "TempApp"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", "ObsoleteApp"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Internet Explorer\Extensions", None),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services", "ObsoleteService"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
                 "InvalidFolder"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\AppCompatFlags", None),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU", None),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Internet Explorer\TypedURLs", None),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Print\Printers", None),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths", "InvalidApp.exe"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs", None),
                (winreg.HKEY_CLASSES_ROOT, r".invalid", None),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.invalid",
                 None),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts", "InvalidFont"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData", None),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Network", None),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache", None),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\COM3", None),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
                 "InvalidPath"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\ShellNoRoam\MUICache", None),
                (winreg.HKEY_CURRENT_USER,
                 r"Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\TrayNotify", None),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Search Assistant", None),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\SharedDLLs", "InvalidDLL.dll"),
                (winreg.HKEY_CLASSES_ROOT, r"TypeLib", None),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Streams", None),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Shell Extensions\Approved",
                 None),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupCommands",
                 None),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace",
                 None),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Network", None),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                 "InvalidVar"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\PowerShell", None),
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy",
                 None)
            ]
            deleted_count = 0
            for hive, subkey, value_name in invalid_entries:
                print(f"optimize_registry: Checking {subkey} for {value_name or 'subkeys'}")
                try:
                    with winreg.OpenKey(hive, subkey, 0, winreg.KEY_ALL_ACCESS) as key:
                        if value_name:
                            try:
                                winreg.DeleteValue(key, value_name)
                                deleted_count += 1
                                print(f"optimize_registry: Deleted value {value_name} in {subkey}")
                            except (FileNotFoundError, PermissionError):
                                print(f"optimize_registry: Value {value_name} not found or access denied in {subkey}")
                                continue
                        else:
                            subkeys = []
                            try:
                                for i in range(winreg.QueryInfoKey(key)[0]):
                                    subkey_name = winreg.EnumKey(key, i)
                                    subkeys.append(subkey_name)
                            except (WindowsError, PermissionError):
                                print(f"optimize_registry: Failed to enumerate subkeys in {subkey}")
                                continue
                            for subkey_name in subkeys:
                                try:
                                    with winreg.OpenKey(key, subkey_name, 0, winreg.KEY_ALL_ACCESS) as sub_key:
                                        try:
                                            winreg.DeleteKey(key, subkey_name)
                                            deleted_count += 1
                                            print(f"optimize_registry: Deleted subkey {subkey_name} in {subkey}")
                                        except (WindowsError, PermissionError):
                                            print(
                                                f"optimize_registry: Failed to delete subkey {subkey_name} in {subkey}")
                                            continue
                                except (WindowsError, PermissionError):
                                    print(f"optimize_registry: Access denied to subkey {subkey_name} in {subkey}")
                                    continue
                except (FileNotFoundError, PermissionError):
                    print(f"optimize_registry: Key {subkey} not found or access denied")
                    continue
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Shell Extensions", 0,
                                    winreg.KEY_ALL_ACCESS) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name, 0, winreg.KEY_ALL_ACCESS) as sub_key:
                                try:
                                    winreg.DeleteKey(key, subkey_name)
                                    deleted_count += 1
                                    print(f"optimize_registry: Deleted shell extension {subkey_name}")
                                except (WindowsError, PermissionError):
                                    print(f"optimize_registry: Failed to delete shell extension {subkey_name}")
                                    continue
                        except (WindowsError, PermissionError):
                            print(f"optimize_registry: Failed to enumerate shell extensions")
                            pass
            except (FileNotFoundError, PermissionError):
                print("optimize_registry: Shell Extensions key not accessible")
                pass
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies", 0,
                                    winreg.KEY_ALL_ACCESS) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            if subkey_name in ["Explorer", "System"]:
                                continue
                            winreg.DeleteKey(key, subkey_name)
                            deleted_count += 1
                            print(f"optimize_registry: Deleted policy {subkey_name}")
                        except (WindowsError, PermissionError):
                            print(f"optimize_registry: Failed to delete policy {subkey_name}")
                            continue
            except (FileNotFoundError, PermissionError):
                print("optimize_registry: Policies key not accessible")
                pass
            try:
                subprocess.run(
                    ["reg", "delete", r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSaveMRU",
                     "/f"], check=False)
                deleted_count += 1
                print("optimize_registry: Cleared OpenSaveMRU")
            except subprocess.CalledProcessError:
                print("optimize_registry: Failed to clear OpenSaveMRU")
                pass
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace", 0,
                                    winreg.KEY_ALL_ACCESS) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            winreg.DeleteKey(key, subkey_name)
                            deleted_count += 1
                            print(f"optimize_registry: Deleted NameSpace entry {subkey_name}")
                        except (WindowsError, PermissionError):
                            print(f"optimize_registry: Failed to delete NameSpace entry {subkey_name}")
                            continue
            except (FileNotFoundError, PermissionError):
                print("optimize_registry: NameSpace key not accessible")
                pass
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"*\shellex\ContextMenuHandlers", 0,
                                    winreg.KEY_ALL_ACCESS) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name, 0, winreg.KEY_ALL_ACCESS) as sub_key:
                                try:
                                    winreg.DeleteKey(key, subkey_name)
                                    deleted_count += 1
                                    print(f"optimize_registry: Deleted ContextMenuHandler {subkey_name}")
                                except (WindowsError, PermissionError):
                                    print(f"optimize_registry: Failed to delete ContextMenuHandler {subkey_name}")
                                    continue
                        except (WindowsError, PermissionError):
                            print(f"optimize_registry: Failed to enumerate ContextMenuHandlers")
                            pass
            except (FileNotFoundError, PermissionError):
                print("optimize_registry: ContextMenuHandlers key not accessible")
                pass
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"", 0, winreg.KEY_ALL_ACCESS) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            if subkey_name.startswith(".") and subkey_name.endswith(".invalid"):
                                winreg.DeleteKey(key, subkey_name)
                                deleted_count += 1
                                print(f"optimize_registry: Deleted invalid extension {subkey_name}")
                        except (WindowsError, PermissionError):
                            print(f"optimize_registry: Failed to delete invalid extension {subkey_name}")
                            continue
            except (FileNotFoundError, PermissionError):
                print("optimize_registry: Root key not accessible")
                pass
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0,
                                    winreg.KEY_ALL_ACCESS) as key:
                    try:
                        winreg.DeleteValue(key, "CachedWallpaper")
                        deleted_count += 1
                        print("optimize_registry: Cleared CachedWallpaper")
                    except (FileNotFoundError, PermissionError):
                        print("optimize_registry: Failed to clear CachedWallpaper")
            except (FileNotFoundError, PermissionError):
                print("optimize_registry: Desktop key not accessible")
                pass
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class", 0,
                                    winreg.KEY_ALL_ACCESS) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name, 0, winreg.KEY_ALL_ACCESS) as sub_key:
                                try:
                                    winreg.DeleteKey(key, subkey_name)
                                    deleted_count += 1
                                    print(f"optimize_registry: Deleted Class entry {subkey_name}")
                                except (WindowsError, PermissionError):
                                    print(f"optimize_registry: Failed to delete Class entry {subkey_name}")
                                    continue
                        except (WindowsError, PermissionError):
                            print(f"optimize_registry: Failed to enumerate Class entries")
                            pass
            except (FileNotFoundError, PermissionError):
                print("optimize_registry: Class key not accessible")
                pass
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0,
                                    winreg.KEY_ALL_ACCESS) as key:
                    try:
                        winreg.DeleteValue(key, "NoAutoRun")
                        deleted_count += 1
                        print("optimize_registry: Cleared NoAutoRun")
                    except (FileNotFoundError, PermissionError):
                        print("optimize_registry: Failed to clear NoAutoRun")
            except (FileNotFoundError, PermissionError):
                print("optimize_registry: Explorer Policies key not accessible")
                pass
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies", 0, winreg.KEY_ALL_ACCESS) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            if subkey_name in ["Microsoft\Windows"]:
                                continue
                            winreg.DeleteKey(key, subkey_name)
                            deleted_count += 1
                            print(f"optimize_registry: Deleted policy {subkey_name}")
                        except (WindowsError, PermissionError):
                            print(f"optimize_registry: Failed to delete policy {subkey_name}")
                            continue
            except (FileNotFoundError, PermissionError):
                print("optimize_registry: Policies key not accessible")
                pass
            if deleted_count > 0:
                print(f"optimize_registry: Completed with {deleted_count} deletions")
                return (True,
                        f"Registry optimized: {deleted_count} invalid entries removed. Backups saved to {backup_dir}")
            else:
                print("optimize_registry: No deletions performed")
                return (True, f"No invalid registry entries found. Backups saved to {backup_dir}")
        except PermissionError:
            print("optimize_registry: Permission denied, skipping")
            return (False, "Skipped: Insufficient permissions. Run as Administrator.")
        except subprocess.CalledProcessError:
            print("optimize_registry: Backup process failed")
            return (False, "Skipped: Failed to create registry backup. Run as Administrator.")
        except Exception as e:
            print(f"optimize_registry: Unexpected error: {str(e)}")
            return (False, "Skipped: An unexpected error occurred. Run as Administrator.")

    @staticmethod
    def disable_search_index():
        try:
            subprocess.run(["sc", "stop", "WSearch"], shell=True)
            subprocess.run(["sc", "config", "WSearch", "start=", "disabled"], shell=True)
            subprocess.run(["taskkill", "/f", "/im", "SearchIndexer.exe"], shell=True)
            subprocess.run(["taskkill", "/f", "/im", "SearchUI.exe"], shell=True)
            subprocess.run(["taskkill", "/f", "/im", "SearchApp.exe"], shell=True)

            index_path = os.path.join(os.environ["ProgramData"], "Microsoft", "Search", "Data")
            if os.path.exists(index_path):
                subprocess.run(f'rmdir /s /q "{index_path}"', shell=True)

            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search", 0,
                                    winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "BingSearchEnabled", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(key, "AllowCortana", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(key, "CortanaConsent", 0, winreg.REG_DWORD, 0)
            except:
                pass

            return True, "Disabled successfully"

        except Exception as e:
            return False, f"Failed with error - {e}"

    @staticmethod
    def enable_classic_right_click():
        print("enable_classic_right_click: Starting")
        try:
            key_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
            with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
                print("enable_classic_right_click: Set registry value")
            subprocess.run("taskkill /f /im explorer.exe", shell=True)
            print("enable_classic_right_click: Killed explorer.exe")
            subprocess.run("start explorer", shell=True)
            print("enable_classic_right_click: Restarted explorer.exe")
            return (True, "Classic right-click enabled successfully")
        except PermissionError:
            print("enable_classic_right_click: Permission denied")
            return (False, "Skipped: Insufficient permissions. Run as Administrator.")
        except Exception as e:
            print(f"enable_classic_right_click: Error: {str(e)}")
            return (False, "Skipped: Failed to enable classic right-click. Run as Administrator.")

    @staticmethod
    def run_windows_utility():
        try:
            command = 'powershell -Command "irm https://christitus.com/win | iex"'
            subprocess.run(command, shell=True, check=True)
            print("✅ Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to run script: {e}")

    @staticmethod
    def clean_temporary_files():
        paths_to_clean = [
            tempfile.gettempdir(),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Prefetch'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'SoftwareDistribution', 'Download')
        ]

        cleaned_paths = []
        failed_paths = []

        for path in paths_to_clean:
            if not os.path.exists(path):
                continue

            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        cleaned_paths.append(file_path)
                    except Exception:
                        failed_paths.append(file_path)

                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        shutil.rmtree(dir_path, ignore_errors=True)
                        cleaned_paths.append(dir_path)
                    except Exception:
                        failed_paths.append(dir_path)

        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x00000001)
        except Exception:
            failed_paths.append("Recycle Bin")

        if not failed_paths:
            return (True, "System cleanup completed successfully.")
        else:
            error_message = "Some temporary files or directories could not be cleaned."
            if failed_paths:
                error_message += f" Failed paths: {', '.join(failed_paths)}."
            return (False, "System cleanup completed successfully.")

    @staticmethod
    def empty_recycle_bin():
        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x00000007)
            print("Recycle Bin emptied.")
            return (True, "Recycle Bin emptied successfully.")
        except Exception as e:
            error_message = f"Failed to empty Recycle Bin: {e}"
            print(error_message)
            return (False, error_message)

    @staticmethod
    def disable_background_apps():
        try:
            import subprocess
            subprocess.run(
                'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f',
                check=True, shell=True
            )
            subprocess.run(
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppPrivacy" /v LetAppsRunInBackground /t REG_DWORD /d 2 /f',
                check=True, shell=True
            )
            return (True, "Background apps disabled.")
        except Exception as e:
            return (False, f"Failed to disable background apps: {e}")

    @staticmethod
    def disable_windows_update():
        try:
            subprocess.run('sc config wuauserv start= disabled', check=True, shell=True)
            subprocess.run(
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAutoUpdate /t REG_DWORD /d 1 /f',
                check=True, shell=True)
            subprocess.run(
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v DisableOSUpgrade /t REG_DWORD /d 1 /f',
                check=True, shell=True)
            subprocess.run(
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate" /v ExcludeWUDriversInQualityUpdate /t REG_DWORD /d 1 /f',
                check=True, shell=True)

            try:
                subprocess.run('sc stop wuauserv', check=True, shell=True)
            except subprocess.CalledProcessError as stop_err:
                if "1062" not in str(stop_err):
                    raise stop_err

            return (True, "Windows Update disabled.")
        except Exception as e:
            return (False, f"Failed to disable Windows Update: {e}")

    @staticmethod
    def clean_all_browser_caches():
        browser_paths = {
            "Chrome": os.path.join(os.getenv("LOCALAPPDATA", ""), "Google", "Chrome", "User Data"),
            "Edge": os.path.join(os.getenv("LOCALAPPDATA", ""), "Microsoft", "Edge", "User Data"),
            "Firefox": os.path.join(os.getenv("APPDATA", ""), "Mozilla", "Firefox", "Profiles"),
            "Brave": os.path.join(os.getenv("LOCALAPPDATA", ""), "BraveSoftware", "Brave-Browser", "User Data"),
            "Opera": os.path.join(os.getenv("APPDATA", ""), "Opera Software", "Opera Stable"),
            "Opera GX": os.path.join(os.getenv("APPDATA", ""), "Opera Software", "Opera GX Stable"),
            "Vivaldi": os.path.join(os.getenv("LOCALAPPDATA", ""), "Vivaldi", "User Data"),
            "Maxthon": os.path.join(os.getenv("APPDATA", ""), "Maxthon5", "Users"),
            "Yandex": os.path.join(os.getenv("LOCALAPPDATA", ""), "Yandex", "YandexBrowser", "User Data"),
            "Comodo Dragon": os.path.join(os.getenv("LOCALAPPDATA", ""), "Comodo", "Dragon", "User Data"),
            "SRWare Iron": os.path.join(os.getenv("LOCALAPPDATA", ""), "Chromium", "User Data"),
            "Torch": os.path.join(os.getenv("LOCALAPPDATA", ""), "Torch", "User Data"),
            "Epic": os.path.join(os.getenv("LOCALAPPDATA", ""), "Epic Privacy Browser", "User Data"),
            "Waterfox": os.path.join(os.getenv("APPDATA", ""), "Waterfox", "Profiles"),
            "Slimjet": os.path.join(os.getenv("LOCALAPPDATA", ""), "Slimjet", "User Data"),
            "Cent Browser": os.path.join(os.getenv("LOCALAPPDATA", ""), "CentBrowser", "User Data"),
            "Pale Moon": os.path.join(os.getenv("APPDATA", ""), "Moonchild Productions", "Pale Moon", "Profiles"),
            "SeaMonkey": os.path.join(os.getenv("APPDATA", ""), "Mozilla", "SeaMonkey", "Profiles"),
            "Avant": os.path.join(os.getenv("APPDATA", ""), "Avant Profiles"),
            "UC Browser": os.path.join(os.getenv("LOCALAPPDATA", ""), "UCBrowser", "User Data")
        }

        cleaned_browsers = []
        failed_browsers = []

        for browser, path in browser_paths.items():
            if not os.path.exists(path):
                continue

            if browser in ["Firefox", "Waterfox", "SeaMonkey", "Pale Moon"]:
                for profile in Path(path).glob("*"):
                    cache = profile / "cache2"
                    if cache.exists():
                        try:
                            shutil.rmtree(cache, ignore_errors=True)
                            cleaned_browsers.append(browser)
                        except Exception:
                            failed_browsers.append(browser)
            else:
                for root, dirs, _ in os.walk(path):
                    if "Cache" in dirs:
                        cache_path = os.path.join(root, "Cache")
                        try:
                            shutil.rmtree(cache_path, ignore_errors=True)
                            cleaned_browsers.append(browser)
                        except Exception:
                            failed_browsers.append(browser)

        if not failed_browsers:
            return (True, "All browser caches cleaned successfully.")
        else:
            error_message = "Some browser caches could not be cleaned."
            if failed_browsers:
                error_message += f" Failed browsers: {', '.join(set(failed_browsers))}."
            return (False, error_message)

    @staticmethod
    def clean_all_logs():
        logs = [
            "Application",
            "Security",
            "Setup",
            "System",
            "ForwardedEvents",
            "Windows PowerShell",
            "Microsoft-Windows-DNS-Client/Operational",
            "Microsoft-Windows-Windows Defender/Operational",
            "Microsoft-Windows-WindowsUpdateClient/Operational",
            "Microsoft-Windows-CertificateServicesClient-Lifecycle-System/Operational",
            "Microsoft-Windows-TerminalServices-LocalSessionManager/Operational",
            "Microsoft-Windows-TaskScheduler/Operational",
            "Microsoft-Windows-GroupPolicy/Operational"
        ]
        cleared_logs = []
        failed_logs = []

        for log in logs:
            try:
                subprocess.run(["wevtutil", "clear-log", log], check=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
                cleared_logs.append(log)
            except subprocess.CalledProcessError:
                failed_logs.append(log)

        paths = [
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Logs'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32', 'LogFiles'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Logs', 'CBS'),
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'WindowsUpdate.log')
        ]
        deleted_files = []
        failed_files = []

        for path in paths:
            if os.path.isfile(path):
                try:
                    os.remove(path)
                    deleted_files.append(path)
                except Exception:
                    failed_files.append(path)
            elif os.path.isdir(path):
                try:
                    shutil.rmtree(path, ignore_errors=True)
                    deleted_files.append(path)
                except Exception:
                    failed_files.append(path)

        if not failed_logs and not failed_files:
            return (True, "All logs and related files cleaned successfully.")
        else:
            error_message = "Some logs or files could not be cleaned."
            if failed_logs:
                error_message += f" Failed logs: {', '.join(failed_logs)}."
            if failed_files:
                error_message += f" Failed files: {', '.join(failed_files)}."
            return (False, error_message)

    @staticmethod
    def run_disk_cleanup():
        try:
            subprocess.run(["cleanmgr.exe", "/sagerun:1"], check=True)
            print("Disk Cleanup ran successfully.")
            return (True, "Disk Cleanup ran successfully.")
        except subprocess.CalledProcessError as e:
            error_message = f"Failed to run Disk Cleanup. Error: {e.stderr}"
            print(error_message)
            return (False, error_message)
        except Exception as e:
            error_message = f"An unexpected error occurred while running Disk Cleanup: {e}"
            print(error_message)
            return (False, error_message)

    @staticmethod
    def run_debloat_utility():
        try:
            command = 'powershell -NoProfile -ExecutionPolicy Bypass -Command & ([scriptblock]::Create((irm "https://debloat.raphi.re/")))'
            result = subprocess.run(command, check=True, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return (True, "Debloat utility ran successfully.")
            else:
                return (False, f"Debloat utility failed with exit code {result.returncode}.")
        except subprocess.CalledProcessError as e:
            return (False, f"Failed to run debloat utility. Error: {e.stderr}")
        except Exception as e:
            return (False, f"An unexpected error occurred: {e}")

    @staticmethod
    def optimize_dns():
        try:
            dns_servers = [("8.8.8.8"), ("1.1.1.1"), ("9.9.9.9")]
            min_latency = float('inf')
            fastest_dns = None
            resolver = dns.resolver.Resolver()
            for ip in dns_servers:
                resolver.nameservers = [ip]
                start = time.perf_counter()
                resolver.resolve("example.com", 'A', lifetime=2)
                latency = time.perf_counter() - start
                if latency < min_latency:
                    min_latency = latency
                    fastest_dns = ip
            if fastest_dns:
                subprocess.run(f"netsh interface ip set dns name=\"Ethernet\" source=static addr={fastest_dns}",
                               shell=True, check=True, timeout=5)
                return (True, f"DNS set to {fastest_dns}")
            return (False, "No DNS server selected")
        except Exception as e:
            return (False, f"DNS optimization failed: {e}")

    @staticmethod
    def disable_metered_connection():
        import subprocess
        try:
            subprocess.run('powershell -Command "Set-NetConnectionProfile -NetworkCategory Private"', shell=True,
                           check=True, timeout=5)
            return (True, "Metered connection disabled")
        except Exception as e:
            return (False, f"Failed to disable metered connection: {e}")

    @staticmethod
    def flush_dns_cache():
        import subprocess
        try:
            subprocess.run("ipconfig /flushdns", shell=True, check=True, timeout=5)
            subprocess.run("net stop dnscache", shell=True, check=True, timeout=5)
            subprocess.run("net start dnscache", shell=True, check=True, timeout=5)
            return (True, "DNS cache flushed and service restarted")
        except Exception as e:
            return (False, f"Failed to flush DNS cache: {e}")

    @staticmethod
    def optimize_network_adapters():
        import subprocess
        try:
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Energy-Efficient Ethernet\' -DisplayValue \'Disabled\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Flow Control\' -DisplayValue \'Disabled\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Interrupt Moderation\' -DisplayValue \'Disabled\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Jumbo Packet\' -DisplayValue \'9014 Bytes\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Receive Buffers\' -DisplayValue \'8192\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Transmit Buffers\' -DisplayValue \'8192\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Adaptive Inter-Frame Spacing\' -DisplayValue \'Disabled\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Priority & VLAN\' -DisplayValue \'Disabled\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Enable-NetAdapterChecksumOffload -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run('powershell -Command "Get-NetAdapter | Enable-NetAdapterLso -ErrorAction SilentlyContinue"',
                           shell=True, check=True, timeout=10)
            subprocess.run('powershell -Command "Get-NetAdapter | Enable-NetAdapterRsc -ErrorAction SilentlyContinue"',
                           shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Disable-NetAdapterPowerManagement -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run('netsh int tcp set global autotuninglevel=disabled', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global rss=enabled', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global congestionprovider=ctcp', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global ecncapability=enabled', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global dca=enabled', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global netdma=enabled', shell=True, check=True, timeout=5)
            subprocess.run('netsh int ip set global taskoffload=enabled', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global chimney=enabled', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global maxsynretransmissions=2', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global nonsackrttresiliency=disabled', shell=True, check=True, timeout=5)
            subprocess.run(
                'powershell -Command "Set-NetTCPSetting -SettingName InternetCustom -MinRto 200 -InitialCongestionWindow 10"',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'powershell -Command "Set-NetTCPSetting -SettingName InternetCustom -MaxSynRetransmissions 2"',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'powershell -Command "Set-NetTCPSetting -SettingName InternetCustom -CongestionAlgorithm CTCP"',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetIPInterface -InterfaceMetric 1 -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run('netsh interface ipv4 set subinterface "Ethernet" mtu=1500 store=persistent', shell=True,
                           check=True, timeout=5)
            subprocess.run('powershell -Command "Set-NetOffloadGlobalSetting -PacketCoalescingFilter Disabled"',
                           shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpMaxDataRetransmissions /t REG_DWORD /d 3 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v DisableTaskOffload /t REG_DWORD /d 0 /f',
                shell=True, check=True, timeout=5)
            return (True, "Network adapters pushed to extreme performance")
        except Exception as e:
            return (False, f"Failed to optimize network adapters: {e}")

    @staticmethod
    def enable_tcp_fast_open():
        import subprocess
        try:
            subprocess.run('netsh int tcp set global fastopen=enabled', shell=True, check=True, timeout=5)
            subprocess.run('powershell -Command "Set-NetTCPSetting -SettingName InternetCustom -FastOpen Enabled"',
                           shell=True, check=True, timeout=5)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Receive Buffers\' -DisplayValue \'16384\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Transmit Buffers\' -DisplayValue \'16384\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Interrupt Moderation\' -DisplayValue \'Disabled\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Enable-NetAdapterChecksumOffload -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run('powershell -Command "Get-NetAdapter | Enable-NetAdapterLso -ErrorAction SilentlyContinue"',
                           shell=True, check=True, timeout=10)
            subprocess.run('powershell -Command "Get-NetAdapter | Enable-NetAdapterRsc -ErrorAction SilentlyContinue"',
                           shell=True, check=True, timeout=10)
            subprocess.run('netsh int tcp set global autotuninglevel=disabled', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global congestionprovider=ctcp', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global ecncapability=enabled', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global maxsynretransmissions=2', shell=True, check=True, timeout=5)
            subprocess.run(
                'powershell -Command "Set-NetTCPSetting -SettingName InternetCustom -MinRto 150 -InitialCongestionWindow 12"',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v Tcp1323Opts /t REG_DWORD /d 3 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpMaxDataRetransmissions /t REG_DWORD /d 2 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpFinWait2Delay /t REG_DWORD /d 30 /f',
                shell=True, check=True, timeout=5)
            return (True, "TCP Fast Open enabled with aggressive optimizations")
        except Exception as e:
            return (False, f"Failed to enable TCP Fast Open: {e}")

    @staticmethod
    def disable_ipv6():
        import subprocess
        try:
            subprocess.run(
                'powershell -Command "Disable-NetAdapterBinding -Name * -ComponentID ms_tcpip6 -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip6\\Parameters" /v DisabledComponents /t REG_DWORD /d 0xFF /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Receive Buffers\' -DisplayValue \'16384\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Transmit Buffers\' -DisplayValue \'16384\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Interrupt Moderation\' -DisplayValue \'Disabled\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Flow Control\' -DisplayValue \'Disabled\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Enable-NetAdapterChecksumOffload -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run('powershell -Command "Get-NetAdapter | Enable-NetAdapterLso -ErrorAction SilentlyContinue"',
                           shell=True, check=True, timeout=10)
            subprocess.run('netsh int tcp set global autotuninglevel=disabled', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global rss=enabled', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global congestionprovider=ctcp', shell=True, check=True, timeout=5)
            subprocess.run('netsh int tcp set global maxsynretransmissions=2', shell=True, check=True, timeout=5)
            subprocess.run(
                'powershell -Command "Set-NetTCPSetting -SettingName InternetCustom -MinRto 150 -InitialCongestionWindow 12"',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v Tcp1323Opts /t REG_DWORD /d 3 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpMaxDataRetransmissions /t REG_DWORD /d 2 /f',
                shell=True, check=True, timeout=5)
            return (True, "IPv6 disabled with aggressive IPv4 optimizations")
        except Exception as e:
            return (False, f"Failed to disable IPv6: {e}")

    @staticmethod
    def clear_ms_store_cache():
        import subprocess
        try:
            subprocess.run("wsreset.exe", shell=True, check=True, timeout=10)
            return (True, "Microsoft Store cache cleared")
        except Exception as e:
            return (False, f"Failed to clear Microsoft Store cache: {e}")

    @staticmethod
    def disable_firewall():
        import subprocess
        try:
            subprocess.run('netsh advfirewall set allprofiles state off', shell=True, check=True, timeout=5)
            return (True, "Windows Firewall disabled")
        except Exception as e:
            return (False, f"Failed to disable Windows Firewall: {e}")

    @staticmethod
    def clear_event_logs():
        import subprocess
        try:
            subprocess.run(
                'powershell -Command "wevtutil enum-logs | ForEach-Object { wevtutil cl $_ }" -ErrorAction SilentlyContinue',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-WinEvent -ListLog * -ErrorAction SilentlyContinue | Where-Object { $_.IsEnabled } | ForEach-Object { Clear-EventLog -LogName $_.LogName -ErrorAction SilentlyContinue }"',
                shell=True, check=True, timeout=10)
            return (True, "Event logs cleared successfully")
        except Exception as e:
            return (False, f"Failed to clear event logs: {e}")

    @staticmethod
    def optimize_cpu_performance():
        import subprocess
        try:
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v DisablePagingExecutive /t REG_DWORD /d 1 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v LargeSystemCache /t REG_DWORD /d 1 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power" /v CsEnabled /t REG_DWORD /d 0 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power" /v HibernateEnabled /t REG_DWORD /d 0 /f',
                shell=True, check=True, timeout=5)
            subprocess.run('bcdedit /set disabledynamictick yes', shell=True, check=True, timeout=5)
            subprocess.run('bcdedit /set useplatformtick yes', shell=True, check=True, timeout=5)
            subprocess.run(
                'powershell -Command "Get-Process -Name System | ForEach-Object { $_.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::High }" -ErrorAction SilentlyContinue',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl" /v Win32PrioritySeparation /t REG_DWORD /d 38 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\intelppm\\Parameters" /v ThreadDpcEnable /t REG_DWORD /d 0 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel" /v DistributeTimers /t REG_DWORD /d 1 /f',
                shell=True, check=True, timeout=5)
            return (True, "CPU performance optimized")
        except Exception as e:
            return (False, f"Failed to optimize CPU performance: {e}")

    @staticmethod
    def disable_automatic_restart():
        import subprocess
        try:
            subprocess.run(
                'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update" /v AUOptions /t REG_DWORD /d 1 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\SystemRestore" /v DisableSR /t REG_DWORD /d 1 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAutoRebootWithLoggedOnUsers /t REG_DWORD /d 1 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\CrashControl" /v AutoReboot /t REG_DWORD /d 0 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'powershell -Command "Set-ItemProperty -Path \'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\' -Name \'SetAutoRestart\' -Value 0 -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=5)
            subprocess.run('sc config wuauserv start= disabled', shell=True, check=True, timeout=5)
            return (True, "Automatic restarts disabled")
        except Exception as e:
            return (False, f"Failed to disable automatic restarts: {e}")

    @staticmethod
    def disable_sleep_mode():
        import subprocess
        try:
            subprocess.run('powercfg -change -standby-timeout-ac 0', shell=True, check=True, timeout=5)
            subprocess.run('powercfg -change -standby-timeout-dc 0', shell=True, check=True, timeout=5)
            subprocess.run('powercfg -change -hibernate-timeout-ac 0', shell=True, check=True, timeout=5)
            subprocess.run('powercfg -change -hibernate-timeout-dc 0', shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power" /v HibernateEnabled /t REG_DWORD /d 0 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings\\238C9FA8-0AAD-41ED-83F4-97BE242C8F20\\7bc4a2f9-d8fc-4469-b07b-33eb785aaca0" /v DefaultPowerSchemeValues /t REG_DWORD /d 0 /f',
                shell=True, check=True, timeout=5)
            subprocess.run('powercfg -setactive SCHEME_MIN', shell=True, check=True, timeout=5)
            return (True, "Sleep mode disabled")
        except Exception as e:
            return (False, f"Failed to disable sleep mode: {e}")

    @staticmethod
    def disable_windows_defender():
        try:
            subprocess.run(
                'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v AllowFastServiceStartup /t REG_DWORD /d 0 /f',
                shell=True, check=True, timeout=5)
            subprocess.run('sc config WinDefend start= disabled', shell=True, check=True, timeout=5)
            return (True, "Windows Defender disabled")
        except Exception as e:
            return (False, f"Failed to disable Windows Defender: {e}")

    @staticmethod
    def optimize_gaming():
        try:
            # Apply CPU performance optimizations
            AstreisFunc.optimize_cpu_performance()

            # Gaming-specific registry tweaks
            subprocess.run(
                'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v SystemResponsiveness /t REG_DWORD /d 0 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v Priority /t REG_DWORD /d 6 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v SFIO Priority /t REG_SZ /d High /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games" /v Scheduling Category /t REG_SZ /d High /f',
                shell=True, check=True, timeout=5)

            # Optimize graphics drivers
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f',
                shell=True, check=True, timeout=5)

            # Disable unnecessary services for gaming
            AstreisFunc.optimize_services()

            # Apply power plan optimizations
            AstreisFunc.optimize_astreis_power_plan()

            # Disable background apps
            AstreisFunc.disable_background_apps()

            # Optimize network for lower latency
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Interrupt Moderation\' -DisplayValue \'Disabled\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)

            return (True, "Gaming optimizations applied successfully with maximum performance tweaks")
        except Exception as e:
            return (False, f"Failed to apply gaming optimizations: {e}")

    @staticmethod
    def run_boost_pc_pack():
        try:
            # Apply CPU optimizations
            AstreisFunc.optimize_cpu_performance()

            # Apply power plan optimizations
            AstreisFunc.optimize_astreis_power_plan()

            # Disable unnecessary services
            AstreisFunc.optimize_services()

            # Clean temporary files
            AstreisFunc.clean_temporary_files()

            # Optimize registry
            AstreisFunc.optimize_registry()

            # Run system file checker and DISM
            subprocess.run('sfc /scannow', shell=True, check=True, timeout=600)
            subprocess.run('DISM /Online /Cleanup-Image /RestoreHealth', shell=True, check=True, timeout=600)

            # Disable Windows Defender for maximum performance
            AstreisFunc.disable_windows_defender()

            # Optimize appearance
            AstreisFunc.optimize_appearance()

            # Disable automatic restarts
            AstreisFunc.disable_automatic_restart()

            return (True, "PC boost pack executed successfully with comprehensive optimizations")
        except Exception as e:
            return (False, f"Failed to execute PC boost pack: {e}")

    @staticmethod
    def run_reduce_ping_pack():
        try:
            # Apply network adapter optimizations
            AstreisFunc.optimize_network_adapters()

            # Enable TCP fast open
            AstreisFunc.enable_tcp_fast_open()

            # Flush DNS cache
            AstreisFunc.flush_dns_cache()

            # Optimize DNS
            AstreisFunc.optimize_dns()

            # Disable IPv6 for better IPv4 performance
            AstreisFunc.disable_ipv6()

            # Additional TCP optimizations
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpFinWait2Delay /t REG_DWORD /d 20 /f',
                shell=True, check=True, timeout=5)
            subprocess.run(
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters" /v TcpTimedWaitDelay /t REG_DWORD /d 30 /f',
                shell=True, check=True, timeout=5)

            # Optimize network buffers
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Receive Buffers\' -DisplayValue \'32768\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)
            subprocess.run(
                'powershell -Command "Get-NetAdapter | Set-NetAdapterAdvancedProperty -Name * -DisplayName \'Transmit Buffers\' -DisplayValue \'32768\' -ErrorAction SilentlyContinue"',
                shell=True, check=True, timeout=10)

            return (True, "Ping reduction pack applied successfully with aggressive network tweaks")
        except Exception as e:
            return (False, f"Failed to apply ping reduction pack: {e}")

    @staticmethod
    def clean_windows():
        try:
            # Clean temporary files
            AstreisFunc.clean_temporary_files()

            # Empty recycle bin
            AstreisFunc.empty_recycle_bin()

            # Clean all browser caches
            AstreisFunc.clean_all_browser_caches()

            # Clear event logs
            AstreisFunc.clear_event_logs()

            # Clear Microsoft Store cache
            AstreisFunc.clear_ms_store_cache()

            # Run disk cleanup
            AstreisFunc.run_disk_cleanup()

            # Run debloat utility
            AstreisFunc.run_debloat_utility()

            # Clean logs
            AstreisFunc.clean_all_logs()

            # Additional cleanup: clear Windows Update cache
            subprocess.run('net stop wuauserv', shell=True, check=True, timeout=5)
            update_path = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'SoftwareDistribution')
            if os.path.exists(update_path):
                shutil.rmtree(update_path, ignore_errors=True)
            subprocess.run('net start wuauserv', shell=True, check=True, timeout=5)

            return (True, "Windows cleaned successfully with comprehensive cleanup")
        except Exception as e:
            return (False, f"Failed to clean Windows: {e}")

    @staticmethod
    def placeholder():
        pass

    @staticmethod
    def placeholder():
        print("Ran Functioion - Placeholder")
        pass
