import re
import itertools
import requests
import time


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


def grab_list():
    for PrxClass in (GatherList, SamairList):
        prx = PrxClass()
        prx.scrap()
        for proxy in prx.proxies:
            yield proxy


if __name__ == '__main__':

    with open('proxylist.txt', 'w') as outfile:
        for row in grab_list():
            outfile.write('{}\n'.format(row))
