import requests
import hashlib
from urllib.parse import urlparse
from os.path import splitext, join
import a2s
from windows_toasts import Toast, WindowsToaster, ToastDisplayImage, InteractableWindowsToaster
from windows_toasts.wrappers import ToastImagePosition
import re
import time
import os


class ImageDownloader:
    def __init__(self, image_url):
        self.image_url = image_url
        self.image_path = self._download_and_save()

    def _download_and_save(self):
        # Compute SHA256 hash of the image URL
        sha256_hash = hashlib.sha256(self.image_url.encode()).hexdigest()

        # Extract the file extension from the URL
        url_path = urlparse(self.image_url).path
        _, file_extension = splitext(url_path)

        # Save the image in the system's temporary directory
        # Change 'image_downloads' to your desired folder name
        temp_dir = os.path.join(os.environ['TEMP'], 'image_downloads')
        os.makedirs(temp_dir, exist_ok=True)
        image_filename = f"{sha256_hash}{file_extension}"
        image_path = os.path.join(temp_dir, image_filename)

        # Check if the image with the same URL has already been downloaded
        if os.path.exists(image_path):
            # print(f"Image already downloaded at: {image_path}")
            return image_path

        # If not, download and save the image
        response = requests.get(self.image_url)
        image_data = response.content
        with open(image_path, 'wb') as image_file:
            image_file.write(image_data)

        # print(f"Image saved at: {image_path}")
        return image_path

    def get_image_path(self):
        return self.image_path


class ServerInfoCache:

    def __init__(self):
        self.cache = {}

    def get_server_info(self, server: tuple):
        # print(f"getting info for {server}")
        if server in self.cache:
            # print("fetching from cache")
            return self.cache[server]
        else:
            # print("grabbing new server info")
            server_info = a2s.info(server)
            self.cache[server] = server_info
            # print("saved to cache")
            return server_info


toaster = WindowsToaster('Smuggler Suite')
info_cache = ServerInfoCache()


def image_downloader(image_url) -> str:
    return ImageDownloader(image_url).get_image_path()


def alert(server: tuple, username, joined=True):
    toast = Toast()
    if joined:
        title = 'Player Joined!'
    else:
        title = 'Player Left!'
    toast.text_fields = [title, f'{username}']
    server_info = info_cache.get_server_info(server)
    server_icon_url = re.findall(r'<tn>https*://.*</tn>', server_info.keywords)
    if len(server_icon_url) > 0:
        # server icons are stored as an image url as an a2s keyword wrapped in <tn> html tags
        server_icon_url = server_icon_url[0].replace(
            '<tn>', '').replace('</tn>', '')
        image_path = image_downloader(server_icon_url)
    else:
        # resort to unturned logo for server if none is provided
        image_path = image_downloader(
            'https://static.wikia.nocookie.net/logopedia/images/4/4e/Unturned_%28Icon%29.jpg/revision/latest/scale-to-width-down/250?cb=20220820223406')

    server_logo = ToastDisplayImage.fromPath(image_path)
    server_logo.position = ToastImagePosition.Inline
    toast.AddImage(server_logo)

    toaster.show_toast(toast)


def player_joined(server: tuple, username):
    alert(server, username, joined=True)


def player_left(server: tuple, username):
    alert(server, username, joined=False)


if __name__ == '__main__':
    # 5.180.106.21:27027
    s = ('5.180.106.21', 27027)
    alert(server=s, username='Gobbler', joined=True)
    time.sleep(5)
    alert(server=s, username='Gobbler', joined=False)
