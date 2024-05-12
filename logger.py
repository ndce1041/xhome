"""
异步日志模块
"""

import asyncio
from read_config import *
import queue_manager
import os
import time
from datetime import datetime

DBG = "0dbg"
INF = "1inf"
ERR = "2err"
WRN = "3wrn"

class Logger:
    def __init__(self,qm:queue_manager.QueueManager):
        self.qm = qm
        self.log_filepath = os.path.abspath(CONF['log_path'])
        self.log_level = CONF['log_level']
        self.log_temp = [] # 存储已经格式化的日志
        self.log_temp_size = CONF['log_temp_size']

        self.log_file = None
        
        self.date = datetime.now().date()   # 如果发现日志日期不是当天,则新建一个日志文件
        self.renew_date()

    def renew_date(self):
        if self.date != datetime.now().date():
            self.date = datetime.now().date()
            # 立即写入剩余的日志
            self.write_log()
            # TODO 新建一个日志文件
            if self.log_file:
                self.log_file.close()
            self.log_file = open(self.log_filepath + str(self.date) + ".txt", 'a')
        return self.date

    def write_log(self):
        """
            考虑到py文件io为同步操作,为避免多线程,通过累积日志一次性写入降低io次数
        """
        log_text = self.log_temp.join('\n')
        self.log_temp = []
        if not self.log_file:
            return False
        try:
            self.log_file.write(log_text + '\n')
            self.log_file.flush()
        except Exception as e:
            pass
        pass
    
    async def loop(self):
        while True:
            log = await self.qm.get_log()
            logdate = datetime.fromtimestamp(log[1]).date()
            if logdate != self.date:
                if logdate != self.renew_date():
                    # 可能是此日志时间不是当天
                    # 加上标记
                    log[2] = "[LOG DATE ERROR]" + log[2]
                    pass
                else:
                    pass
            # 加入到临时日志
            if self.log_temp.__len__() >= self.log_temp_size:
                self.write_log()
            self.log_temp.append(datetime.fromtimestamp(log[1]).strftime("%Y-%m-%d %H:%M:%S") + " " + log[0] + " " + log[2])

    def __del__(self):
        if self.log_file:
            self.write_log()
            self.log_file.close()



def log(rank, log:str):
    if int(rank[0]) < int(CONF['log_level']):
        return False
    log = (rank, time.time(), log)
    return log