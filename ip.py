import requests
from time import sleep, time


class PublicIpAPI:
    """
    Object for a public IP API
    Needs to have a get_method that returns a tuple of (ip, http_status_code)
    """

    name = None
    url = None
    get_method = None
    count = 0
    timeout = 3

    def get_ip(self):
        try:
            ip, code = self.get_method()
            if code == 200:
                return ip
        except Exception as e:
            print(f"[{self.name} IP] Error obtaining IP [{code}]: {e}")
            return False
        finally:
            self.count += 1


class PublicIp:
    def __init__(self):
        self.api_list = []

    def register_api(self, api: PublicIpAPI):
        self.api_list.append(api)

    def get_public_ip(self) -> str:
        while True:
            counts = [api.count for api in self.api_list]
            choice = self.api_list[counts.index(min(counts))]

            ip = choice.get_ip()
            if ip:
                return ip
            else:
                continue


class Ipify(PublicIpAPI):
    name = "Ipify"
    url = "https://api.ipify.org"

    def get_method(self):
        r = requests.get(self.url, timeout=self.timeout)
        return r.text, r.status_code


class BigData(PublicIpAPI):
    name = "BigData"
    url = "https://api.bigdatacloud.net/data/client-ip"

    def get_method(self):
        r = requests.get(self.url, timeout=self.timeout)
        return r.json().get('ipString'), r.status_code


class SeeIP(PublicIpAPI):
    name = "SeeIP"
    url = "https://api.seeip.org/jsonip?"

    def get_method(self):
        r = requests.get(self.url, timeout=self.timeout)
        return r.json().get('ip'), r.status_code


def IpManager():
    ip = PublicIp()

    ipify = Ipify()
    ip.register_api(ipify)

    big_data = BigData()
    ip.register_api(big_data)

    see_ip = SeeIP()
    ip.register_api(see_ip)
    return ip


if __name__ == '__main__':
    ip_manager = IpManager()

    # test using only 1 api, then test using all 3

    s = time()
    for i in range(10):
        ip = ip_manager.get_public_ip()
        print(ip, i)
    e = time()

    print(f"Time taken: {e - s}")

    ip_manager = PublicIp()
    ip_manager.register_api(Ipify())

    s = time()
    for i in range(10):
        ip = ip_manager.get_public_ip()
        print(ip, i)
    e = time()

    print(f"Time taken: {e - s}")
