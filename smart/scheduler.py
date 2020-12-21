# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      scheduler
# Author:    liangbaikai
# Date:      2020/12/21
# Desc:      there is a python file description
# ------------------------------------------------------------------
from collections import deque
from typing import Optional

from smart.request import Request


class Scheduler:
    def __init__(self):
        self.request_queue = deque()

    def schedlue(self, request: Request):
        self.request_queue.append(request)

    def get(self) -> Optional[Request]:
        if self.request_queue:
            return self.request_queue.popleft()
        return None
