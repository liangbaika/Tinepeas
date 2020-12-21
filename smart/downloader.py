# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      downloader
# Author:    liangbaikai
# Date:      2020/12/21
# Desc:      there is a python file description
# ------------------------------------------------------------------
import asyncio
from asyncio import Queue, QueueEmpty
from typing import Optional

import aiohttp
from concurrent.futures import TimeoutError
from smart.response import Response
from .request import Request


class Downloader:
    def __init__(self):
        self.response_queue: asyncio.Queue = Queue()

    async def download(self, request: Request):
        async with aiohttp.ClientSession() as clicnt:
            try:
                resp = await clicnt.request(request.method,
                                            request.url,
                                            headers=request.header,
                                            cookies=request.cookies,
                                            data=request.data,
                                            **request.extras
                                            )
            except TimeoutError as e:
                print(e)
                return
            byte_content = await resp.read()
        response = Response(body=byte_content, request=request, status=resp.status)
        response.raw_response = resp
        await self.response_queue.put(response)

    def get(self) -> Optional[Response]:
        try:
            response = self.response_queue.get_nowait()
        except QueueEmpty:
            return None
        return response
