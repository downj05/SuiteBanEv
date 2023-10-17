import drive_helpers
import os
import subprocess
import hashlib
import uuid
import winreg
import json
from colorama import Fore, Back, Style
from typing import Optional, Union

# Salt Unturned uses for HWID
SALT = "Zpsz+h>nJ!?4h2&nVPVw=DmG"


def set_player_prefs(val) -> bool:
    return drive_helpers.set_registry_value(
        winreg.HKEY_CURRENT_USER,
        r"Software\Smartly Dressed Games\Unturned",
        "CloudStorageHash_h1878083263",
        val,
    )


def get_player_prefs() -> str:
    return drive_helpers.get_registry_value(
        winreg.HKEY_CURRENT_USER,
        r"Software\Smartly Dressed Games\Unturned",
        "CloudStorageHash_h1878083263",
    )


def set_convenient_save_data(val) -> bool:
    try:
        with open(
            os.path.join(
                drive_helpers.get_unturned_path(), "Cloud", "ConvenientSavedata.json"
            ),
            "r",
        ) as f:
            data = json.load(f)
        data["Strings"]["ItemStoreCache"] = val
        with open(
            os.path.join(
                drive_helpers.get_unturned_path(), "Cloud", "ConvenientSavedata.json"
            ),
            "w",
        ) as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error setting convenient save data: {str(e)}")
        return False


def get_convenient_save_data() -> str:
    with open(
        os.path.join(
            drive_helpers.get_unturned_path(), "Cloud", "ConvenientSavedata.json"
        ),
        "r",
    ) as f:
        return json.load(f)["Strings"]["ItemStoreCache"]
    pass


def set_windows_guid(val) -> bool:
    return drive_helpers.set_registry_value(
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Cryptography",
        "MachineGuid",
        val,
    )


def get_windows_guid() -> Optional[str]:
    return drive_helpers.get_registry_value(
        winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", "MachineGuid"
    )


def random_set_windows_guid() -> bool:
    return set_windows_guid(str(uuid.uuid4()))


def random_set_convenient_save_data() -> bool:
    return set_convenient_save_data(random_sha1().hexdigest()[:32])


def random_set_player_prefs() -> bool:
    return set_player_prefs(random_sha1().hexdigest()[:32])


def get_hwid() -> list:
    hwid_array = []
    hwid_array.append(get_windows_guid())
    hwid_array.append(get_player_prefs())
    hwid_array.append(get_convenient_save_data())
    return hwid_array


def randomize_hwid() -> None:
    if random_set_convenient_save_data():
        print(
            Fore.LIGHTGREEN_EX
            + f"Successfully spoofed convenient save data! {Fore.MAGENTA}[{get_convenient_save_data()}]"
            + Style.RESET_ALL
        )
    else:
        print(Fore.RED + "Failed to spoof convenient save data!" + Style.RESET_ALL)
    if random_set_player_prefs():
        print(
            Fore.LIGHTGREEN_EX
            + f"Successfully spoofed player prefs! {Fore.MAGENTA}[{get_player_prefs()}]"
            + Style.RESET_ALL
        )
    else:
        print(Fore.RED + "Failed to spoof player prefs!" + Style.RESET_ALL)
    if random_set_windows_guid():
        print(
            Fore.LIGHTGREEN_EX
            + f"Successfully spoofed windows guid! {Fore.MAGENTA}[{get_windows_guid()}]"
            + Style.RESET_ALL
        )
    else:
        print(Fore.RED + "Failed to spoof windows guid!" + Style.RESET_ALL)

def random_sha1():
    return hashlib.sha1(uuid.uuid4().bytes)


if __name__ == "__main__":
    # print all hwids
    print(get_hwid())
