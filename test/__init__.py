import asyncio

from smart.middlewire import Middleware

middleware2 = Middleware()

total_res = 0
succedd = 0


@middleware2.request(1)
async def print_on_request(spider_ins, request):
    request.metadata = {"url": request.url}
    global total_res
    total_res += 1
    print(f"requesssst: {request.metadata}")
    print(f"total_res: {total_res}")

    # Just operate request object, and do not return anything.


@middleware2.response
def print_on_response(spider_ins, request, response):
    if response and 0<response.status<=200:
        global succedd
        succedd += 1
    print(f"response0: {response.status}")
    print(f"succedd: {succedd}")


