import dynamic_filelist as df
import socket
import time
import resolver
import threading


def application(env, start_response):
    '''
    f = open(r'./static/html/welcome.html', 'rb')
    body = f.read()
    f.close()
    '''
    head = env['headers']

    if 'Cookie' in head:
        cookie = head['Cookie']
        start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
        body = cookie
    else:
        start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8'), ('set-cookie', 'A68T')])
        body = 'A68T'
    return body
    pass
