# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      response
# Author:    liangbaikai
# Date:      2020/12/21
# Desc:      there is a python file description
# ------------------------------------------------------------------
import json
from dataclasses import dataclass
from typing import List, Dict, Union, Any

from jsonpath import jsonpath
from parsel import Selector, SelectorList

from smart.tool import get_index_url
from .request import Request


@dataclass
class Response:
    body: bytes
    status: int
    request: Request = None
    headers: dict = None
    cookies: dict = None
    _selector: Selector = None

    def xpath(self, xpath_str) -> Union[SelectorList]:
        """
        个别html可能不兼容 导致无法搜索到结果
        :param xpath_str: xpath str
        :return: SelectorList
        """
        return self.selector.xpath(xpath_str)

    def css(self, css_str) -> Union[SelectorList]:
        return self.selector.css(css_str)

    def re(self, partern, replace_entities=True) -> List:
        return self.selector.re(partern, replace_entities)

    def re_first(self, partern, default=None, replace_entities=True) -> Any:
        return self.selector.re_first(partern, default, replace_entities)

    def json(self) -> Dict:
        return json.loads(self.text)

    def jsonpath(self, jsonpath_str) -> List:
        return jsonpath(self.json(), jsonpath_str)

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

    def get_base_url(self):
        return get_index_url(self.url)

    def urljoin(self, url):
        if url is None or url == '':
            raise ValueError("urljoin  url can not be empty")
        if url.startswith("http"):
            return url
        else:
            basr_url = self.get_base_url()
            if url.startswith("/"):
                return basr_url + url
            else:
                return basr_url + "/" + url
