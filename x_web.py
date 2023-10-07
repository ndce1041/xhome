# 环境: Linux


import socket
import re
import threading
import time
import sys
import logging
from select import epoll, EPOLLIN
from urllib.parse import unquote  # , quote


status_code = {
    200: 'OK',
    304: 'NOT MODIFIED',
    404: 'NOT FOUND',
    500: 'SERVER ERROR',
    501: 'NOT IMPLEMENTED',
    502: 'BAD GATEWAY',
    503: 'SERVICE UNAVAILABLE',
    504: 'GATEWAY TIMEOUT'
}



# TODO 适配windows 通用性主要是“\r\n”
if sys.platform.startswith('win'):
    ENTER = '\n'
    pass
elif sys.platform.startswith('linux'):
    ENTER = '\r\n'
    pass
else:
    logging.warning('未知系统###:%s,默认为linux' % sys.platform)
    ENTER = '\r\n'


logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s-%(asctime)s - %(filename)s[line:%(lineno)d]:%(message)s\r\n',
                    filename='./log/log %s.txt' % time.strftime('%Y-%m-%d-%h-%m'),
                    filemode='w')

sys.path.append('./web_frame')  # web框架根目录位置


class WSGIServer:
    def __init__(self):
        logging.info("#starting...#")
        self.conf_dict = dict
        self.app = None
        self.response_header = None
        self.setting()

        logging.debug('#创建监听套接字#')
        # 创建监听套接字
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定接口
        self.tcp_server_socket.bind(("", self.conf_dict["http_port"]))
        # 设置监听
        self.tcp_server_socket.listen(128)
        self.tcp_server_socket.setblocking(False)
        '''
        # 创建控制套接字
        self.master_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.master_socket.bind(("127.0.0.1", self.conf_dict["master_port"]))
        self.master_socket.setblocking(False)
        '''
        logging.debug('#注册epoll#')
        self.epl = epoll()
        # 注册到epoll中
        self.epl.register(self.tcp_server_socket.fileno(), EPOLLIN)
        # self.epl.register(self.master_socket.fileno(), EPOLLIN)

        logging.info('#start successfully#')

    # http服务器主逻辑
    def service_client(self, new_socket: socket.socket, id_s):
        # 用来给客户端返回数据
        img = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.ico']
        logging.info("NO.%d service is created" % id_s)
        while True:
            try:
                request = new_socket.recv(1024)
            except ConnectionResetError:
                logging.warning('链接超时')
                new_socket.close()
                logging.info("NO.%d service is closed" % id_s)
                break

            try:
                request = request.decode("utf-8")
            except UnicodeDecodeError:
                logging.warning('NO.%s: 返回编码错误###:%s' % (id_s, str(request)))

            if not request:
                new_socket.close()
                logging.info("NO.%d service is closed" % id_s)
                break
            # 分解请求
            path = ""
            target = ""
            filetype = ""
            response = ""
            try:
                path = request.split()[1]
            except:
                logging.warning('NO.%s: 收到空请求或者错误请求###:%s' % (id_s, str(request)))
                response = "HTTP/1.1 404 NOT FOUND".encode("utf-8")
                new_socket.send(response)
                break

            logging.info("NO.%d: request_head:" % id_s + str(path))
            ret = re.match(r"[^/]*/(\S*).*", path)
            if ret:
                target = ret.group(1)
                ret2 = re.match(r'.*(\..+).*', target)
                if ret2:
                    filetype = ret2.group(1)

            # 根据后缀名返回静态资源
            if filetype == ".css":
                try:
                    f = open('./static/css/' + target, "rb")
                except FileNotFoundError:
                    logging.warning("NO.%d: 404 filetype=.css target = %s " % (id_s, target))
                    response = "HTTP/1.1 404 NOT FOUND".encode("utf-8")
                else:
                    body = f.read()
                    f.close()
                    headers = "HTTP/1.1 200 ok\r\nContent-Length:%s\r\n\r\n" % len(body)
                    response = headers.encode("utf-8") + body
            elif filetype == ".js":
                try:
                    f = open('./static/js/' + target, "rb")
                except FileNotFoundError:
                    logging.warning("NO.%d: 404 filetype=.js target = %s " % (id_s, target))
                    response = "HTTP/1.1 404 NOT FOUND".encode("utf-8")
                else:
                    body = f.read()
                    f.close()
                    headers = "HTTP/1.1 200 ok\r\nContent-Length:%s\r\n\r\n" % len(body)
                    response = headers.encode("utf-8") + body
            elif filetype in img:
                try:
                    f = open('./static/image/' + target, "rb")
                except FileNotFoundError:
                    logging.warning("NO.%d: 404 filetype=img target = %s " % (id_s, target))
                    response = "HTTP/1.1 404 NOT FOUND".encode('utf-8')
                else:
                    body = f.read()
                    f.close()
                    headers = "HTTP/1.1 200 ok\r\nContent-Length:%s\r\nContent-type:image/%s\r\n\r\n" % (
                        len(body), filetype[1:])
                    response = headers.encode("utf-8") + body
            elif filetype == ".html":
                try:
                    f = open('./static/html/' + target, "rb")
                except FileNotFoundError:
                    logging.debug("NO.%d: return to web_frame" % id_s)
                    response = self.call_frame(Un_Request(request).get_all())
                    # 返回给web框架
                else:
                    body = f.read()
                    f.close()
                    headers = "HTTP/1.1 200 ok\r\nContent-Type: text/html;charset=utf-8\r\nConnection: " \
                              "keep-alive\r\nserver:x_web\r\nContent-Length:%s\r\n\r\n" % len(
                                body)
                    response = headers.encode("utf-8") + body
            else:
                logging.debug("NO.%d: return to web_frame" % id_s)
                response = self.call_frame(Un_Request(request).get_all())
                # 其他数据返回给web框架
                # 发送返回数据
            try:
                new_socket.send(response)
            except ConnectionResetError:
                logging.warning('链接超时###')

    # 主要调用逻辑
    def run(self):
        id_s = 0
        # key = 0
        while True:
            fd_list = self.epl.poll()
            for fd, event in fd_list:
                if fd == self.tcp_server_socket.fileno():
                    try:
                        new_socket, client_addr = self.tcp_server_socket.accept()
                    except:
                        logging.warning('套接字链接失败')
                        pass
                    else:
                        id_s += 1  # 给创建的套接字一个id
                        new_socket.setblocking(True)
                        logging.info("create a new_client NO.%dclient_address:%s" % (id_s, str(client_addr)))
                        p = threading.Thread(target=self.service_client, args=(new_socket, id_s))
                        p.start()
                        logging.info('当前线程数:%d' % threading.active_count())

            '''                        
                elif fd == self.master_socket.fileno():
                    try:
                        order = self.master_socket.recvfrom(1024)
                    except:
                        pass
                    else:
                        if order[0] == b"stop":
                            key = 1
                        else:
                            print(order)
            if key:
                break
                
            '''
        # self.tcp_server_socket.close()

    # 读取配置文件
    # TODO 增加路由功能1.静态资源 2.普通网站 3.带参数url 4.正则匹配url
    # TODO 更多选项移动至配置文件
    def setting(self):
        logging.info("#读取配置文件......#")
        conf = open('./xweb.conf', 'r')
        self.conf_dict = eval(conf.read())
        conf.close()
        frame = __import__(self.conf_dict['WSGIMod'])
        self.app = getattr(frame, self.conf_dict['WSGIFunction'])

    # WSGI 调用web框架返回head body
    def call_frame(self, request_dict):
        # request_dict 解析函数处理后返回的字典
        response_body = self.app(request_dict, self.start_response)
        if type(response_body) == str:
            response_body = response_body.encode('utf-8')

        self.response_header += 'content-length:%s\r\n\r\n' % len(response_body)

        return self.response_header.encode('utf-8') + response_body

    # WSGI 传入接收head函数
    def start_response(self, state: str, headers: list):
        self.response_header = "HTTP/1.1 %s\r\n" % state
        for temp in headers:
            self.response_header += "%s:%s\r\n" % (temp[0], temp[1])

    # 控制器监听
    '''
    def web_stop(self):
        try:
            order, address = self.master_socket.recvfrom(1024)
            print('b')
        except:
            pass
        else:
            logging.debug("receive order: " + order.decode("utf-8") + " | from:" + str(address))
            if order == b"stop":
                return 1
            else:
                print(order)
                return 0
'''


