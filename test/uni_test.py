# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      uni_test
# Author:    liangbaikai
# Date:      2021/1/5
# Desc:      there is a python file description
# ------------------------------------------------------------------
import copy
from dataclasses import asdict, fields

from smart.request import Request
from smart.response import Response
from smart.tool import get_domain, get_index_url


class TestClassOne(object):
    def test_response(self):
        request = Request("http://www.ocpe.com.cn/nengyuanjingji/zf/2020-08-29/3785.html")
        request.encoding = "utf-8"
        with open("test.html", "rb") as f:
            data = f.read()
            # data='{"code":200,"msg":"success","data":{"SYS_NAME":"职业院校综合管理与内部质量诊断与改进平台","LOGO":"/dfs/2020/11/05/20201105143318-47f7d6e3ca5637b23468330cab0ec0f3.jpg","BACKGROUND":"/dfs/2020/10/19/20201019194723-cdec006aef30e1e8313ac25eb2b71e38.png"}}'
            response = Response(data, 200, request)
            res = response.xpath("//div[@class='xwt_a']//a/text()").getall()
            print(res)




if __name__ == '__main__':
    TestClassOne().test_response()
