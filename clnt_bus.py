#!/usr/bin/env python
# coding: utf-8

#테스트용 클라이언트 버스(1)
# In[ ]:


import socket
import threading

status = '0'
busID = '123456789'

def send_lisence(sock,lisence):
    global status
    
    sock.settimeout(0)
    try:
        status = sock.recv(1).decode('utf-8')
    except BlockingIOError:
        status = status
    
    if status == '1':
        sock.send(lisence.encode('utf-8'))
    

def check_Thread(sock):
    global status
    if status == '0':
        sock.settimeout(None)
    else:
        sock.settimeout(0)
    try:
        status = sock.recv(1).decode('utf-8')
    except BlockingIOError:
        status = status
        
#CONNECNTION
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1',8888)) # 정류소 서버와 연결
sock.send('3'.encode('utf-8')) # 클라이언트 타입 1
sock.send(busID.encode('utf-8'))

while 1:
    check_Thread(sock)
    
    inp = str(input('>>>')) #영상 인식 코드로 대체
    
    
    send_lisence(sock,inp)

sock.close()


# ## 

# In[ ]:




