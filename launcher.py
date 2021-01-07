import asyncio
import threading
import time
from multiprocessing.pool import Pool

from smart.log import log
from smart.pipline import Piplines
from smart.runer import CrawStater
from spiders.govs import GovsSpider
from spiders.ipspider2 import IpSpider3, GovSpider, IpSpider, ApiSpider
from spiders.json_spider import JsonSpider
from test import middleware2

piplinestest = Piplines()


@piplinestest.pipline(1)
async def do_pip(spider_ins, item):
    return item


@piplinestest.pipline(2)
def do_pip2(spider_ins, item):
    print(f"我是item####222 {item.results}")
    return item


def start1():
    starter = CrawStater()
    starter.run_single(IpSpider(), middlewire=middleware2, pipline=piplinestest)


if __name__ == '__main__':
    starter = CrawStater()
    spider1 = GovsSpider()
    spider2 = JsonSpider()
    starter.run_many([spider1,spider2], middlewire=middleware2, pipline=piplinestest)
