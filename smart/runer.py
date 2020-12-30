# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      run
# Author:    liangbaikai
# Date:      2020/12/22
# Desc:      there is a python file description
# ------------------------------------------------------------------
import asyncio
import importlib
import inspect
import sys
import time
from asyncio import CancelledError
from typing import List

from smart import log
from smart.core import Engine
from smart.middlewire import Middleware
from smart.spider import Spider


# def run(spider_name):
#     spider_module = importlib.import_module(f'{spider_name}')
#     spider = [x for x in inspect.getmembers(spider_module,
#                                             predicate=lambda x: inspect.isclass(x)) if
#               issubclass(x[1], Spider) and x[1] != Spider]
#     if spider and len(spider) > 0:
#         loop = asyncio.get_event_loop()
#         core = Engine(spider[0][1])
#         loop.run_until_complete(core.start())


class CrawStater:

    def __init__(self, loop=None):
        if sys.platform == "win32":
            loop = loop or asyncio.ProactorEventLoop()
            loop.set_debug(True)
        else:
            # todo use  uvloop
            self.loop = loop or asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = loop
        self.cores = []
        self.spider_names = []

    def run_by_class_or_instance(self, spider, middlewire: Middleware = None):
        if not spider:
            raise ValueError("need a  Spider class or Spider sub instance")
        if isinstance(spider, Spider):
            spider = spider.__class__
        elif not issubclass(spider, Spider) or spider == Spider:
            raise ValueError("need a  Spider class or Spider sub instance")
        start = time.time()
        core = Engine(spider, middlewire)
        self.cores.append(core)
        self.spider_names.append(spider.name)
        self._run()
        log.get_logger().info(f'craw succeed {",".join(self.spider_names)} ended.. it cost {time.time() - start}s')

    def run(self, spider_module: str, spider_names: List[str] = [], middlewire: Middleware = None):
        start = time.time()

        spider_module = importlib.import_module(f'{spider_module}')
        spider = [x for x in inspect.getmembers(spider_module,
                                                predicate=lambda x: inspect.isclass(x)) if
                  issubclass(x[1], Spider) and x[1] != Spider]
        if spider and len(spider) > 0:
            for tuple_item in spider:
                if (not spider_names or len(spider_names) <= 0) \
                        or tuple_item[1].name in spider_names:
                    core = Engine(tuple_item[1], middlewire)
                    self.cores.append(core)
                    self.spider_names.append(tuple_item[1].name)
            self._run()
            log.get_logger().info(f'craw succeed {",".join(self.spider_names)} ended.. it cost {time.time() - start}s')

    def stop(self):
        log.get_logger().info(f'warning stop be called,  {",".join(self.spider_names)} will stop ')
        for core in self.cores:
            self.loop.call_soon_threadsafe(core.close)

    def _run(self):
        tasks = []
        for core in self.cores:
            log.get_logger().info(f'{core.spider.name} start run..')
            future = asyncio.ensure_future(core.start(), loop=self.loop)
            tasks.append(future)
        if len(tasks) <= 0:
            raise ValueError("can not finded spider to start so ended...")
        group_tasks = asyncio.gather(*tasks, loop=self.loop)
        self.loop.run_until_complete(group_tasks)
