import socket
import re
import time
import sys
import logging
from urllib.parse import unquote,urlparse  # , quote
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

from analysis_request import AnalysisRequest

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

# 获取当前文件路径
PATH = sys.path[0]

LOG = True
DEBUG = logging.debug
INFO = logging.info
WARNING = logging.warning
ERROR = logging.error
if LOG:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s-%(asctime)s - %(filename)s[line:%(lineno)d]:%(message)s\r\n',
                        filename='%s.txt' % time.strftime('%Y-%m-%d'),
                        filemode='w',
                        encoding='utf-8')
else:
    logging.basicConfig(level=logging.WARNING,
                        format='%(levelname)s-%(asctime)s - %(filename)s[line:%(lineno)d]:%(message)s\r\n',
                        filename='%s.txt' % time.strftime('%Y-%m-%d'),
                        filemode='w',
                        encoding='utf-8')

sys.path.append('./web_frame')  # web框架根目录位置 方便导入

# 区别linux 和 windows
# if sys.platform.startswith('win'):
#     ENTER = '\n'

# elif sys.platform.startswith('linux'):
#     ENTER = '\r\n'

# else:
#     WARNING('未知系统###:%s,默认为linux' % sys.platform)
#     ENTER = '\r\n'

"""
key = [socket,fd,events,data]  套接字,文件描述符,事件,数据
windows 无法处理文件描述符
"""

PORT = 80
PROTOCOL = 'HTTP/1.1'
IP = "127.0.0.1"

# 导入config文件
DEBUG("#读取配置文件......#")

try:
    with open(PATH + '/xweb.conf', 'r',encoding="utf-8") as conf:
        conf_dict = eval(conf.read())
except Exception as e:
    ERROR('配置文件读取失败,请检查配置文件是否存在或者格式是否正确',e)
    exit(1)
else:
    # TODO 添加静态资源路径
    if "http_port" in conf_dict:
        PORT = conf_dict['http_port']
        print(PORT)
    if "network_protocol" in conf_dict:
        PROTOCOL = conf_dict['network_protocol']
        print(PROTOCOL)
    if "IP" in conf_dict:
        IP = conf_dict['IP']
        print(IP)
    if "TIMEOUT" in conf_dict:
        TIMEOUT = conf_dict['TIMEOUT']
        print(TIMEOUT)
    if "static_path" in conf_dict:
        STATIC_PATH = conf_dict['static_path']
        print(STATIC_PATH)
    if "static_url" in conf_dict:
        STATIC_URL = conf_dict['static_url'].strip('/')
        print(STATIC_URL)

INFO('配置文件读取成功,端口:%s,协议:%s,IP:%s' % (PORT, PROTOCOL, IP))

class Server:
    def __init__(self):
        DEBUG("#初始化服务器......#")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.socket.setblocking(False)
        self.socket.bind((IP, PORT))
        self.socket.listen(128)
        self.selector = DefaultSelector()
        # io

        self.selector.register(self.socket, EVENT_READ, self.accept)
        # windows 无法传入文件描述符
        INFO('服务器初始化成功,端口:%s,协议:%s,IP:%s' % (PORT, PROTOCOL, IP))

    def accept(self,key):
        if self.socket.fileno() == key.fd:
            new_socket, client_addr = self.socket.accept()
            DEBUG('服务器接收到新连接,IP:%s' % str(client_addr))
            #new_socket.setblocking(False)
            # 
            self.selector.register(new_socket, EVENT_READ, self.accept)
        else:

            self.recv_data(key)
            # TODO 处理数据
            # TODO 路由采用回调函数
            response = "a"
            ####
            key[0].send(response.encode('utf-8'))
            self.selector.unregister(key[0])
            key[0].close()

    def recv_data(self, key):
        # 接收数据
        INFO("接收数据中...")
        new_socket = key.fileobj
        client_addr = new_socket.getpeername()
        recv_data = b''
        while True:
            new_socket.setblocking(False)
            try:
                recv_data += new_socket.recv(1024)
            except Exception as e:
                INFO('数据接收中断 IP:%s' % str(client_addr))
                # 数据传输完成  大概
                break
            else:
                if len(recv_data) == False:  # 收到数据小于等于0 说明客户端断开连接
                    WARNING('客户端断开连接 IP:%s' % str(client_addr))
                    INFO(recv_data.decode('utf-8'))
                    self.selector.unregister(new_socket.fileno())
                    new_socket.close()
                    raise Exception('客户端断开连接%s' % (str(client_addr)))
        

        # TODO解码
        try:
            recv_data = recv_data.decode('utf-8')
        except:
            ERROR('数据解码失败')
            raise Exception('数据解码失败%s' % str(client_addr) )
        DEBUG('接收到数据')

        # 分割数据
        try:
            self.request_head = AnalysisRequest(recv_data)
        except Exception as e:
            ERROR('请求头解析失败')
            print(e)
            raise Exception('请求头解析失败%s' % str(client_addr) )
        
        # 第一行解析成功说明是有效的请求头
        DEBUG('请求头解析成功')




    def loop(self):
        while True:
            print('等待事件发生...')
            events = self.selector.select(timeout=TIMEOUT)
            for key, mask in events:
                # 获取key[0]套接字的ip和端口
                print(key)
                try:
                    ip = key[0].getpeername()
                    print("套接字响应",ip)
                except:
                    pass
            
                callback = key.data
                callback(key)
                # try:
                #     callback(key)
                # except Exception as e:
                #     ERROR('套接字异常中断:%s' % str(e))
                

        




