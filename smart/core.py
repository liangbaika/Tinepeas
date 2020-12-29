# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      core
# Author:    liangbaikai
# Date:      2020/12/22
# Desc:      there is a python file description
# ------------------------------------------------------------------
import asyncio
import inspect
import threading
import time
import uuid
from collections import deque, Iterable
from typing import Dict, Union, List

from smart import log
from smart.downloader import Downloader
from smart.middlewire import Middleware
from smart.request import Request
from smart.scheduler import Scheduler
from smart.spider import Spider


class Engine:
    def __init__(self, spider, middlewire=None):
        self.task_dict: Dict[str, asyncio.Task] = {}
        self.middlewire = middlewire
        self.scheduler = Scheduler()
        self.downloader = Downloader(self.scheduler, self.middlewire)
        self.spider = spider()
        self.stop = False
        self.request_generator_queue = deque()

    def iter_request(self):
        while True:
            if not self.request_generator_queue:
                yield None
                continue
            request_generator = self.request_generator_queue[0]
            spider, request_generator = request_generator[0], request_generator[1]
            try:
                log.get_logger().debug(f" execute and get a request from cutomer code ")
                request = next(request_generator)
                request.__spider__ = spider
            except StopIteration:
                self.request_generator_queue.popleft()
                continue
            except Exception as e:
                self.request_generator_queue.popleft()
                continue
            yield request

    def check_complete_callback(self, task):
        if task.cancelled():
            log.get_logger().debug(f" a task canceld ")
            return
        if task and task.done() and task._key:
            log.get_logger().debug(f"a task done  ")
            self.task_dict.pop(task._key)

    async def start(self):
        self.request_generator_queue.append((self.spider, iter(self.spider)))
        # self.request_generator_queue.append( iter(self.spider))

        while not self.stop:
            request_to_schedule = next(self.iter_request())
            if request_to_schedule:
                self.scheduler.schedlue(request_to_schedule)
            request = self.scheduler.get()
            if request is None and not self.task_dict:
                log.get_logger().debug(f" engine will stop now")
                self.stop = True
                break
            if isinstance(request, Request):
                task = asyncio.ensure_future(self.downloader.download(request))
                key = str(uuid.uuid4())
                task._key = key
                self.task_dict[key] = task
                task.add_done_callback(self.check_complete_callback)

            resp = self.downloader.get()
            if not resp:
                # 让下载器能被调度
                await asyncio.sleep(0.0005)
                continue
            custome_callback = resp.request.callback
            if custome_callback:
                request_generator = custome_callback(resp)
                if request_generator:
                    self.request_generator_queue.append((custome_callback.__self__, request_generator))
                    # self.request_generator_queue.append( request_generator)

    def close(self):
        self.stop = True
        tasks = asyncio.all_tasks()
        for it in tasks:
            it.cancel()
        asyncio.gather(*tasks, return_exceptions=True)
        log.get_logger().debug(f" engine cloese.. ")
