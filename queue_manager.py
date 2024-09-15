"""
队列管理器
任务队列   task_queue   类型 selector.Selector.selectkey
日志队列    log_queue   类型 tuple(rank,timestamp,text)
消息队列    msg_queue   类型 tuple(target,...) 可用于各种消息传递  (target为目标对象,后续参数为传递的消息
"""

import asyncio
from read_config import *
# from logger import log
import time

class QueueManager:
    def __init__(self):
        # self.task_queue = asyncio.Queue(CONF['task_queue_size'])
        self.task_queue = asyncio.Queue()
        self.log_queue = asyncio.Queue(200)
        self.log_overflow = False

        self.topic = {}
        self.topic_epoch = {}  # 用于标记topic的版本号 实际是偏移量
        self.topicmsg_outtime = 10  # topic消息超时时间 s
        # TODO 将topic消息换用链表存储，以便快速删除超时消息

    def put_task(self, task):
        self.task_queue.put_nowait(task)

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
    
    def get_topic_by_name(self,topic_name):
        if topic_name in self.topic:
            return self.topic[topic_name]
        else:
            return False
    
    def is_topic_exist(self,topic_name):
        return topic_name in self.topic

    def new_topic(self,topic_name):
        if topic_name not in self.topic:
            self.topic[topic_name] = []
            self.topic_epoch[topic_name] = 0

        return follow_topic(topic_name,self)
    
    def follow(self,topic_name,id):
        if self.is_topic_exist(topic_name):
            return False
        return follow_topic(topic_name,id,self)
    
    def get_topic_msg(self,topic_name,pointer):
        if topic_name not in self.topic:
            return False
        try:
            msgs = self.topic[topic_name][pointer-self.topic_epoch[topic_name]:]
            if time.time() - msgs[0][1]  > self.topicmsg_outtime:
                self.topic_epoch[topic_name] += self.recycl_topic(topic_name)
                return self.topic[topic_name][pointer-self.topic_epoch[topic_name]:]
            else:
                return msgs
        except Exception as e:
            return "Error:topic_list_pointer"+str(e)
        
    def recycl_topic(self,topic_name):
        """
        TODO 将topic中超时的消息删除
        懒汉式 在获取消息时检查，如果超时则触发清理
        """
        if topic_name not in self.topic:
            return False
        now = time.time()
        for i in range(len(self.topic[topic_name])):
            if now - self.topic[topic_name][i][1] > self.topicmsg_outtime:
                self.topic[topic_name].pop(i)
            else:
                return i+1  # 删除个数




class follow_topic:
    def __init__(self,topic_name,id,queue:QueueManager):
        self.topic_name = topic_name
        self.qm = queue
        self.id = id
        self.pointer = 0
        
    def put(self,msg,from_=0):
        """
            (from,time,msg)
            from: 发送者 同上 不为0   1为reactor 2为handler 3为logger  或直接为id
            time: 发送时间 时间戳 s
            msg: 消息内容 任意类型
        """

        self.qm.topic[self.topic_name].append(((self.id if from_ == 0 else from_),time.time(),msg))

    def get(self):
        msg = self.qm.get_topic_msg(self.topic_name,self.pointer)
        if msg:
            self.pointer += len(msg)
        return msg
