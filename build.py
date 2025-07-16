import PyInstaller.__main__
import shutil
import os
import stat
import sys
import multiprocessing
import socket

# Define the name of the application
app_name = "Astreis"

def on_rm_error(func, path, exc_info):
    """
    Error handler for shutil.rmtree.
    If the error is a PermissionError, it attempts to change the file's
    permissions and then retry the deletion.
    """
    if issubclass(exc_info[0], PermissionError):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        raise

def check_single_instance(port=65432):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        return True  # This is the only instance
    except socket.error:
        return False  # Another instance is running

def build():
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist', onerror=on_rm_error)
    if os.path.exists('build'):
        shutil.rmtree('build', onerror=on_rm_error)
    if os.path.exists(f'{app_name}.spec'):
        os.remove(f'{app_name}.spec')

    # Platform-specific separator for PyInstaller --add-data
    sep = ';' if sys.platform.startswith('win') else ':'

    # PyInstaller arguments
    pyinstaller_args = [
        'main.py',
        '--noconfirm',
        '--onedir',
        '--windowed',
        f'--name={app_name}',
        f'--icon=icon.ico',
        f'--add-data=AstreisFunc{sep}AstreisFunc',
        f'--add-data=gui{sep}gui',
        f'--add-data=icon.ico{sep}.',
        f'--add-data=settings.json{sep}.',
        f'--add-data=config{sep}config',  # Include config directory
        f'--add-data=gui/themes{sep}gui/themes',  # Include themes
        f'--add-data=gui/images{sep}gui/images',  # Include images
        '--hidden-import=win32com.shell',
    ]

    # Run PyInstaller
    PyInstaller.__main__.run(pyinstaller_args)

    print(f"\n\nBuild complete. Executable is in the 'dist/{app_name}' folder.")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    if not check_single_instance():
        print("Another instance is already running.")
        exit(0)
    build()