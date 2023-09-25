# 用来解析请求头的
import re


def analysis(request):
    rule_request = "GET\s/(.*)\sHTTP/1.1"  # 请求内容正则
    req = re.match(rule_request, request, flags=0).group()
    return req

