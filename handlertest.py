import handler
import url_manager
import asyncio


url = url_manager.url_manager()

def index(request,key,rest):
    return handler.ResponseMaker(code=200,content=b'ok')





que = asyncio.Queue()




hand = handler.Handler(url)