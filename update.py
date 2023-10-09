import os
import json
import shutil
import subprocess
import zipfile
import requests
import argparse
from typing import Optional

# toggle argument 'update'
parser = argparse.ArgumentParser()
parser.add_argument("--set", help="set the latest version info", action="store_true")
args = parser.parse_args()


REPO_ZIP_URL = "https://github.com/downj05/SuiteBanEv/archive/refs/heads/main.zip"
COMMITS_URL = "https://api.github.com/repos/downj05/SuiteBanEv/commits/main"


# Function to fetch the latest version information from the internet
def get_latest_version_info() -> tuple:
    # Use requests or any other method to fetch the latest version info from your Git repo
    # Parse and return the latest version information (e.g., commit hash or version number)
    response = requests.get(COMMITS_URL)
    if response.status_code == 200:
        json_r = json.loads(response.content)
        return (
            json_r["sha"],
            json_r["commit"]["message"],
            json_r["commit"]["author"]["date"],
        )
    else:
        raise Exception(f"Failed to fetch latest version info: {response.content}")


def set_latest_version_info():
    with open("version.json", "w") as f:
        json.dump(get_latest_version_info(), f, indent=4)


def get_current_version_info() -> Optional[tuple]:
    if not os.path.isfile(os.path.join(os.path.dirname(__file__), "version.json")):
        return None
    with open("version.json", "r") as f:
        v_json = json.load(f)
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

    # Database file
    print("Copying database file...")
    shutil.copy2(
        os.path.join(os.path.dirname(__file__), "db.json"),
        os.path.join(destination_folder, "db.json"),
    )


# Function used with copytree() to get verbose output
def verbose_copy(source, target):
    print(f"Copying {source} to {target}")
    shutil.copy2(source, target)


# Function to replace the current script folder with the updated version
def replace_current_folder(destination_folder, current_folder):
    # Move the contents of the new folder to the current folder
    for item in os.listdir(destination_folder):
        source = os.path.join(destination_folder, item)
        target = os.path.join(current_folder, item)
        if os.path.isdir(source):
            shutil.copytree(
                source, target, dirs_exist_ok=True, copy_function=verbose_copy
            )
        else:
            shutil.copy2(source, target)


# Main function to perform the update process
def update_script():
    if not compare_versions():
        print("No updates available.")
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
        print("Cleaning up...")
        shutil.rmtree(destination_folder)

        print("Update successful.")
        os.system("run.bat")
    except Exception as e:
        print(f"Update failed: {str(e)}")


if __name__ == "__main__":
    if args.set:
        set_latest_version_info()
        exit(0)
