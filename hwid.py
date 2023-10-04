import subprocess
import os
from typing import Optional, Union
import drive_helpers

DRIVE_LETTER = drive_helpers.get_unturned_drive()


def is_volid_installed():
    try:
        subprocess.run(["volid"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False


VOLID_INSTALLED = is_volid_installed()

if not VOLID_INSTALLED:
    import urllib.request
    import zipfile

    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the download URL and file paths
    download_url = "https://download.sysinternals.com/files/VolumeId.zip"
    zip_file_path = os.path.join(script_dir, "VolumeId.zip")

    print("'volid' is not found. Installing...")

    try:
        # Download the ZIP file
        urllib.request.urlretrieve(download_url, zip_file_path)

        # Extract 'volid.exe' from the ZIP file to the script's directory
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extract("VolumeId/volid.exe", script_dir)

        # Clean up by removing the ZIP file
        os.remove(zip_file_path)

        print("'volid' is now installed in the script's directory.")
    except Exception as e:
        print(f"An error occurred while installing 'volid': {str(e)}")


def get_drive_serial_number(drive_letter: str = DRIVE_LETTER) -> Optional[str]:
    """
    Use `vol` to get the current drive serial number
    :param drive_letter: The drive letter to get the serial number of
    :return: The serial number of the drive
    """
    # Run the 'vol' command with the specified drive letter
    process = subprocess.run(
        ["vol", f"{drive_letter}:"], capture_output=True, text=True, shell=True
    )

    # Extract the output text from the process output
    output_text = process.stdout.strip()

    # Split the output text into lines
    lines = output_text.split("\n")

    # Extract the line containing the volume serial number
    serial_number_line = None
    for line in lines:
        if "Volume Serial Number" in line:
            serial_number_line = line
            break

    # If the serial number line was found, extract the serial number and return it as a string
    if serial_number_line:
        serial_number = serial_number_line.split()[-1]
        return str(serial_number)

    # If the serial number line was not found, return None
    else:
        return None


def set_drive_serial_number(
    serial_number: str, drive_letter=DRIVE_LETTER
) -> Union[bool, str]:
    # use subprocess.run and the volid command to set the drive serial number
    # volid usage: volid <drive letter>: <serial number>

    process = subprocess.run(
        ["volid", f"{drive_letter}:", serial_number],
        capture_output=True,
        text=True,
        shell=True,
    )
    # get output text
    output_text = process.stdout.strip()
    # return output text
    if "updated to" in output_text:
        return True
    elif "denied" in output_text:
        return False
    return output_text


def increment_hwid(serial_number) -> str:
    # take serial number, which is in the format '5A34-0007' for example,
    # cast to int, increment, cast back to string.
    incremented_serial_number = int(serial_number.replace("-", ""), 16) + 1
    incremented_serial_number = str(hex(incremented_serial_number))[2:].upper()
    # add dash
    incremented_serial_number = (
        incremented_serial_number[:4] + "-" + incremented_serial_number[4:]
    )
    return incremented_serial_number


if __name__ == "__main__":
    print(get_drive_serial_number())
