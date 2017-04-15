import requests

link = 'http://l2.io/ip'

with open('proxylist.txt', 'r') as infile:
    for row in infile:
        proxy = row.strip('\n')
        try:
            response = requests.get(
                link, proxies={'http': 'http://' + proxy}, timeout=15).content.decode('utf-8')
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
            response = 'TIMEOUT'
        print(proxy, response, ('\033[0;31mFAIL', '\033[0;32mPASS')[proxy.startswith(response)], '\033[0m')
