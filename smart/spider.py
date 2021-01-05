# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      spider
# Author:    liangbaikai
# Date:      2020/12/21
# Desc:      there is a  abstract spider
# ------------------------------------------------------------------
from abc import ABC, abstractmethod
import uuid
from typing import List

from smart.request import Request
from smart.response import Response


class SpiderHook(ABC):

    def on_start(self):
        pass

    def on_close(self):
        pass

    def on_exception_occured(self, e: Exception):
        pass


class Spider(SpiderHook):
    name: str = f'smart-spider-{uuid.uuid4()}'

    # spider leaf state:  init | runing | paused | closed
    state: str = "init"

    start_urls: List[str] = []

    cutome_setting_dict = {
        # 请求延迟
        "req_delay": None,
        # 每个爬虫的请求并发数
        "req_per_concurrent": None,
        # 每个请求的最大重试次数
        "req_max_try": None,
        # 默认请求头
        "default_headers": None,
        # 根据响应的状态码 忽略以下响应
        "ignore_response_codes": None,
        "middleware_instance": None,
        "piplines_instance": None,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    @abstractmethod
    def parse(self, response: Response):
        ...

    def __iter__(self):
        yield from self.start_requests()
