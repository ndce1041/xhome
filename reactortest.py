import reactor
import asyncio
from selector import Selector,EVENT_READ
import socket

selector = Selector()
or_sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
or_sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
or_sk.setblocking(False)
or_sk.bind(('0.0.0.0',80))
or_sk.listen(5)

fd_or_sk = or_sk.fileno()
loop = asyncio.get_event_loop()

selector.register(or_sk,EVENT_READ)
que = asyncio.Queue()
react = reactor.reactor(selector,que,fd_or_sk,loop)

loop.run_until_complete(react.loop_reactor())
