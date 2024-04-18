import analysis_request
AnalysisRequest = analysis_request.AnalysisRequest
import asyncio
import response_maker
ResponseMaker = response_maker.ResponseMaker



class Handler:

    loop = asyncio.get_running_loop()


    def __init__(self,url,queue: asyncio.Queue):
        self.url = url
        self.queue = queue

        self.request = None

        pass

    async def recv_data(self,key):
        # 接收数据

        sk = key[0]

        recv_data = b''
        while True:
            try:
                recv_data += await self.loop.sock_recv(sk,1024)
                if len(recv_data) == False:  # 收到数据小于等于0 说明客户端断开连接
                    try:
                        self.selector.unregister(sk.fileno())
                        sk.close()
                    except:
                        pass
            except Exception as e:
                # 数据传输完成  大概
                break
        
        # 分割数据
        try:
            self.request = AnalysisRequest(recv_data)
        except Exception as e:
            client_addr = sk.getpeername()
            raise Exception('请求头解析失败%s' % str(client_addr) )
        
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
                await self.loop.sock_sendall(ans.content())
            ####

    async def loop_handle(self):
        while True:
            key = await self.queue.get()
            await self.recv_data(key)
            await self.handle(key)