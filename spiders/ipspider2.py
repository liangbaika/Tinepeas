import threading

from lxml import etree
from smart.response import Response
from smart.request import Request
from smart.spider import Spider




class IpSpider(Spider):
    name = 'ipspider2'
    start_urls = []

    def start_requests(self):
        for page in range(1010):
            print(page)
            url = f'http://exercise.kingname.info/exercise_middleware_ip/{page}'
            # url = f'http://exercise.kingname.info/exercise_middleware_ip/{page}'
            # url = 'http://fzggw.zj.gov.cn/art/2020/8/26/art_1621004_55344873.html'
            url = 'https://s.bdstatic.com/common/openjs/amd/eslx.js'
            yield Request(url, callback=self.parse,  dont_filter=True)

    def parse(self, response: Response):
        print(threading.current_thread().name, "runing...", self.name)
        print(f'#######{self.name}')
        print(response.status)
        yield Request(response.url, callback=self.parse2, dont_filter=True)

    def parse2(self, response):
        print(response.status)
        print("parse2222")



class IpSpider3(Spider):
    name = 'IpSpider22222'
    start_urls = []

    def start_requests(self):
        for page in range(1010):
            # url = f'http://exercise.kingname.info/exercise_middleware_ip/{page}'
            url = 'https://s.bdstatic.com/common/openjs/amd/eslx.js'
            yield Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response: Response):
        # print('#######2')
        print(f'#######{self.name}')
        # print(threading.current_thread().name, "runing...", self.name)
        print(response.status)
        # yield Request(url=response.url, callback=self.parse2, dont_filter=True)

    def parse2(self, response):
        pass
