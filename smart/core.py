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
from smart.request import Request
from smart.scheduler import Scheduler


class Engine:
    def __init__(self, spider, middlewire=None):
        self.task_dict: Dict[str, asyncio.Task] = {}
        self.middlewire = middlewire
        self.scheduler = Scheduler()
        self.downloader = Downloader(self.scheduler, self.middlewire)
        self.spider = spider()
        self.request_generator_queue = deque()
        self.stop = False

    def iter_request(self):
        while True:
            if not self.request_generator_queue:
                yield None
                continue
            request_generator = self.request_generator_queue[0]
            spider, real_request_generator = request_generator[0], request_generator[1]
            try:
                # execute and get a request from cutomer code
                request = next(real_request_generator)
                request.__spider__ = spider
            except StopIteration:
                self.request_generator_queue.popleft()
                continue
            except Exception as e:
                # 可以处理异常
                self.request_generator_queue.popleft()
                self._handle_exception(spider, e)
                continue
            yield request

    def check_task_done(self):
        # for key, task in list(self.task_dict.items()):
        #     if task.done:
        #         self.task_dict.pop(key)
        if len(self.task_dict.items()) > 0:
            return False
        tasks = asyncio.Task.all_tasks()
        for t in tasks:
            print('##########1', t)
            print('##########2', asyncio.current_task())
            # if asyncio.current_task() == t:
            #     continue
            if not t.done():
                return False

        return True

    def check_complete_callback(self, task):
        if task.cancelled():
            log.get_logger().debug(f" a task canceld ")
            return
        if task and task.done() and task._key:
            log.get_logger().debug(f"a task done  ")
            self.task_dict.pop(task._key)

    async def start(self):
        self.spider.on_start()

        self.request_generator_queue.append((self.spider, iter(self.spider)))
        # self.request_generator_queue.append( iter(self.spider))
        # core  implenment
        while not self.stop:
            request_to_schedule = next(self.iter_request())
            if request_to_schedule:
                self.scheduler.schedlue(request_to_schedule)
            request = self.scheduler.get()
            check_can_stop = self.check_can_stop(request)
            # if request is None and not self.task_dict:
            if check_can_stop:
                # there is no request and the task has been completed.so ended
                log.get_logger().debug(
                    f" here is no request and the task has been completed.so  engine will stop ..")
                self.stop = True
                break
            if isinstance(request, Request):
                self._ensure_future(request)

            resp = self.downloader.get()

            if resp is None:
                # let the_downloader can be scheduled, test 0.001-0.0006 is better
                await asyncio.sleep(0.001)
                continue

            custome_callback = resp.request.callback
            if custome_callback:
                request_generator = custome_callback(resp)
                if request_generator:
                    self.request_generator_queue.append((custome_callback.__self__, request_generator))
                    # self.request_generator_queue.append( request_generator)

        self.spider.on_close()
        log.get_logger().debug(f" engine stoped..")

    def close(self):
        # can make external active end engine
        self.stop = True
        tasks = asyncio.all_tasks()
        for it in tasks:
            it.cancel()
        asyncio.gather(*tasks, return_exceptions=True)
        log.get_logger().debug(f" out called stop.. so engine close.. ")

    def _ensure_future(self, request: Request):
        # compatible py_3.6
        task = asyncio.create_task(self.downloader.download(request))
        key = str(uuid.uuid4())
        task._key = key
        self.task_dict[key] = task
        task.add_done_callback(self.check_complete_callback)

    def _handle_exception(self, spider, e):
        if spider:
            try:
                spider.on_exception_occured(e)
            except BaseException:
                pass

    def check_can_stop(self, request):
        if request:
            return False
        if len(self.task_dict) > 0:
            return False
        if len(self.request_generator_queue) > 0:
            return False
        if self.downloader.response_queue.qsize() > 0:
            return False

        return True
