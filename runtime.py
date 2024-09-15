import socket 
import asyncio
from selector import Selector, EVENT_READ, EVENT_WRITE
from handler import Handler
from reactor import Reactor
from url_manager import url_manager
from read_config import *
from response_maker import ResponseMaker
from static_resources_manager import static
from logger import log,DBG,INF,ERR,WRN,Logger
from queue_manager import QueueManager



class Server:
    loop = asyncio.get_event_loop()
    que = QueueManager()
    selector = Selector()


    def __init__(self):

        or_sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        or_sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        or_sk.setblocking(False)
        or_sk.bind((IP,80))
        or_sk.listen(5)
        self.fd_or_sk = or_sk.fileno()
        self.selector.register(or_sk, EVENT_READ)
        # 定义无效路径回调
        def not_found(request,key,rest):
            return ResponseMaker(code=404)
        # 注册路由
        self.url = url_manager(unfound=not_found)
        # 注册默认静态资源回调
        self.url.add(STATIC_URL,static)

        self.log = Logger(self.que)



    def start(self,handlernum=int(CONF['handler_num'])):
        reactor_list = []
        handler_list = []
        handler_id = []

        reactor = Reactor(self.selector, self.que, self.fd_or_sk, self.loop)
        reactor_list.append(reactor.loop_reactor())

        for i in range(handlernum):
            handler_id.append(1000+i)
            handler = Handler(self.url, self.que, self.loop, handler_id[i]) 
            handler_list.append(handler.loop_handle())

        self.loop.run_until_complete(asyncio.gather(*reactor_list, *handler_list, self.log.loop()))
