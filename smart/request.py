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
    header: dict
    cookies: dict
    data: any
    extras: dict
    callback: Callable
    method: str = 'get'
    meta: dict = None
    dont_filter: bool = False
    encoding: str = 'utf-8'

    def __repr__(self):
        return f'url: {self.url}, callback: {self.callback}'
