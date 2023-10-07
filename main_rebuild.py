import socket
import re
import threading
import time
import sys
import logging
from urllib.parse import unquote  # , quote

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
LOG = True
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
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
if sys.platform.startswith('win'):
    ENTER = '\n'
    pass
elif sys.platform.startswith('linux'):
    ENTER = '\r\n'
    from select import epoll, EPOLLIN
    pass
else:
    WARNING('未知系统###:%s,默认为linux' % sys.platform)
    ENTER = '\r\n'



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

INFO('配置文件读取成功,端口:%s,协议:%s,IP:%s' % (PORT, PROTOCOL, IP))


class Server:
    def __init__(self):
        DEBUG("#初始化服务器......#")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((IP, PORT))
        self.socket.listen(128)
        self.socket.setblocking(False)


        # epoll
        self.epoll = epoll()
        self.epoll.register(self.socket.fileno(), EPOLLIN)
        INFO('服务器初始化成功,端口:%s,协议:%s,IP:%s' % (PORT, PROTOCOL, IP))

    def recv_data(self, new_socket,client_addr):
        # 接收数据
        recv_data = b''
        while True:
            try:
                recv_data += new_socket.recv(1024)
            except:
                WARNING('客户端断开连接 IP:%s' % str(client_addr))
                new_socket.close()
                break
            else:
                if len(recv_data) == 0:
                    WARNING('客户端断开连接IP:%s' % str(client_addr))
                    new_socket.close()
                    break
        
        # 解码
        try:
            recv_data = recv_data.decode('utf-8')
        except:
            recv_data = recv_data.decode('gbk')
        DEBUG('接收到数据')

        # 分割数据
        data_head,data_body = recv_data.split(ENTER*2)
        DEBUG('数据分割完成')
        DEBUG('请求头:\r\n%s' % data_head)

        # 解析请求头
        data_head = data_head.split(ENTER)

        return recv_data


    def run(self):
        DEBUG("#服务器启动......#")
        while True:
            # 监听
            client_list = self.epoll.poll()
            for fd, event in client_list:
                if fd == self.socket.fileno():
                    # 新连接
                    new_socket, client_addr = self.socket.accept()
                    DEBUG('服务器接收到新连接,IP:%s' % str(client_addr))
                    # 接收数据
                    print(self.recv_data(new_socket,client_addr))
                    # t = threading.Thread(target=self.recv_data, args=(new_socket,client_addr))
                    # t.start()

        



if __name__ == "__main__":
    server = Server()
    server.run()


