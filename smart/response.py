# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      response
# Author:    liangbaikai
# Date:      2020/12/21
# Desc:      there is a python file description
# ------------------------------------------------------------------
import json
import re
from dataclasses import dataclass

from .selector import Selector
from .request import Request


@dataclass
class Response:
    body: bytes = None
    request: Request = None
    headers:dict=None
    cookies:dict=None
    status: int = -1
    _selector: Selector = None

    def xpath(self, xpath_str):
        """
        个别html可能不兼容 导致无法搜索到结果
        :param xpath_str: xpath str
        :return: SelectorList
        """
        return self.selector.xpath(xpath_str)

    def re(self, partern, flags=0):
        return re.findall(partern, self.text, flags)

    def json(self):
        return json.loads(self.text)

    @property
    def selector(self):
        if not self._selector:
            self._selector = Selector(self.text)
        return self._selector

    @property
    def text(self):
        if not self.body:
            return None
        return self.body.decode(self.encoding)

    @property
    def url(self):
        return self.request.url

    @property
    def meta(self):
        return self.request.meta

    @property
    def encoding(self):
        return self.request.encoding
