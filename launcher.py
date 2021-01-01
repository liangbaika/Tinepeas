from smart.pipline import Piplines
from smart.runer import CrawStater
from spiders.ipspider2 import IpSpider3, GovSpider, IpSpider, ApiSpider
from test import middleware2
from tinepeas import run

piplinestest = Piplines()


@piplinestest.pipline(1)
async def do_pip(item):
    print(item.to_dict())
    print("我是item############################################11111111")
    return item


@piplinestest.pipline(2)
def do_pip2(item):
    print(item.to_dict())
    print("我是item############################################222222")
    return item


if __name__ == '__main__':
    # run("ipspider")
    starter = CrawStater()
    starter.run_by_class_or_instance(IpSpider, middlewire=middleware2, pipline=piplinestest)
    # starter.run_by_class_or_instance(IpSpider,middlewire=middleware2)
    # IpSpider
    # starter.run("spiders.ipspider2", ["IpSpider22222", "ipspider2"],middlewire=None)
    # starter.run("spiders.ipspider2", ["IpSpider22222"])
