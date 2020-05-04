#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import time
import xml.etree.ElementTree as ET
import datetime
import threading
import socket
import sys

lock = threading.Lock()
check_bus={}
st_addr={}
busSocks={}

class msg:
    def __init__(self,key,data):
        self.key = key
        self.data = data
    
    def getKey(self):
        return self.key
    
    def getData(self):
        return self.data
    
class Queue: # 버스 캠을 전송하기 위한 큐(버퍼)
    def __init__(self):
        self.Queue_item = []
    
    def print_queue(self):
        for i in range(len(self.Queue_item)):
            print(self.Queue_item[i])
            print()
    
    # Enqueue 기능 구현
    def Enqueue(self,x):
        self.Queue_item.append(x)
        return None
    
    # Dequeue 기능 구현
    def Dequeue(self):
        item_length = len(self.Queue_item)
        if item_length < 1:
            print("Queue is empty!")
            return False
        result = self.Queue_item[0]
        del self.Queue_item[0]
        return result
    
    # isEmpty 기능 구현
    def isEmpty(self):
        return not self.Queue_item


def msg_thread(stId,sock,msgQueue):
    global lock
    while st_addr.get(stId) is not None:
        if msgQueue.isEmpty():
            continue
        lock.acquire()
        msg = msgQueue.Dequeue()
        lock.release()
        sock.send(msg.getKey().encode('utf-8'))
        sock.send(msg.getData().encode('utf-8'))
    print('MSG 큐 소멸')

    
class Bus:
    def __init__(self,buskey,sock):
        self.buskey = buskey
        self.sock = sock
        self.isNeed = False
    def __repr__(self):
        return str(self.buskey)

    def getKey(self):
        return self.buskey
    
    def getSock(self):
        return self.sock
    def setNeed(self):
        self.isNeed = True
    def unNeed(self):
        self.isNeed = False
    def getNeed(self):
        return self.isNeed
        
def Thread_sock_1(clnt,addr): ## raspberry
    print ('(1)Connected with ' + addr[0] + ':' + str(addr[1]))
    stId = clnt.recv(9).decode('utf-8')
    print('정류장 ID : ',stId)
    st_addr[stId] = addr[0]
    msgQueue = Queue()
    print('addr:',st_addr.get(stId))
    print('MSG QUEUE START')
    msgThread = threading.Thread(target=msg_thread,args=(stId,clnt,msgQueue))
    msgThread.start()
    while 1:
        try:
            header = clnt.recv(1).decode('utf-8')
        except:
            break
            
        if(len(header)<1):
            break
            
        elif(header == '1'):
            bus_key = clnt.recv(9).decode('utf-8')
            bus = busSocks.get(bus_key)
            if bus is not None:
                print(bus.getKey())
                if bus.getNeed():
                    continue
                else:
                    cam_thread= threading.Thread(target=Thread_sock_3,args=(busSocks.get(bus_key),addr,clnt,msgQueue))
                    cam_thread.start()
                
        elif(header == '2'):
            bus_key = clnt.recv(9).decode('utf-8')
            bus_sock = busSocks.get(bus_key)
            if bus_sock is not None:
                bus_sock.unNeed()
            
            
    print ('Disconnected with ' + addr[0] + ':' + str(addr[1]))
    del st_addr[stId]
    clnt.close()

def Thread_sock_2(clnt,addr): ## Android
    print ('(2)Connected with ' + addr[0] + ':' + str(addr[1]))
    global st_addr
    while 1:
        recv_msg = clnt.recv(10).decode('utf-8')
        recv_addr = st_addr.get(recv_msg)
        if(recv_addr is not None):
            clnt.send((recv_addr+'\r\n').encode('utf-8'))
            clnt.recv(1)    
            break
        else:
            break
        
    print ('Disconnected with ' + addr[0] + ':' + str(addr[1]))
    clnt.close()
    
def Thread_sock_3(bus,addr,clnt,msgQueue): ## BUS CAMERA
    global lock
    print ('카메라 요청 ' + addr[0] + ':' + bus.getKey())
    bus.setNeed()
    busSock = bus.getSock()
    busSock.send('1'.encode('utf-8')) # 연결 요청
    
    while bus.getNeed():
            try:
                busSock.settimeout(7)
                recvMsg = busSock.recv(4).decode('utf-8') #버스 번호판 (일단 4자리로 설정)
                if bus.getNeed() and len(recvMsg) == 4:
                    lock.acquire()
                    msgQueue.Enqueue(msg(bus.getKey(),recvMsg))
                    lock.release()
            except socket.timeout :
                lock.acquire()
                msgQueue.Enqueue(msg(bus.getKey(),'0000'))
                lock.release()
                
    print(bus.getKey(),'번 카메라 종료')
    busSock.send('0'.encode('utf-8')) # 연결 종료
    
HOST = '' #all available interfaces
PORT = 8888

serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ('Socket created')

#2. bind to a address and port
try:
    serverSock.bind((HOST, PORT))
except socket.error as msg:
    print ('Bind Failed. Error code: ' + str(msg[0]) + ' Message: ' + msg[1])
    sys.exit()

print ('Socket bind complete')

serverSock.listen(10)
print ('Socket now listening')

while 1:
    connect_check = False
    clnt, addr = serverSock.accept()
    sock_type=clnt.recv(1).decode('utf-8')
    if(sock_type=='1'):
        clnt_thread = threading.Thread(target=Thread_sock_1,args=(clnt,addr))
        connect_check = True
        
    elif(sock_type=='2'):
        clnt_thread = threading.Thread(target=Thread_sock_2,args=(clnt,addr))
        connect_check = True
        
    elif(sock_type=='3'):
        bus_key = clnt.recv(9).decode('utf-8')
        temp_bus = Bus(bus_key,clnt)
        busSocks[bus_key]=temp_bus
        print ('(3)Connected with ' + addr[0] + ':' + str(addr[1]))
        
    if(connect_check):
        clnt_thread.start()

serverSock.close()

