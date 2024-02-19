import os
import json
import shutil
import subprocess
import zipfile
import requests
import argparse
from tqdm import tqdm
from command import Command2
import db_provider, ban_manager, server
from time import time as timestamp
from typing import Optional

REPO_ZIP_URL = "https://github.com/downj05/SuiteBanEv/archive/refs/heads/main.zip"
COMMITS_URL = "https://api.github.com/repos/downj05/SuiteBanEv/commits/main"


# Function to fetch the latest version information from the internet
def get_latest_version_info(check_every_second=0) -> tuple:
    # Use requests or any other method to fetch the latest version info from your Git repo
    # Parse and return the latest version information (e.g., commit hash or version number)
    
    # Check every second determines the interval between checking for updates
    # E.g if it is 300, then the function will only check for updates once the
    # last one is > 5 minutes old
    if check_every_second > 0:
        last_checked = get_current_version_timestamp()
        if last_checked is not None:
            if timestamp() - last_checked < check_every_second:
                print("Not checking for updates, last check was too recent")
                return get_current_version_info()
        else:
            print("Current version has no timestamp!")
    print("Fetching latest version info...")
    response = requests.get(COMMITS_URL)
    if response.status_code == 200:
        json_r = json.loads(response.content)
        # set_current_version_timestamp()
        print(f'Latest version info fetched, not fetching for another {check_every_second} seconds')
        json_r = (json_r["sha"],
            json_r["commit"].get("message", "No update notes"),
            json_r["commit"]["author"]["date"],
            timestamp(),)
        with open("version.json", "w") as f:
            json.dump(json_r, f, indent=4)
        return json_r
    else:
        if 'max' in response.content and 'retries' in response.content:
            print("Rate limited, ignoring this time...")
            curr = get_current_version_info()
            return curr[0], curr[1], curr[2], timestamp()
        print(f"Failed to fetch latest version info: {response.content}, {response.status_code}")
        raise Exception(
            f"Failed to fetch latest version info: {response.content}")


def set_latest_version_info():
    with open("version.json", "w") as f:
        json.dump(get_latest_version_info(), f, indent=4)


def get_current_version_timestamp() -> Optional[int]:
    if not os.path.isfile(os.path.join(os.path.dirname(__file__), "version.json")):
        return None
    with open("version.json", "r") as f:
        try:
            v_json = json.load(f)
        except json.JSONDecodeError:
            return None
        if len(v_json) < 4:
            return None
        return v_json[3]

def set_current_version_timestamp():
    with open("version.json", "r") as f:
        try:
            v_json = json.load(f)
        except json.JSONDecodeError:
            v_json = ['Unknown', '', '', timestamp()]
    with open("version.json", "w") as f:
        if len(v_json) < 4 and len(v_json) > 0:
            print(v_json)
            v_json = [v_json[0], v_json[1], v_json[2], timestamp()]
        else:
            v_json[3] = timestamp()
        json.dump(v_json, f, indent=4)

def get_current_version_info() -> Optional[tuple]:
    if not os.path.isfile(os.path.join(os.path.dirname(__file__), "version.json")):
        return None
    with open("version.json", "r") as f:
        try:
            v_json = json.load(f)
        except json.JSONDecodeError:
            return None
        return (v_json[0], v_json[1], v_json[2])


def compare_versions(latest_version=None) -> bool:
    # Returns True if the current version is outdated, False otherwise
    # Can optionally pass the latest version info as a tuple to avoid fetching it again
    current_version = get_current_version_info()
    if current_version is None:
        return True
    if latest_version is None:
        latest_version = get_latest_version_info()
    return current_version[0] != latest_version[0]


# Function to download and extract the latest version
def download_and_extract_latest_version(destination_folder):
    # Download the latest version as a ZIP file
    response = requests.get(REPO_ZIP_URL)

    if response.status_code == 200:
        with open("latest_version.zip", "wb") as zip_file:
            zip_file.write(response.content)

        # Extract the ZIP file
        with zipfile.ZipFile("latest_version.zip", "r") as zip_ref:
            zip_ref.extractall(destination_folder)

        os.remove("latest_version.zip")


# Function to preserve user settings and ignore files
def preserve_user_settings(destination_folder):
    # Copy user settings, secret files, config files, etc., from the old folder to the new folder
    try:
        current_folder = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(current_folder, "db.json")
        if not os.path.isfile(db_path):
            print("No database file found, skipping...")
            return
        # Database file
        print("Copying database file...")
        shutil.copy2(
            db_path,
            os.path.join(destination_folder, "db.json"),
        )
    except Exception as e:
        print(f"Failed to preserve user settings: {str(e)}")


# Function used with copytree() to get verbose output
def verbose_copy(source, target):
    print(f"Copying {source} to {target}")
    shutil.copy2(source, target)


