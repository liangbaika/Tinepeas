# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      request
# Author:    liangbaikai
# Date:      2020/12/21
# Desc:      there is a python file description
# ------------------------------------------------------------------
from dataclasses import dataclass
from typing import Callable


@dataclass
class Request:
    url: str
    callback: Callable = None
    method: str = 'get'
    timeout: float = None
    encoding: str = 'utf-8'
    header: dict = None
    cookies: dict = None
    # post data
    data: any = None
    # http requets kwargs..
    extras: dict = None
    # different callback functions can be delivered
    meta: dict = None
    # do not filter repeat url
    dont_filter: bool = False
    # no more than  max retry times  and retry is delay retry
    _retry: int = 0

    def __repr__(self):
        return f'url: {self.url}, retry:{self._retry}, callback: {self.callback}'

    @property
    def retry(self):
        return self._retry

    @retry.setter
    def retry(self, value):
        if isinstance(value, int):
            self._retry = value
        else:
            raise ValueError("need a int value")
