import os, sys
from steam_api import get_user_info, steamid3_to_steam64
import winreg
import time
import drive_helpers

DRIVE_LETTER = None

def get_steam_logins_by_modified():
    # Get the steamid3's of all the previously logged in Steam users on this machine
    # Sorts them by modification date
    global DRIVE_LETTER
    if DRIVE_LETTER == None:
        DRIVE_LETTER = drive_helpers.get_steam_drive()
    dir_path = rf'{DRIVE_LETTER}:\Program Files (x86)\Steam\userdata' 
    files = os.listdir(dir_path)
    files_with_mtime = [(f, os.stat(os.path.join(dir_path, f)).st_mtime) for f in files]
    sorted_files = sorted(files_with_mtime, key=lambda x: x[1])
    return sorted_files

def readable_modification_date(modification_time):
    current_time = time.time()
    time_diff = current_time - modification_time

    # If the modification time is in the future, return an error message
    if time_diff < 0:
        return "Invalid timestamp"

    # If the modification time is less than 1 minute ago, return "Just now"
    if time_diff < 60:
        return "Just now"

    # If the modification time is less than 1 hour ago, return the number of minutes
    if time_diff < 3600:
        minutes = int(time_diff // 60)
        if minutes == 1:
            return "1 minute ago"
        else:
            return f"{minutes} minutes ago"

    # If the modification time is less than 1 day ago, return the number of hours
    if time_diff < 86400:
        hours = int(time_diff // 3600)
        if hours == 1:
            return "1 hour ago"
        else:
            return f"{hours} hours ago"

    # If the modification time is less than 1 week ago, return the number of days
    if time_diff < 604800:
        days = int(time_diff // 86400)
        if days == 1:
            return "1 day ago"
        else:
            return f"{days} days ago"

    # If the modification time is less than 1 month ago, return the number of weeks
    if time_diff < 2592000:
        weeks = int(time_diff // 604800)
        if weeks == 1:
            return "1 week ago"
        else:
            return f"{weeks} weeks ago"

    # If the modification time is less than 1 year ago, return the number of months
    if time_diff < 31536000:
        months = int(time_diff // 2592000)
        if months == 1:
            return "1 month ago"
        else:
            return f"{months} months ago"

    # Otherwise, calculate the number of years and months ago
    years = int(time_diff // 31536000)
    months = int((time_diff % 31536000) // 2592000)
    if years == 0:
        if months == 1:
            return "1 month ago"
        else:
            return f"{months} months ago"
    elif years == 1:
        if months == 0:
            return "1 year ago"
        elif months == 1:
            return "1 year and 1 month ago"
        else:
            return f"1 year and {months} months ago"
    else:
        if months == 0:
            return f"{years} years ago"
        elif months == 1:
            return f"{years} years and 1 month ago"
        else:
            return f"{years} years and {months} months ago"

def get_steam_current_id3_from_registry():
    # Open the registry key for reading
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Valve\Steam\ActiveProcess')

    # Read the ActiveUser value as a REG_DWORD
    active_user, _ = winreg.QueryValueEx(key, 'ActiveUser')

    # Convert the value to a base-10 integer
    active_user_int = int(active_user)

    # Close the registry key
    winreg.CloseKey(key)

    # Print the value as an integer
    return active_user_int

def select_all_steam64():
    steamid3_list = get_steam_logins_by_modified()
    steamid64_list = []
    for s, modified in steamid3_list:
        steamid64_list.append(steamid3_to_steam64(f"U:1:{s}"))
    return steamid64_list

def get_latest_user_steam64():
    # Get the steam64 of the latest user logged into Steam on the users machine
    # Pull active user from registry
    steamid3 = get_steam_current_id3_from_registry()
    steam64 = steamid3_to_steam64(f"U:1:{steamid3}")
    return steam64

def get_latest_user_info():
    return get_user_info(get_latest_user_steam64())

class ClientIDList:
    @staticmethod
    def ids() -> list[int]:
        """
        Get all of the steam64 ids of the users logged into Steam on the users machine
        :returns: list of steam64 ids
        """
        return select_all_steam64()

    @staticmethod
    def latest() -> int:
        """
        Get the steam64 of the latest user logged into Steam on the users machine
        :returns: latest users steam64 id
        """
        return get_latest_user_steam64()

if __name__ == '__main__':
    id64 = get_latest_user_steam64()
    c = ClientIDList()
    print(f"Real {id64} ClientIDList {c.latest}")