# Function to replace the current script folder with the updated version
def replace_current_folder(destination_folder, current_folder):
    # Move the contents of the new folder to the current folder
    print(
        f"Replacing current folder from {destination_folder} to {current_folder}...")
    try:
        # Contents we need to move will be in the first subfolder of the destination folder
        # This is because the ZIP file contains a parent folder with the repo name

        # Verify that the destination folder contains only one subfolder
        print("Verifying destination folder...")
        subfolders = [
            item
            for item in os.listdir(destination_folder)
            if os.path.isdir(os.path.join(destination_folder, item))
        ]
        print(f"Found {len(subfolders)} subfolders")
        if len(subfolders) != 1:
            raise Exception(
                f"Expected only one subfolder in the destination folder, found {len(subfolders)}"
            )
        print(f'Using subfolder "{subfolders[0]}"')
        destination_folder = os.path.join(destination_folder, subfolders[0])

        for item in os.listdir(destination_folder):
            source = os.path.join(destination_folder, item)
            target = os.path.join(current_folder, item)
            if os.path.isdir(source):
                print(f'Copying directory "{source}" to "{target}"')
                shutil.copytree(
                    source, target, dirs_exist_ok=True, copy_function=verbose_copy
                )
            else:
                print(f'Copying file "{source}" to "{target}"')
                shutil.copy2(source, target)
    except Exception as e:
        print(f"Failed to replace current folder: {str(e)}")
        exit(1)


class JSON2SQLMigrator(Command2):
    """
    Uploads the JSON database to the SQL database provided one is selected
    
    """
    name:str = "upload"
    usage:str = "upload <database server>/<selected (none)>"
    help:str = "upload the current JSON database to the selected/provided SQL database\nfor migration purposes"

    def execute(self, *args):
        parser = argparse.ArgumentParser()
        parser.add_argument('server', type=str, default=None, nargs='?')
        args = parser.parse_args(args)
        if args.server is None:
            if db_provider.SelectedDatabaseServerService.selected() is None:
                raise("No database server selected/provided")
            args.server = db_provider.SelectedDatabaseServerService.selected()
            print("Testing database server...")
            r = args.server.test_connection(host=args.server.host_port, user=args.server.user, password=args.server.password, print_info=True,)
            if r:
                print("Database server is working!")
            else:
                raise Exception("Database server is not working!")
            # Select the server
            print("Selecting the database server...")
            db_provider.SelectedDatabaseServerService.select(args.server)


            # Get all JSON bans
            print("Fetching all bans from JSON database...")
            json_bans = ban_manager.JsonBan.all()

            # Confirm
            print(f"You are about to upload {len(json_bans)} locally saved bans to the database: {args.server.name}")
            i = input("Continue? (y/n): ")
            if i.lower() != "y":
                print("Cancelled by user.")
                return

            # Upload all bans to the SQL database
            print("Uploading bans to the SQL database...")
            banManger = ban_manager.BanDatabaseService()

            loading_bar = tqdm(json_bans, desc="Uploading bans")
            for ban in loading_bar:
                # add ban to the SQL database
                loading_bar.set_description(f"Uploading ban: {ban.steam64}, {ban.server}")
                banManger.add_ban(ip=ban.ip, hwid=ban.hwid, steam64=ban.steam64, duration=ban.duration, server=server.ServerListService().from_name(ban.server))
            print("Upload complete! Bans are now imported!")


# Main function to perform the update process
def update_script(parent=None):
    if not compare_versions():
        print("No updates available.")
        i = input("Force update? (y/n): ")
        if i.lower() != "y":
            return
    current_folder = os.path.abspath(os.path.dirname(__file__))
    destination_folder = os.path.join(current_folder, "temp_new_version")

    try:
        # Step 1: Download and extract the latest version
        print("Downloading and extracting the latest version...")
        download_and_extract_latest_version(destination_folder)

        # Step 2: Preserve user settings
        print("Migrating user settings...")
        preserve_user_settings(destination_folder)

        # Step 3: Replace the current script folder with the updated version
        print("Replacing the current script folder with the updated version...")
        replace_current_folder(destination_folder, current_folder)

        # Install any new dependencies
        print("Installing new pip dependencies...")
        venv_path = os.path.join(current_folder, "venv", "Scripts", "pip.exe")
        requirements_path = os.path.join(current_folder, "requirements.txt")
        subprocess.check_call([venv_path, "install", "-r", requirements_path])

        # Update version info
        print("Updating version info...")
        set_latest_version_info()

        # Clean up
        print(f"Cleaning up...")
        print(f"Deleting {destination_folder}...")
        shutil.rmtree(destination_folder)

        print("Update successful.")
        os.system("run.bat")
    except Exception as e:
        print(f"Update failed: {str(e)}")


if __name__ == "__main__":
    set_current_version_timestamp()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--set", help="set the latest version info", action="store_true")
    parser.add_argument("--update", help="force an update",
                        action="store_true")
    args = parser.parse_args()
    if args.set:
        set_latest_version_info()
        exit(0)
    if args.update:
        update_script()
        exit(0)
    