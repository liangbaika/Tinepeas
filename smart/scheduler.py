# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      scheduler
# Author:    liangbaikai
# Date:      2020/12/21
# Desc:      there is a python file description
# ------------------------------------------------------------------
import asyncio
from asyncio import Queue
from collections import deque
from typing import Optional

from smart import log
from smart.request import Request

from abc import ABC, abstractmethod


class BaseDuplicateFilter(ABC):

    @abstractmethod
    def add(self, url):
        pass

    @abstractmethod
    def contains(self, url):
        pass

    @abstractmethod
    def length(self):
        pass


class SampleDuplicateFilter(BaseDuplicateFilter):

    def __init__(self):
        self.set_container = set()
        self.set_container = set()

    def add(self, url):
        if url:
            self.set_container.add(hash(url))

    def contains(self, url):
        if not url:
            return False
        if hash(url) in self.set_container:
            return True
        return False

    def length(self):
        return len(self.set_container)


class Scheduler:
    def __init__(self):
        self.request_queue = deque()
        self.duplicate_filter = SampleDuplicateFilter()

    def schedlue(self, request: Request):
        log.get_logger().debug(f"get a request {request} wating toschedlue ")
        if not request.dont_filter:
            _url = request.url + ":" + str(request.retry)
            if self.duplicate_filter.contains(_url):
                log.get_logger().debug(f"duplicate_filter filted ... url{_url} ")
                return
            self.duplicate_filter.add(_url)
        self.request_queue.append(request)

    def get(self) -> Optional[Request]:
        log.get_logger().debug(f"get a request to download task ")
        if self.request_queue:
            return self.request_queue.popleft()
        return None
