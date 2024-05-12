import asyncio
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
import os
from logger import Logger  # 假设Logger类在logger.py文件中

# 模拟的配置字典
CONF = {
    'log_path': './log/',
    'log_level': 'info',
    'log_temp_size': 10
}

class simulate_queue_manager:
    que = []

    def get_log(self):
        return self.que.pop(0)




class TestLogger(unittest.TestCase):
    def setUp(self):
        # 确保日志目录存在
        os.makedirs(CONF['log_path'], exist_ok=True)
        # 创建Logger实例
        self.logger = Logger()

    def tearDown(self):
        # 测试完成后清理创建的日志文件
        for filename in os.listdir(CONF['log_path']):
            os.remove(os.path.join(CONF['log_path'], filename))

    @patch('logger.datetime')
    def test_renew_date(self, mock_datetime):
        # 设置模拟的当前日期
        mock_datetime.now.return_value = datetime(2023, 4, 1)
        mock_datetime.now.return_value.date.return_value = datetime(2023, 4, 1).date()
        self.logger.renew_date()
        
        # 改变模拟的当前日期，触发新建日志文件的条件
        mock_datetime.now.return_value = datetime(2023, 4, 2)
        mock_datetime.now.return_value.date.return_value = datetime(2023, 4, 2).date()
        self.logger.renew_date()
        
        # 检查是否创建了新的日志文件
        expected_log_file_path = os.path.join(CONF['log_path'], "2023-04-02.txt")
        self.assertTrue(os.path.exists(expected_log_file_path))

if __name__ == '__main__':
    unittest.main()



