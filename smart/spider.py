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


class Spider(ABC):
    name: str = f'smart-spider-{uuid.uuid4()}'
    state: int = 0
    start_urls: List[str] = []

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    @abstractmethod
    def parse(self, response: Response):
        ...

    def __iter__(self):
        yield from self.start_requests()
