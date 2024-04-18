import selector
import socket

Selector = selector.Selector()


or_sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
or_sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#self.socket.setblocking(False)
or_sk.bind(('0.0.0.0',80))
or_sk.listen(5)

fd_or_sk = or_sk.fileno()

print(isinstance(or_sk,socket.socket))
print(selector.EVENT_READ)
Selector.register(or_sk,selector.EVENT_READ)

while True:
    event = Selector.select(1)
    if event:
        for key in event:
            if key[0] == or_sk:
                newsk,addr = or_sk.accept()
                Selector.register(newsk,selector.EVENT_READ)
                print("accept")
            else:
                print("read")
                Selector.unregister(key[0])
    else:
        pass


    print("oneselect")