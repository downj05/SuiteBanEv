import winreg
import os
import vdf
from typing import Optional
import subprocess

UNTURNED_APP_ID = 304930


def set_registry_value(key, key_path, value_name, value) -> bool:
    try:
        key = winreg.CreateKey(key, key_path)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error setting {value_name}: {str(e)}")
        return False


def get_registry_value(key, key_path, value_name) -> Optional[str]:
    try:
        key = winreg.OpenKey(key, key_path)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        return value
    except Exception as e:
        print(f"Error reading {value_name}: {str(e)}")
        return None


def get_steam_path() -> Optional[str]:
    key_path = r"SOFTWARE\Valve\Steam"
    value_name = "SteamPath"
    return get_registry_value(winreg.HKEY_CURRENT_USER, key_path, value_name)


def get_steam_drive():
    steam_path = get_steam_path()
    if steam_path is None:
        print("Error: Steam not found in registry")
        print("This likely means Steam is not installed on this machine, which is required to run this program!")
        exit(1)
    else:
        return steam_path.split(":")[0].upper()


def get_steam_library():
    vdf_path = os.path.join(get_steam_path(), "steamapps", "libraryfolders.vdf")
    with open(vdf_path, "r") as f:
        libraries = vdf.loads(f.read(), mapper=vdf.VDFDict)["libraryfolders"]
    return libraries


def get_unturned_library():
    libraries = get_steam_library()
    for key, value in libraries.items():
        path = value["path"]
        for app in value["apps"]:
            if app == str(UNTURNED_APP_ID):
                return path
    print("Error: Unturned not found in Steam libraries")


def get_unturned_path() -> str:
    return os.path.join(get_unturned_library(), "steamapps", "common", "Unturned")


def get_unturned_drive() -> Optional[str]:
    return get_unturned_library().split(":")[0].upper()


def start_unturned(*args, parent=None):
    unturned_path = get_unturned_path()
    if not os.path.exists(unturned_path):
        print(f"Error: Unturned not found at {unturned_path}")
        print("This likely means Unturned is not installed on this machine, which is required to run this program!")
        exit(1)
    else:
        # Run and pass args
        subprocess.Popen([os.path.join(unturned_path, "Unturned_BE.exe")] + list(args))


if __name__ == "__main__":
    print(get_unturned_path())
