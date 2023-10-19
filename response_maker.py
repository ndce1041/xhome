"""
用于生成响应的模块
"""
import time

STATUS_CODE= {
    200: 'OK',
    304: 'NOT MODIFIED',
    404: 'NOT FOUND',
    500: 'SERVER ERROR',
    501: 'NOT IMPLEMENTED',
    502: 'BAD GATEWAY',
    503: 'SERVICE UNAVAILABLE',
    504: 'GATEWAY TIMEOUT'
}

class ResponseMaker:
    global PROTOCOL

    def __init__(self,code=200):
        self.response_head = {
            'Content-Type': 'text/html' ,
            'charset': 'utf-8',  # Content-Type: text/html; charset=utf-8  要合在一起
            'Server': 'XHome',
            "Content-Encoding": "gzip",
            "Date": time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()),
        }
        self.response_body = ''
        self.cange_cookie = {}

        self.first_line = PROTOCOL + ' ' + str(code) + ' ' + STATUS_CODE[code]


    def set_head(self,key,value):
        self.response_head[key] = value

    def set_cookie(self,key,value):
        """
        set_cookie关键字一条只能设置一个cookie
        注意拼接时key & value需要转换为字符串
        """
        if type(key) == str:
            self.cange_cookie[key] = value
        elif type(key) == dict:
            self.cange_cookie.update(key)
        elif type(key)==list & type(value)==list:
            if len(key) != len(value):
                raise Exception('key和value长度不一致')
            for i in range(len(key)):
                self.cange_cookie[key[i]] = value[i]
        else:
            raise Exception('set_cookie参数错误')
        

    def set_body(self,body):
        self.response_body = body

    def __str__(self):
        # TODO 未完成拼接response
        return str(self.response_head) + '\r\n\r\n' + str(self.response_body)
