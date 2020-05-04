#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#테스트용 클라이언트 라즈베리파이
import socket
import threading

status = '0'
def send_lisence(sock,lisence):
    sock.send(lisence.encode('utf-8')) #라이센스 번호 전송
    
    
#CONNECNTION
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1',7777)) # 정류소 서버와 연결
sock.send('1'.encode('utf-8')) # 클라이언트 타입 1

while 1:
    inp = str(input('>>>')) #번호판 4글자 입력
    
    send_lisence(sock,inp)

sock.close()


# In[ ]:





# In[ ]:




