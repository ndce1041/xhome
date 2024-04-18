
import select
import socket
import platform
import collections
        
EVENT_READ = 1
EVENT_WRITE = 2
EVENT_ERROR = 3

class Selector:
    # 链接池


    pf = platform.system()

    Timeout = 20
    fd_key = {}
    selectkey = collections.namedtuple('selectkey',['fileobj','fd','events','data'])

    def __init__(self,short=False):


        # short 为True时一旦套接字事件发生就立即剔除
        # short 为False时需要外部调用函数剔除

        if self.pf == 'Windows':


            self.selector = select.select

            def add_fd(fd,key):
                self.fd_key[fd] = key
                


        elif self.pf == 'Linux':

            self.selector = select.epoll()
            def add_fd(sk,mask):
                # TODO: 未完成
                fd = sk.fileno()
                self.fd_key[sk] = mask

        self.add_fd = add_fd

    def fileno(self,obj):
        if type(obj) == int:
            return obj
        else:
            return obj.fileno()

    def register(self,sk,mask,data=None):
        # 判断参数是否合法
        if not isinstance(sk,socket.socket) or not mask in [EVENT_READ,EVENT_WRITE,EVENT_ERROR]:
            raise Exception('参数错误')
        
        key = self.selectkey(sk,sk.fileno(),mask,data)

        self.add_fd(sk.fileno(),key)

    def unregister(self,sk):
        if self.pf == 'Windows':
            self.fd_key.pop(self.fileno(sk))
        elif self.pf == 'Linux':
            self.selector.unregister(self.fileno(sk))

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
            
            # print(self.Read_fds)
            # print('R',R)
            # print('W',W)
            # print('E',E)
            # print('ans',ans)
            # print(len(self.fd_key))

            if R:
                ans += [self.fd_key[r] for r in R]
            if W:
                ans += [self.fd_key[w] for w in W]
            if E:
                ans += [self.fd_key[e] for e in E]
            
            # if R:
            #     ans += [self.fd_to_socket[r] for r in R]
            # if W:
            #     ans += [self.fd_to_socket[w] for w in W]
            # if E:
            #     ans += [self.fd_to_socket[e] for e in E]

            print('ans',ans)
            return ans
                    
        elif self.pf == 'Linux':
            return self.selector.poll(timeout)
        
    def close(self):
        self.selector.close()
        