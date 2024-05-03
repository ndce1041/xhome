import select
import socket
import platform
import collections
        
EVENT_READ = 0
EVENT_WRITE = 1
EVENT_ERROR = 2

class Selector:
    # 链接池
    pf = platform.system()
    Timeout = 1
    fd_key = {}
    selectkey = collections.namedtuple('selectkey',['fileobj','fd','events','data'])

    def __init__(self):
        if self.pf == 'Windows':
            self.selector = select.select
                
        elif self.pf == 'Linux':
            self.selector = select.epoll()
            self.epoll_event = (select.EPOLLIN , select.EPOLLOUT , select.EPOLLERR)

    def register(self,sk,mask,data=None):
        # 判断参数是否合法
        if not isinstance(sk,socket.socket) or not mask in [EVENT_READ,EVENT_WRITE,EVENT_ERROR]:
            raise Exception('参数错误')
        key = self.selectkey(sk,sk.fileno(),mask,data)
        self.fd_key[sk.fileno()] = key
        if self.pf == 'Linux':
            self.selector.register(sk.fileno(),self.epoll_event[mask])

    def unregister(self,sk):
        self.fd_key.pop(sk.fileno())
        if self.pf == 'Linux':
            self.selector.unregister(sk.fileno())

    def select(self,timeout=Timeout):
        if self.pf == 'Windows':
            ans = []
            R,W,E = [],[],[]
            for fd,key in self.fd_key.items():
                if key[2] == EVENT_READ:
                    R.append(fd)
                elif key[2] == EVENT_WRITE:
                    W.append(fd)
                elif key[2] == EVENT_ERROR:
                    E.append(fd)
            R,W,E = select.select(R,W,E,timeout)
            if R:
                ans += [self.fd_key[r] for r in R]
            if W:
                ans += [self.fd_key[w] for w in W]
            if E:
                ans += [self.fd_key[e] for e in E]
            return ans
                    
        elif self.pf == 'Linux':
            ans = self.selector.poll(timeout)
            return [self.fd_key[i[0]] for i in ans]
    
    def close(self):
        if self.pf == 'Linux':
            self.selector.close()
        elif self.pf == 'Windows':
            pass    