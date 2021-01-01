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
from _multiprocessing import send
from asyncio import coroutine
from collections import deque, Iterable
from typing import Dict, Union, List

from smart import log
from smart.downloader import Downloader
from smart.item import Item
from smart.pipline import Piplines
from smart.request import Request
from smart.scheduler import Scheduler


class Engine:
    def __init__(self, spider, middlewire=None, pipline: Piplines = None):
        self.task_dict: Dict[str, asyncio.Task] = {}
        self.pip_task_dict: Dict[str, asyncio.Task] = {}
        self.middlewire = middlewire
        self.piplines = pipline
        self.scheduler = Scheduler()
        self.downloader = Downloader(self.scheduler, self.middlewire)
        self.spider = spider()
        self.request_generator_queue = deque()
        self.stop = False
        self.log = log.get_logger(name="smart-engine")

    def iter_request(self):
        while True:
            if not self.request_generator_queue:
                yield None
                continue
            request_generator = self.request_generator_queue[0]
            spider, real_request_generator = request_generator[0], request_generator[1]
            try:
                # execute and get a request from cutomer code
                # request=real_request_generator.send(None)
                request = next(real_request_generator)
                print(type(request))
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

    def _check_complete_pip(self, task):
        if task.cancelled():
            self.log.debug(f" a task canceld ")
            return
        if task and task.done() and task._key:
            result = task.result()
            if result:
                if hasattr(task, '_index'):
                    self._hand_piplines(result, task._index + 1)
            self.log.debug(f"a task done  ")
            self.pip_task_dict.pop(task._key)

    def _check_complete_callback(self, task):
        if task.cancelled():
            self.log.debug(f" a task canceld ")
            return
        if task and task.done() and task._key:
            self.log.debug(f"a task done  ")
            self.task_dict.pop(task._key)

    async def start(self):
        self.spider.on_start()
        # self.spider
        self.request_generator_queue.append((self.spider, iter(self.spider)))
        # self.request_generator_queue.append( iter(self.spider))
        # core  implenment
        while not self.stop:
            request_to_schedule = next(self.iter_request())
            if isinstance(request_to_schedule, Request):
                self.scheduler.schedlue(request_to_schedule)

            if isinstance(request_to_schedule, Item):
                self._hand_piplines(request_to_schedule)

            request = self.scheduler.get()
            can_stop = self._check_can_stop(request)
            # if request is None and not self.task_dict:
            if can_stop:
                # there is no request and the task has been completed.so ended
                self.log.debug(
                    f" here is no request and the task has been completed.so  engine will stop ..")
                self.stop = True
                break
            if isinstance(request, Request):
                self._ensure_future(request)

            resp = self.downloader.get()

            if resp is None:
                # let the_downloader can be scheduled, test 0.001-0.0006 is better
                await asyncio.sleep(0.0005)
                continue

            custome_callback = resp.request.callback
            if custome_callback:
                request_generator = custome_callback(resp)
                if request_generator:
                    self.request_generator_queue.append((custome_callback.__self__, request_generator))
                    # self.request_generator_queue.append( request_generator)

        self.spider.on_close()
        self.log.debug(f" engine stoped..")

    def close(self):
        # can make external active end engine
        self.stop = True
        tasks = asyncio.all_tasks()
        for it in tasks:
            it.cancel()
        asyncio.gather(*tasks, return_exceptions=True)
        self.log.debug(f" out called stop.. so engine close.. ")

    def _ensure_future(self, request: Request):
        # compatible py_3.6
        task = asyncio.ensure_future(self.downloader.download(request))
        key = str(uuid.uuid4())
        task._key = key
        self.task_dict[key] = task
        task.add_done_callback(self._check_complete_callback)

    def _handle_exception(self, spider, e):
        if spider:
            try:
                spider.on_exception_occured(e)
            except BaseException:
                pass

    def _check_can_stop(self, request):
        if request:
            return False
        if len(self.task_dict) > 0:
            return False
        if len(self.request_generator_queue) > 0:
            return False
        if self.downloader.response_queue.qsize() > 0:
            return False
        if len(self.pip_task_dict) > 0:
            return False
        return True

    def _hand_piplines(self, item, index=0):
        if self.piplines is None or len(self.piplines.piplines) <= 0:
            self.log.info("get a item but can not  find a piplinse to handle it so ignore it ")
            return

        if len(self.piplines.piplines) < index + 1:
            return

        pip = self.piplines.piplines[index][1]

        # for pipgroups in self.piplines.piplines:
        #     pip = pipgroups[1]
        if callable(pip):
            if not inspect.iscoroutinefunction(pip):
                task = asyncio.get_running_loop().run_in_executor(None, pip, item)
            else:
                task = asyncio.ensure_future(pip(item))
            key = str(uuid.uuid4())
            task._key = key
            task._index = index
            self.pip_task_dict[key] = task
            task.add_done_callback(self._check_complete_pip)
