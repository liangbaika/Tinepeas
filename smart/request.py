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
    timeout: float = 10.0
    encoding: str = 'utf-8'
    header: dict = None
    cookies: dict = None
    # post 数据
    data: any = None
    # request内的其他请求参数 比如 proxy  等
    extras: dict = None
    # 不同的回调函数可以借此传递数据
    meta: dict = None
    dont_filter: bool = False
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
