import uuid
import asyncio
from typing import Dict
from collections import deque
from tinepeas.scheduler import Scheduler
from tinepeas.downloader import Downloader
from tinepeas.request import Request


class Core:
    def __init__(self, spider):
        self.request_generator_queue = deque()
        self.task_dict: Dict[uuid.UUID, asyncio.Task] = {}
        self.request_generator = self.iter_request()
        self.scheduler = Scheduler()
        self.stop = False
        self.spider = spider()

    def check_task_done(self):
        for key, task in list(self.task_dict.items()):
            if task.done:
                self.task_dict.pop(key)

    def iter_request(self):
        while True:
            if not self.request_generator_queue:
                yield None
                continue
            request_generator = self.request_generator_queue[0]
            try:
                request = next(request_generator)
            except StopIteration:
                self.request_generator_queue.popleft()
                continue
            yield request

    async def start(self):
        downloader = Downloader()
        self.request_generator_queue.append(iter(self.spider))
        while not self.stop:
            request_to_schedule = next(self.iter_request())
            if request_to_schedule:
                self.scheduler.schedule(request_to_schedule)
            request = self.scheduler.get()
            if request is None:
                if not self.task_dict:
                    break
            if isinstance(request, Request):
                task = asyncio.create_task(downloader.download(request))
                self.task_dict[uuid.uuid4()] = task
            resp = downloader.get()
            if not resp:
                await asyncio.sleep(0.005)
                continue
            print('get response of: ', resp.url)
            callback = resp.request.callback
            request_generator = callback(resp)
            if request_generator:
                self.request_generator_queue.append(request_generator)
            self.check_task_done()

        await asyncio.sleep(3)


if __name__ == '__main__':
    from spiders import ipspider
    core = Core(ipspider)
    asyncio.run(core.start())

