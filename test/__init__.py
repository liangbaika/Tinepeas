from smart.middlewire import Middleware

middleware2 = Middleware()


@middleware2.request(1)
async def print_on_request(spider_ins, request):
    request.metadata = {"url": request.url}
    print(f"requesssst: {request.metadata}")
    # Just operate request object, and do not return anything.


@middleware2.response(-11)
def print_on_response22(spider_ins, request, response):
    print(f"response -11: {response.status}")


@middleware2.response
def print_on_response(spider_ins, request, response):
    print(f"response0: {response.status}")


def testmmmmmmmm():
    pass
