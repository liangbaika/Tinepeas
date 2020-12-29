import threading

from tinepeas import Spider, Request


class IpSpider(Spider):
    name = 'ipspider'
    start_urls = []

    def start_requests(self):
        for page in range(1, 1000):
            url = f'http://exercise.kingname.info/exercise_middleware_ip/{page}'
            yield Request(url, callback=self.parse)

    def parse(self, response):
        print(response.body)
        print(threading.current_thread().name,"runing...",self.name)
        yield Request(response.url, callback=self.parse2)
        print(2222)

    def parse2(self, response):
        print(333)
        pass
