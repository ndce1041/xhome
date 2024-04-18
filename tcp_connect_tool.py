"""
小小的测试工具，向指定端口发起tcp连接
"""


import socket
import time
ttlist = []


def tcp_connect_tool(num, ip, port, timeout=5,delay=0.1):
    for i in range(num):
        sk = socket.socket()
        sk.connect((ip, port))
        sk.settimeout(timeout)
        ttlist.append(sk)
        print('连接成功:', i)
        time.sleep(delay)


def close_all():
    for i in ttlist:
        i.close()
        print('关闭连接:', i)


if __name__ == '__main__':
    try:
        tcp_connect_tool(50, '127.0.0.1', 80)
    except Exception as e:
        print(e)
    input('按任意键关闭连接')
    close_all()