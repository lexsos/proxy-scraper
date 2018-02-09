import re
import itertools
import requests
import time
from urllib.parse import urlencode
from multiprocessing import Pool


PROCESSES = 32
TEST_URL = 'https://www.reformagkh.ru/myhouse'
TEST_TIMEOUT = 5


class ProxyList(object):

    """ Base class for scrap proxies """

    BASE_URL = None
    PAGE_RANGE = itertools.count(1)
    SLEEP_TIME = 1

    REGEX = r'(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}'

    proxies = []

    def findall(self, content):
        return re.findall(self.REGEX, content.decode('utf-8'))

    def scrap(self):
        self.proxies = []
        for page in self.PAGE_RANGE:
            response = requests.get(self.BASE_URL.format(page=page))
            response_proxies = self.findall(response.content)
            if not response_proxies:
                return
            self.proxies.extend(response_proxies)
            time.sleep(self.SLEEP_TIME)


class SamairList(ProxyList):

    """ Scrap proxy from http://samair.ru/ """

    BASE_URL = 'http://samair.ru/proxy/list-IP-port/proxy-{page}.htm'


class GatherList(ProxyList):

    """ Scrap proxy from http://www.gatherproxy.com/ """

    BASE_URL = 'http://www.gatherproxy.com/'
    REGEX_IP = r'\"PROXY_IP\":\"((?:\d{1,3}\.){3}\d{1,3})\"'
    REGEX_PORT = r'\"PROXY_PORT\":\"(\w{1,4})\"'
    PAGE_RANGE = (1, )

    def findall(self, content):
        ips = re.findall(self.REGEX_IP, content.decode('utf-8'))
        ports = re.findall(self.REGEX_PORT, content.decode('utf-8'))
        proxies = []
        for ip, port in zip(ips, ports):
            proxies.append('{}:{}'.format(ip, int(port, base=16)))
        return proxies


class FoxtoolsScraper(object):

    API_URL = 'http://api.foxtools.ru/v2/Proxy'
    PER_PAGE = 100
    MAX_PAGE=10

    def __init__(self):
        self.proxies = list()

    def get_url(self, page):
        arguments = urlencode(dict(free='yes', limit=100, page=page))
        return '{}?{}'.format(self.API_URL, arguments)

    def scrap(self):
        for i in range(1, self.MAX_PAGE):
            url = self.get_url(page=i)
            try:
                res = requests.get(url, timeout=5)
                self.add_proxy_to_list(data=res.json())
            except:
                pass
        return self.proxies

    def add_proxy_to_list(self, data):
        for item in data['response']['items']:
            proxy = '{}:{}'.format(item['ip'], item['port'])
            self.proxies.append(proxy)


def grab_list():
    for PrxClass in (SamairList, GatherList, FoxtoolsScraper):
        prx = PrxClass()
        prx.scrap()
        for proxy in prx.proxies:
            yield proxy


def test_proxy(proxy_address):
    try:
        proxy = {'https': 'http://' + proxy_address.strip('\n')}
        requests.get(TEST_URL, proxies=proxy, timeout=TEST_TIMEOUT)
        print(proxy_address)
        return proxy_address
    except:
        pass


def proxy_filter(proxy_list):
    with Pool(PROCESSES) as p:
        tested_proxy = p.map(test_proxy, proxy_list)
    return [p for p in tested_proxy if p]


if __name__ == '__main__':

    full_list = grab_list()
    good_list = proxy_filter(full_list)

    with open('proxylist.txt', 'w') as outfile:
        for row in good_list:
            outfile.write('{}\n'.format(row))