# 解析请求
# TODO 优化解析函数,请求头&响应头
class Un_Request:
    def __init__(self, content):
        self.content = content
        self.method = content.split()[0]
        self.path = content.split()[1]

        if ENTER*2 in content:
            self.body = content.split(ENTER*2, 1)[1]
        else:
            self.body = ''
        pass

    def parse_path(self) -> (str, dict):
        # url地址表单解析  返回基础地址和表单数据字典
        index = self.path.find('?')
        if index == -1:
            return self.path, {}
        else:
            path, query_string = self.path.split('?', 1)
            query = {}
            args = query_string.split('&')
            for arg in args:
                if '=' in arg:
                    k, v = arg.split('=', 1)
                    query[k] = unquote(v)  # 如果v包含中文会显示url编码 需要解码
                else:
                    logging.warning('请求头错误 错误行###:%s' % arg)
                    continue
            return path, query

    def headers(self) -> dict:
        # 返回请求头内容
        header_content = self.content.split('\r\n\r\n', 1)[0].split('\r\n')[1:]
        result = {}
        for line in header_content:
            k, v = line.split(': ')
            result[unquote(k)] = unquote(v)
        return result

    def get_all(self):
        requests_content = {}
        path, form = self.parse_path()
        headers = self.headers()
        requests_content['path'] = path
        requests_content['form'] = form
        requests_content['headers'] = headers
        requests_content['method'] = self.method
        requests_content['body'] = self.body
        return requests_content


# TODO 合成响应头
class response():

    def __init__(self, s_code=200,type=""):
        self.status_line = ()
        self.headers = {}




# 开始运行
def main():
    wsgi_server = WSGIServer()
    wsgi_server.run()


if __name__ == "__main__":
    main()
