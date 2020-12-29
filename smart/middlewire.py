# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      middlewire
# Author:    liangbaikai
# Date:      2020/12/28
# Desc:      there is a python file description
# ------------------------------------------------------------------
from copy import copy
from functools import wraps
from typing import Union, Callable

class Middleware:
    def __init__(self):
        # request middleware
        self.request_middleware = []
        # response middleware
        self.response_middleware = []

    def request(self, order_or_func: Union[int, Callable]):
        def outWrap(func):
            """
            Define a Decorate to be called before a request.
            eg: @middleware.request
            """
            middleware = func

            @wraps(middleware)
            def register_middleware(*args, **kwargs):
                self.request_middleware.append((order_or_func, middleware))
                self.request_middleware = sorted(self.request_middleware, key=lambda key: key[0])
                return middleware

            return register_middleware()

        if callable(order_or_func):
            cp_order = copy(order_or_func)
            order_or_func = 0
            return outWrap(cp_order)
        return outWrap

    def response(self, order_or_func: Union[int, Callable]):
        def outWrap(func):
            """
            Define a Decorate to be called before a request.
            eg: @middleware.request
            """
            middleware = func

            @wraps(middleware)
            def register_middleware(*args, **kwargs):
                self.response_middleware.append((order_or_func, middleware))
                self.response_middleware = sorted(self.response_middleware, key=lambda key: key[0], reverse=True)
                return middleware

            return register_middleware()

        if callable(order_or_func):
            cp_order = copy(order_or_func)
            order_or_func = 0
            return outWrap(cp_order)
        return outWrap
