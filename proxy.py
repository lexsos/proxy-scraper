import re
import itertools
import requests


class SamairList(object):

    """ Scrap proxy from http://samair.ru/ """
    
    BASE_URL = 'http://samair.ru/proxy/list-IP-port/proxy-{page}.htm'

    def scrap(self):
        self.proxies = []
        for page in itertools.count(1):
            response = requests.get(self.BASE_URL.format(page=page))
            response_proxies = re.findall(
                r'(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}',
                response.content.decode('utf-8'))
            if not len(response_proxies):
                return
            self.proxies.extend(response_proxies)


if __name__ == '__main__':

    prx = SamairList()
    prx.scrap()
    print(prx.proxies)
