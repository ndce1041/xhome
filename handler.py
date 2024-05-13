import analysis_request
AnalysisRequest = analysis_request.AnalysisRequest
import asyncio
import response_maker
ResponseMaker = response_maker.ResponseMaker
import select
from logger import log,ERR,INF,WRN,DBG
import queue_manager


class Handler:

    def __init__(self,url,queue:queue_manager.QueueManager,loop: asyncio.AbstractEventLoop):
        self.url = url
        self.qm = queue
        self.loop = loop
        self.request = None
        self.flag = False # 用于标记套接字是否已经关闭

        self.log = log(self.qm)
        pass

    async def recv_data(self,key):
        # 接收数据
        # print('接收数据中...')
        sk = key[0]
        sk.setblocking(False)
        recv_data = b''
        while True:
            try:
                # print('recv_data')
                temp = await self.loop.sock_recv(sk,1024)
                # print(temp)
                recv_data += temp
                if temp == b'':  # 收到数据小于等于0 说明客户端断开连接
                    self.log.log(INF,'handler:客户端断开连接')
                    # print('recv_data close')
                    # 此时无论如何都不再处理
                    self.flag = True
                    break
                a,_,_ = select.select([sk],[],[],0)
                self.log.log(DBG,'handler:recv_data:select:%s'%str(a))
                if not a:
                    self.log.log(DBG,'handler:recv_data:select:break')
                    break
            except Exception as e:
                # 此时发送未知错误
                self.log.log(ERR,'handler:recv_data:未知错误:%s'%str(e))
                break
        
        # 分割数据
        try:
            if recv_data:
                self.request = AnalysisRequest(recv_data)
            # self.log.log(DBG,'handler:recv_data:AnalysisRequest success .... request:%s'%str(self.request["path"]))
            # self.log.log(DBG,self.url.url)
        except Exception as e:
            print(e)
            self.flag = True

            #raise Exception('请求头解析失败%s' % str(client_addr) )
        
        # 第一行解析成功说明是有效的请求头


    async def handle(self,key):
            ans = None
            func,rest = self.url.get(self.request['path']["url"])
            ans = func(self.request,key,rest=rest)
            # try:
            #     func,rest = self.url.get(self.request['path']["url"])
            #     print(func,rest)
            #     ans = func(self.request,key,rest=rest)
            # except Exception as e:
            #     ERROR('路由分发失败')
            #     print(self.request['path']["url"])
            #     print(self.url.url)
            #     print(self.request['path']["url"][0] in self.url.url)
            if ans == None or not isinstance(ans,ResponseMaker):
                await self.loop.sock_sendall(key[0],ResponseMaker(code=404).content())
            # elif ans == False:
            #     # 表示收发由回调函数自己处理
            #     # 注意回调函数需要自己关闭套接字
            #     pass
            else:
                # print(ans.content())
                await self.loop.sock_sendall(key.fileobj,ans.content())

            key[0].close()
            ####

    async def loop_handle(self):
        while True:
            key = await self.qm.get_task()
            self.log.log(DBG,'handler:New data received')
            # print("handle step1 get")
            await self.recv_data(key)
            self.log.log(DBG,'handler:Data received')
            # print("handle step2 recv")
            if not self.flag:
                await self.handle(key)
                # print("handle step3 handle")
            else:
                key[0].close()
                self.flag = False
                