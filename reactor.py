# 负责接收socket,并且注册到selector中,并将可读socket放入queue中

import socket
import asyncio
from selector import Selector,EVENT_READ



class Reactor:

    def __init__(self,selector:Selector,queue:asyncio.queues,oringin_socket:int,loop:asyncio.AbstractEventLoop):
        try:
            self.selector = selector
            self.queue = queue
            self.o_skfd = oringin_socket
            #self.loop = asyncio.get_event_loop()
            self.loop = loop
        except Exception as e:
            print('error')

    async def accept(self,key:Selector.selectkey):
        if self.o_skfd == key.fd:
            try:
                new_socket, client_addr = await self.loop.sock_accept(key.fileobj)
                new_socket.setblocking(False)
                self.selector.register(new_socket, EVENT_READ)
            except Exception as e:
                print(e)
        else:
            self.selector.unregister(key.fileobj)  # 剔除否则循环触发事件
            await self.queue.put(key)
            print(self.queue.qsize())

    async def loop_reactor(self):
        while True:
            event = self.selector.select(0)  # 0表示不阻塞
            await asyncio.sleep(0.1)
            if event:
                for key in event:
                    await self.accept(key)
            else:
                pass