# 负责接收socket,并且注册到selector中,并将可读socket放入queue中

import socket
import asyncio
from selector import Selector,EVENT_READ
from logger import log,ERR,INF,WRN,DBG



class Reactor:

    def __init__(self,selector:Selector,queue,oringin_socket:int,loop:asyncio.AbstractEventLoop,handler_id:list):
        try:
            self.handler_id = handler_id

            self.selector = selector
            self.qm = queue
            self.o_skfd = oringin_socket
            #self.loop = asyncio.get_event_loop()
            self.loop = loop
            self.log = log(self.qm)
            self.log.log(DBG,'Reactor init success')

            ### TODO
            self.sdtopic = self.qm.new_topic('shutdown')





        except Exception as e:
            self.log.log(ERR,'Reactor init error:'+e)

    async def accept(self,key:Selector.selectkey):
        # self.log.log(DBG,'New connection accepted')
        if self.o_skfd == key.fd:
            try:
                # self.log.log(DBG,'New client')
                new_socket, client_addr = await self.loop.sock_accept(key.fileobj)
                new_socket.setblocking(False)
                self.selector.register(new_socket, EVENT_READ)
            except Exception as e:
                print(e)
        else:
            # self.log.log(INF,'new data received')
            self.selector.unregister(key.fileobj)  # 剔除否则循环触发事件
            self.qm.put_task(key)
            # self.log.log(DBG,'new data put into queue' + str(self.qm.task_queue.qsize()))
            # print(self.queue.qsize())

    async def loop_reactor(self):
        while True:
            event = self.selector.select(0)  # 0表示不阻塞
            # await asyncio.sleep(0.1)
            if event:
                for key in event:
                    await self.accept(key)
            else:
                pass


            # TODO 通过队列管理处理器数量

            """
                topic: shotdown
                (1,time,id)
            """

