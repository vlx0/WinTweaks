import ctypes
import subprocess
import winreg

HKCU = winreg.HKEY_CURRENT_USER
HKLM = winreg.HKEY_LOCAL_MACHINE


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def read_value(hive, path, name):
    try:
        with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except (FileNotFoundError, OSError):
        return None


def write_value(hive, path, name, value, value_type):
    with winreg.CreateKeyEx(hive, path, 0, winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, name, 0, value_type, value)


def delete_value(hive, path, name):
    try:
        with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
    except (FileNotFoundError, OSError):
        pass


def restart_explorer():
    subprocess.run(["taskkill", "/f", "/im", "explorer.exe"],
                   capture_output=True, shell=False)
    subprocess.Popen(["explorer.exe"], shell=False)