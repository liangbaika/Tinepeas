# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      response
# Author:    liangbaikai
# Date:      2020/12/21
# Desc:      there is a python file description
# ------------------------------------------------------------------
import json
from dataclasses import dataclass

from .selector import Selector
from .request import Request


@dataclass
class Response:
    body: bytes = None
    status: int = -1
    request: Request = None
    _selector: Selector = None
    status: int = 200


    def json(self):
        return json.loads(self.body)

    @property
    def selector(self):
        if not self._selector:
            self._selector = Selector(self.body.decode(self.encoding))
        return self._selector

    def xpath(self, xpath_str):
        return self.selector.xpath(xpath_str)

    @property
    def url(self):
        return self.request.url

    @property
    def meta(self):
        return self.request.meta

    @property
    def encoding(self):
        return self.request.encoding
