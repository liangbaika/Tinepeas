from smart.runer import CrawStater
from test import middleware2

if __name__ == '__main__':
    starter = CrawStater()
    starter.run("spiders.ipspider2", ["IpSpider22222", "ipspider2"],middlewire=None)
    # starter.run("spiders.ipspider2", ["IpSpider22222"])

