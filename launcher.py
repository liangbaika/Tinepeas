from smart.runer import CrawStater
from spiders.ipspider2 import IpSpider3, GovSpider, IpSpider, ApiSpider
from test import middleware2
from tinepeas import run

if __name__ == '__main__':
    # run("ipspider")
    starter = CrawStater()
    starter.run_by_class_or_instance(ApiSpider,middlewire=middleware2)
    # starter.run_by_class_or_instance(IpSpider,middlewire=middleware2)
    #IpSpider
    # starter.run("spiders.ipspider2", ["IpSpider22222", "ipspider2"],middlewire=None)
    # starter.run("spiders.ipspider2", ["IpSpider22222"])

