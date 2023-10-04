import winreg
import os
import vdf

UNTURNED_APP_ID = 304930


def set_registry_value(key_path, value_name, value):
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)
        print(f"Successfully set {value_name} to {value}")
    except Exception as e:
        print(f"Error setting {value_name}: {str(e)}")


def get_registry_value(key_path, value_name):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        return value
    except Exception as e:
        print(f"Error reading {value_name}: {str(e)}")
        return None


def get_steam_path():
    key_path = "SOFTWARE\Valve\Steam"
    value_name = "SteamPath"
    return get_registry_value(key_path, value_name)


def get_steam_drive():
    return get_steam_path().split(":")[0].upper()


def get_steam_library():
    vdf_path = os.path.join(get_steam_path(), "steamapps", "libraryfolders.vdf")
    with open(vdf_path, "r") as f:
        libraries = vdf.loads(f.read(), mapper=vdf.VDFDict)["libraryfolders"]
    return libraries


def get_unturned_drive() -> str:
    libraries = get_steam_library()
    for key, value in libraries.items():
        path = value["path"]
        for app in value["apps"]:
            if app == str(UNTURNED_APP_ID):
                return path.split(":")[0].upper()
    print("Error: Unturned not found in Steam libraries")
    return None
