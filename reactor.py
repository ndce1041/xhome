# 负责接收socket,并且注册到selector中,并将可读socket放入queue中

import socket
import asyncio
from selector import Selector,EVENT_READ



class reactor:

    def __init__(self,selector:Selector,queue:asyncio.queues,oringin_socket:int):
        self.selector = selector
        self.queue = queue
        self.o_skfd = oringin_socket
        self.loop = asyncio.get_running_loop()


    async def accept(self,key:Selector.selectkey):
        if self.o_skfd == key.fd:
            new_socket, client_addr = await self.loop.sock_accept(key.fileobj)
            new_socket.setblocking(False)
            self.selector.register(new_socket, EVENT_READ)
        else:
            await self.queue.put(new_socket)

    async def loop_reactor(self):
        while True:
            event = self.selector.select(0)  # 0表示不阻塞
            if event:
                for key in event:
                    await self.accept(key)
            else:
                pass