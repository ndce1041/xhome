"""
队列管理器
任务队列   task_queue   类型 selector.Selector.selectkey
日志队列    log_queue   类型 tuple(rank,timestamp,text)
消息队列    msg_queue   类型 tuple(target,...) 可用于各种消息传递  (target为目标对象,后续参数为传递的消息
"""

import asyncio
from read_config import *
# from logger import log

class QueueManager:
    def __init__(self):
        self.task_queue = asyncio.Queue(CONF['task_queue_size'])
        self.log_queue = asyncio.Queue(200)
        self.log_overflow = False

        # self.log = log(self)

    async def put_task(self, task):
        await self.task_queue.put(task)

    async def get_task(self):
        return await self.task_queue.get()
    
    def put_log(self,log):
        try:
            self.log_queue.put_nowait(log)
        except asyncio.QueueFull:
            # TODO 日志队列溢出处理
            return False

    async def get_log(self):
        return await self.log_queue.get()

