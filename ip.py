import requests
from time import sleep

# Function to obtain the public IP address of the device
def get_public_ip(cooldown:int=3) -> str:
    """
    Get the public IP address of the device
    :return: The public IP address of the device
    """
    # Define the URL for the ipify API
    url = 'https://api.ipify.org?format=json'
    
    # Send a GET request to the URL
    while True:
        try:
            response = requests.get(url)
            # Parse the JSON content of the response
            data = response.json()
            break
        except Exception as e:
            print(f"[IP] Error obtaining IP: {e}")
            print(f"[IP] Retrying in {cooldown} seconds")
            sleep(cooldown)
            continue
    
    # Extract the IP address from the JSON data and return it
    return data['ip']
