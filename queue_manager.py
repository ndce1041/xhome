"""
队列管理器
任务队列   task_queue
日志队列    log_queue
"""

import asyncio
from read_config import *
from logger import log,DBG,INF,ERR,WRN

class QueueManager:
    def __init__(self):
        self.task_queue = asyncio.Queue(CONF['task_queue_size'])
        self.log_queue = asyncio.Queue(200)
        self.log_overflow = False

        log(DBG,"Queue init success")

    async def put_task(self, task):
        await self.task_queue.put(task)

    async def get_task(self):
        return await self.task_queue.get()
    
    def log(self,log):
        try:
            self.log_queue.put_nowait(log)
        except asyncio.QueueFull:
            # TODO 日志队列溢出处理
            return False

    async def get_log(self):
        return await self.log_queue.get()

