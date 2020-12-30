# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      downloader
# Author:    liangbaikai
# Date:      2020/12/21
# Desc:      there is a python file description
# ------------------------------------------------------------------
import asyncio
import inspect
from asyncio import Queue, QueueEmpty
from contextlib import suppress
from typing import Optional
import aiohttp
from concurrent.futures import TimeoutError

from smart import log
from smart.middlewire import Middleware
from smart.response import Response
from smart.scheduler import Scheduler
from .request import Request


class Downloader:

    def __init__(self, scheduler: Scheduler, middwire: Middleware = None):
        self.scheduler = scheduler
        self.middwire = middwire
        self.response_queue: asyncio.Queue = Queue()
        #  the file handle opens too_much to report an error
        self.semaphore = asyncio.Semaphore(1000)
        # starting from 0
        self.max_retry = 3

    async def download(self, request: Request):
        if request and request.retry >= self.max_retry:
            # reached max retry times
            log.get_logger().error(f'reached max retry times... {request}')
            return
        request.retry = request.retry + 1
        # when canceled
        loop = asyncio.get_running_loop()
        if loop.is_closed() or not loop.is_running():
            log.get_logger().warning(f'loop is closed in download')
            return
        with suppress(asyncio.CancelledError):
            async  with self.semaphore:
                await self._beforeFetch(request)

                fetch = self.fetch
                iscoroutinefunction = inspect.iscoroutinefunction(fetch)
                # support sync or async request
                if iscoroutinefunction:
                    response = await fetch(request)
                else:
                    log.get_logger().debug(f'fetch may be an snyc func  so it will run in executor ')
                    response = await asyncio.get_event_loop() \
                        .run_in_executor(None, fetch, request)

                await self._afterFetch(request, response)

        if response:
            response.__spider__ = request.__spider__
            await self.response_queue.put(response)

    def get(self) -> Optional[Response]:
        try:
            resp = self.response_queue.get_nowait()
        except QueueEmpty:
            return None
        return resp

    async def fetch(self, request: Request) -> Response:
        async with aiohttp.ClientSession() as clicnt:
            try:
                log.get_logger().debug(f'url {request.url} will send a request to fetch resource ..')
                resp = await clicnt.request(request.method,
                                            request.url,
                                            timeout=request.timeout or 10,
                                            headers=request.header or {},
                                            cookies=request.cookies or {},
                                            data=request.data or {},
                                            **request.extras or {}
                                            )
                byte_content = await resp.read()
            except TimeoutError as e:
                # delay retry
                self.scheduler.schedlue(request)
                log.get_logger().debug(
                    f'req  to fetch is timeout now so this req will dely to sechdule for retry {request.url}')
                return
            except asyncio.CancelledError as e:
                log.get_logger().error(f' task is cancel..')
                return
            except BaseException as e:
                log.get_logger().error(f'occured some exception in downloader e:{e}')
                return
        headers = {}
        if resp.headers:
            headers = {k: v for k, v in resp.headers.items()}
        response = Response(body=byte_content, request=request,
                            headers=headers,
                            cookies=resp.cookies,
                            status=resp.status)

        return response

    async def _beforeFetch(self, request):
        if self.middwire and len(self.middwire.request_middleware) > 0:
            for item_tuple in self.middwire.request_middleware:
                user_func = item_tuple[1]
                if callable(user_func):
                    if inspect.iscoroutinefunction(user_func):
                        res = await user_func(request.__spider__, request)
                    else:
                        res = await asyncio.get_event_loop() \
                            .run_in_executor(None, user_func, request.__spider__, request)

    async def _afterFetch(self, request, response):
        if response and self.middwire and len(self.middwire.response_middleware) > 0:
            for item_tuple in self.middwire.response_middleware:
                if callable(item_tuple[1]):
                    if inspect.iscoroutinefunction(item_tuple[1]):
                        res = await item_tuple[1](request.__spider__, request, response)
                    else:
                        res = await asyncio.get_event_loop() \
                            .run_in_executor(None, item_tuple[1], request.__spider__, request, response)

    # def fetch(self, request: Request) -> Response:
    #     try:
    #         res = requests.get(request.url,
    #                            timeout=request.timeout or 3 ,
    #                            )
    #     except Exception as e:
    #         return
    #     response = Response(body=res.content, request=request,
    #                         headers=res.headers,
    #                         cookies=res.cookies,
    #                         status=res.status_code)
    #     return response
