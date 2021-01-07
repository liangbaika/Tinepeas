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
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from smart.log import log
from smart.core import Engine
from smart.middlewire import Middleware
from smart.pipline import Piplines
from smart.setting import gloable_setting_dict
from smart.spider import Spider


class CrawStater:

    def __init__(self, loop=None):
        if sys.platform == "win32":
            loop = loop or asyncio.ProactorEventLoop()
        else:
            # todo use  uvloop
            self.loop = loop or asyncio.new_event_loop()
        thread_pool_max_size = gloable_setting_dict.get(
            "thread_pool_max_size", 30)
        loop.set_default_executor(ThreadPoolExecutor(thread_pool_max_size))
        asyncio.set_event_loop(loop)
        self.loop = loop
        self.cores = []
        self.log = log
        self.spider_names = []

    def run_many(self, spiders: List[Spider], middlewire: Middleware = None, pipline: Piplines = None):
        if not spiders or len(spiders) <= 0:
            raise ValueError("need spiders")
        start = time.time()
        for spider in spiders:
            if not isinstance(spider, Spider):
                raise ValueError("need a   Spider sub instance")
            _middle = spider.cutome_setting_dict.get("middleware_instance") or middlewire
            _pip = spider.cutome_setting_dict.get("piplines_instance") or pipline
            core = Engine(spider, _middle, _pip)
            self.cores.append(core)
            self.spider_names.append(spider.name)
        self._run()
        self.log.info(f'craw succeed {",".join(self.spider_names)} ended.. it cost {time.time() - start}s')

    def run_single(self, spider: Spider, middlewire: Middleware = None, pipline: Piplines = None):
        if not spider:
            raise ValueError("need a  Spider class or Spider sub instance")
        if not isinstance(spider, Spider):
            raise ValueError("need a   Spider sub instance")
        start = time.time()
        _middle = spider.cutome_setting_dict.get("middleware_instance") or middlewire
        _pip = spider.cutome_setting_dict.get("piplines_instance") or pipline
        core = Engine(spider, _middle, _pip)
        self.cores.append(core)
        self.spider_names.append(spider.name)
        self._run()
        self.log.info(f'craw succeed {",".join(self.spider_names)} ended.. it cost {time.time() - start}s')

    def run(self, spider_module: str, spider_names: List[str] = [], middlewire: Middleware = None,
            pipline: Piplines = None):
        start = time.time()

        spider_module = importlib.import_module(f'{spider_module}')
        spider = [x for x in inspect.getmembers(spider_module,
                                                predicate=lambda x: inspect.isclass(x)) if
                  issubclass(x[1], Spider) and x[1] != Spider]
        if spider and len(spider) > 0:
            for tuple_item in spider:
                if (not spider_names or len(spider_names) <= 0) \
                        or tuple_item[1].name in spider_names:
                    _middle = tuple_item[1].cutome_setting_dict.get("middleware_instance") or middlewire
                    _pip = tuple_item[1].cutome_setting_dict.get("piplines_instance") or pipline
                    _spider = tuple_item[1]()
                    if not isinstance(_spider, Spider):
                        raise ValueError("need a   Spider sub instance")
                    core = Engine(_spider, _middle, _pip)
                    self.cores.append(core)
                    self.spider_names.append(_spider.name)
            self._run()
            self.log.info(f'craw succeed {",".join(self.spider_names)} ended.. it cost {time.time() - start}s')

    def stop(self):
        self.log.info(f'warning stop be called,  {",".join(self.spider_names)} will stop ')
        for core in self.cores:
            self.loop.call_soon_threadsafe(core.close)

    def pause(self):
        self.log.info(f'warning pause be called,  {",".join(self.spider_names)} will pause ')
        for core in self.cores:
            self.loop.call_soon_threadsafe(core.pause)

    def recover(self):
        self.log.info(f'warning recover be called,  {",".join(self.spider_names)} will recover ')
        for core in self.cores:
            self.loop.call_soon_threadsafe(core.recover)

    def _run(self):
        tasks = []
        for core in self.cores:
            self.log.info(f'{core.spider.name} start run..')
            future = asyncio.ensure_future(core.start(), loop=self.loop)
            tasks.append(future)
        if len(tasks) <= 0:
            raise ValueError("can not finded spider tasks to start so ended...")
        try:
            group_tasks = asyncio.gather(*tasks, loop=self.loop)
            self.loop.run_until_complete(group_tasks)
        except CancelledError as e:
            self.log.debug(f" in loop, occured CancelledError e {e} ", exc_info=True)
        except KeyboardInterrupt as e2:
            self.log.debug(f" in loop, occured KeyboardInterrupt e {e2} ")
            self.stop()
        except BaseException as e3:
            self.log.error(f" in loop, occured BaseException e {e3} ", exc_info=True)
