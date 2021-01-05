import asyncio
import threading
import time
from multiprocessing.pool import Pool

from smart.pipline import Piplines
from smart.runer import CrawStater
from smart.scheduler import SampleDuplicateFilter
from spiders.ipspider2 import IpSpider3, GovSpider, IpSpider, ApiSpider
from test import middleware2

piplinestest = Piplines()


@piplinestest.pipline(1)
async def do_pip(spider_ins, item):
    print(item.to_dict())
    print("我是item############################################11111111")
    return item


@piplinestest.pipline(2)
def do_pip2(spider_ins, item):
    print(item.to_dict())
    print("我是item############################################222222")
    return item


def start1():
    starter = CrawStater()
    starter.run_single(IpSpider(), middlewire=middleware2, pipline=piplinestest)


if __name__ == '__main__':
    starter = CrawStater()
    starter.run_many([IpSpider()], middlewire=middleware2, pipline=piplinestest)
    # starter = CrawStater()
    # starter.run_by_class_or_instance(IpSpider, middlewire=middleware2, pipline=piplinestest)
    # run("ipspider")
    # thread = threading.Thread(target=start1)
    # thread.start()
    # time.sleep(1)
    # starter.pause()
    # time.sleep(4)
    # starter.recover()
    # thread.join()

    # starter.run_by_class_or_instance(IpSpider,middlewire=middleware2)
    # IpSpider
    # starter.run("spiders.ipspider2", ["IpSpider22222", "ipspider2"],middlewire=None)
    # starter.run("spiders.ipspider2", ["IpSpider22222"])
