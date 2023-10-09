import socket
import re
import time
import sys
import logging
from urllib.parse import unquote,urlparse  # , quote
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

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

TIMEOUT = 20


LOG = True
DEBUG = logging.debug
INFO = logging.info
WARNING = logging.warning
ERROR = logging.error
if LOG:
    logging.basicConfig(level=DEBUG,
                        format='%(levelname)s-%(asctime)s - %(filename)s[line:%(lineno)d]:%(message)s\r\n',
                        filename='./log/log %s.txt' % time.strftime('%Y-%m-%d'),
                        filemode='w')
else:
    logging.basicConfig(level=WARNING,
                        format='%(levelname)s-%(asctime)s - %(filename)s[line:%(lineno)d]:%(message)s\r\n',
                        filename='./log/log %s.txt' % time.strftime('%Y-%m-%d'),
                        filemode='w')

sys.path.append('./web_frame')  # web框架根目录位置 方便导入

# 区别linux 和 windows
# if sys.platform.startswith('win'):
#     ENTER = '\n'

# elif sys.platform.startswith('linux'):
#     ENTER = '\r\n'

# else:
#     WARNING('未知系统###:%s,默认为linux' % sys.platform)
#     ENTER = '\r\n'



PORT = 80
PROTOCOL = 'HTTP/1.1'
IP = "127.0.0.1"

# 导入config文件
DEBUG("#读取配置文件......#")

try:
    with open('./xweb.conf', 'r') as conf:
        conf_dict = eval(conf.read())
except:
    ERROR('配置文件读取失败,请检查配置文件是否存在或者格式是否正确')
    exit(1)
else:
    if "http_port" in conf_dict:
        PORT = conf_dict['http_port']
    if "network_protocol" in conf_dict:
        PROTOCOL = conf_dict['network_protocol']
    if "IP" in conf_dict:
        IP = conf_dict['IP']
    if "TIMEOUT" in conf_dict:
        TIMEOUT = conf_dict['TIMEOUT']

INFO('配置文件读取成功,端口:%s,协议:%s,IP:%s' % (PORT, PROTOCOL, IP))


class Server:
    def __init__(self):
        DEBUG("#初始化服务器......#")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((IP, PORT))
        self.socket.listen(128)
        self.socket.setblocking(False)
        # io
        self.selector = DefaultSelector()
        self.selector.register(self.socket.fileno(), EVENT_READ, self.accept)
        INFO('服务器初始化成功,端口:%s,协议:%s,IP:%s' % (PORT, PROTOCOL, IP))

    def accept(self,key):
        if self.socket.fileno() == key.fd:
            new_socket, client_addr = self.socket.accept()
            DEBUG('服务器接收到新连接,IP:%s' % str(client_addr))
            new_socket.setblocking(False)
            self.selector.register(new_socket.fileno(), EVENT_READ, self.recv_data, timeout=TIMEOUT)
        else:

            data = self.recv_data(key)
            # TODO 处理数据
            response = data
            ####

            key.fileobj.send(response.encode('utf-8'))
            self.selector.unregister(key.fd)
            key.fileobj.close()

    def recv_data(self, key)->dict:
        # 接收数据
        new_socket = key.fileobj
        client_addr = new_socket.getpeername()
        recv_data = b''
        # TODO 循环接受数据
        while True:
            try:
                recv_data += new_socket.recv(1024)
            except Exception as e:
                WARNING('客户端断开连接 IP:%s' % str(client_addr))
                self.selector.unregister(new_socket.fileno())
                new_socket.close()
                raise Exception('客户端断开连接%s%s' % (str(client_addr), str(e)))
            else:
                if len(recv_data) == False:  # 收到数据小于等于0 数据接收完毕
                    break
        
        # TODO解码
        # try:
        #     recv_data = recv_data.decode('utf-8')
        # except:
        #     recv_data = recv_data.decode('gbk')
        # DEBUG('接收到数据')

        # 分割数据

        if "\r\n" in recv_data:
            ENTER = "\r\n"
        else:
            ENTER = "\n"
        data_head,data_body = recv_data.split(ENTER*2)

        # 解析请求头
        request_head = {}
        request_head_list = data_head.split(ENTER)
        try:
            request_head['method'],request_head['url'],request_head['protocol'] = request_head_list[0].split(' ')
        except:
            ERROR('请求头解析失败')
            raise Exception('请求头解析失败%s/t%s' % str(client_addr) % str(request_head_list[0]))
        
        # 第一行解析成功说明是有效的请求头

        return recv_data




    def loop(self):
        while True:
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                try:
                    callback(key)
                except Exception as e:
                    ERROR('套接字异常中断:%s' % str(e))
                

        



if __name__ == "__main__":
    server = Server()
    server.loop()


