#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import time
import datetime
import threading
import socket
import sys

class Bus:
    def __init__(self,busId,lisence,key):
        self.busId = busId
        self.lisence = lisence
        self.key = key
        self.next = None
        
    def __repr__(self):
        return str(self.busId)
    
    def getLisence(self):
        return self.lisence
    
    def getId(self):
        return self.busId
    
    def getKey(self):
        return self.key

class Node:
    def __init__(self, data) :
        self.data = data
        self.next = None
        self.prev = None
    def getData(self):
        return self.data
    def setData(self, val):
        self.data = val
    def hasVale(self, val) :
        return self.data == val
    def getNext(self):
        return self.next
    def setNext(self, node) :
        if type(node) == Node:
            self.next = node          
            return
        elif node is None:
            self.next = None
        else:
            print("setNext  type error:{} and type is {}".format(node,type(Node)))
    def getPrev(self):
        return self.prev
    def setPrev(self, node) :
        if type(node) == Node:
            self.prev = node
        elif node == None:
            self.prev = None
        else:
            print("setPrev type error:{} and type is {}".format(node,type(Node)))  
    def __repr__(self):
        return "(data :" + str(self.data) + ")"
    
class DoubleLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    def getSize(self):
        return self.size
    
    def addTop(self,data):
        global lock
        newNode = Node(data)
        print('TOP추가:',data)
        callCamera(data.getKey())
        if self.head is None:
            self.head = newNode
            newNode.prev = None
            newNode.next = None
            self.tail = newNode
            self.size += 1
        else:
            self.head.prev = newNode
            newNode.next = self.head
            newNode.prev = None
            self.head = newNode
        self.printNodes()
        
    def addNode(self, data):
      #  "add an item at the end of the list"
        newNode = Node(data)
        callCamera(data.getKey())
        if self.head is None:
            self.head = newNode
            newNode.prev = None
            newNode.next = None
            self.tail = newNode
        else:
            self.tail.setNext(newNode)
            newNode.setPrev(self.tail)
            self.tail = newNode
        self.size +=1
        self.printNodes()
        
    def addNode2(self, curr, data):
        print('addNode2')
        newNode = Node(data)
        callCamera(data.getKey())
        if curr.next is None:
            self.tail = newNode
            newNode.next = None
            newNode.prev = curr
            curr.next = newNode
        else :
            curr.next.prev = newNode
            newNode.next = curr.next
            newNode.prev = curr
            curr.next = newNode
        self.size +=1
        self.printNodes()
    
    def findNode2(self,data):
        curr = self.head
        if type(data) is Node:
            data = data.getData().getLisence()
        while curr:
            if curr.getData().getLisence() == data:
                return curr
            curr = curr.getNext()
        return False
    
    def findNode(self,data):
        curr = self.head
        if type(data) is Node:
            data = data.getData().getKey()
        while curr:
            if curr.getData().getKey() == data:
                return curr
            curr = curr.getNext()
        return False
    
    def removeNode(self, data):
        if self.findNode(data) == False:
            print("Data " + str(data) + " is not in the list, remove op is not carried out")
            return
        curr = self.head
        self.size = self.size -1
        while curr is not None:
            prev = curr.getPrev()
            next = curr.getNext()
            if curr.getData() == data.getData():
                offCamera(curr.getData().getKey())
                if prev is not None:
                    prev.setNext(next)
                    if next is not None:
                        next.setPrev(prev)
                    else:
                        self.tail = prev #
                    print("Data " + str(data) + " is removed")
                else:
                    self.head = next
                    if next is not None:
                        next.setPrev(None)
                    else:
                        self.tail = prev
                    print("Data " + str(data) + " is removed")
                return
            curr = next
        self.printNodes()
            
    def refreshLink(self,target,node):
        if target.getNext() is not None:
            while target.getNext().getData() == node:
                self.removeNode(target.getNext())
            self.printNodes()
                
    def printNodes(self):
        if self.size == 0:
            print("The list is empty")
            return
        curr = self.head
        tail = self.tail
        print("head = {} and tail = {}. Size = {}".format(self.head, self.tail, self.size))
        pos = 1
        print('--------')
        while curr:
            print("position :"+str(pos) + "  " + str(curr.data))
            pos += 1
            curr = curr.getNext()
        print('--------')
    def printNodesReverse(self):
        if self.size == 0:
            print("The list is empty")
            return
        curr = self.tail
        pos = self.size
        
        while curr: 
            print("position :"+str(pos) + "  " + str(curr.data))
            pos = pos -1
            curr = curr.getPrev()
    
    def sendList(self,sock):
        global lock
        if self.size == 0:
            sock.send(('0'+'\r\n').encode('utf-8'))
            return
        else :
            lock.acquire()
            sock.send((str(self.getSize())+'\r\n').encode('utf-8'))
            curr = self.head
            while curr:
                sock.send((curr.getData().getId()+'\r\n').encode('utf-8'))
                curr = curr.getNext()
            lock.release()
            
                                                        
busll = DoubleLinkedList()

check_bus={}
sock_list_2=[]
sock_list_3=[]
lock = threading.Lock()
guest = 0

 # API 부분 #
def get_html(Id):
    print(datetime.datetime.now())
    _html = ""
    URL = 'http://ws.bus.go.kr/api/rest/arrive/getLowArrInfoByStId?ServiceKey=0f2to44ZSBP527qwIw6lc6b0cRp22W2ThXgWnrfMGyXeaLSHv7fswO0997FTVjRP38E5jNoHB0m0mZZuNDQx%2BQ%3D%3D'
    params = {'stId':Id}
    res = requests.get(URL, params=params)
    if res.status_code == 200:
        _html = res.text
    return _html

def readAttrib(text,att):
    leng = len(att)+2
    start = text.find('<'+att+'>')+leng
    end = text.find('</'+att+'>')
    return(text[start:end])

def readTime(text):
    last = text.find('[막차]')
    if(last != -1):
        text = text[last+5:]
    
    minute = text.find('분')
    second = text.find('초')
    if(minute == -1):
        return None
    
    else:
        res = int(text[:minute])*60
        if(second != -1):
            res +=int(text[minute+1:second])
        return res

def xmlparse(text):
    check = False
    global sleep_time
    for items in text.split('<itemList>'):
        msg1 = readAttrib(items,'arrmsg1')
        rtNm = readAttrib(items,'rtNm')
        key = readAttrib(items,'vehId1')
        
        if(msg1 == '곧 도착'):
            plainNm = readAttrib(items,'plainNo1')[-4:]
            if(check_bus.get(plainNm) is None):
                print("체크리스트 추가(차량번호:{})".format(plainNm))
                check_bus[plainNm] = Bus(rtNm,plainNm,key)
                check = True
        else:
            msg_check = msg1.find('[우회]')
            if msg_check != -1 :
                msg1 = msg1[msg_check+5:]
                
            time = readTime(msg1)
            if(time is not None):
                if(time < sleep_time):
                    sleep_time = time

def lisenceCheck(lisence):
    ch = check_bus.get(lisence)
    if(ch != None):
        check_bus.pop(lisence)        
        return ch
    
    else:
        return None
    
#API 부분#
def callCamera(key):
    global mainSock
    print('카메라요청:',key)
    
    mainSock.send('1'.encode('utf-8'))
    mainSock.send(key.encode('utf-8')) #9자리 수
    
def offCamera(key):
    global mainSock
    print('카메라종료:',key)
    mainSock.send('2'.encode('utf-8'))
    mainSock.send(key.encode('utf-8'))

# 메인 서버로 요청 #
def Thread_BusList():
    global busll
    global mainSock
    global lock
    while 1:
        buskey=mainSock.recv(9).decode('utf-8')
        recvMsg=mainSock.recv(4).decode('utf-8')
        
        lock.acquire()
        curr = busll.findNode(buskey)
        if curr is False:
            lock.release()
            continue
        print('({})버스 후방카메라 인식 : {}'.format(buskey,recvMsg))
        
            
        if recvMsg == '0000':
            if curr.getNext() is not None:
                busll.removeNode(curr.getNext())
            lock.release()
            continue
        elif curr.getNext() is not None:
            if curr.getNext().getData().getLisence() == recvMsg:
                lock.release()
                continue
                
        nextBus = lisenceCheck(recvMsg)
        
        if nextBus is None:
            check = busll.findNode2(recvMsg)
            if check is not None:
                if curr is not None:
                    busll.refreshLink(curr,nextBus)
        else:
            if curr == busll.tail:
                busll.addNode(nextBus)
            else:
                busll.addNode2(curr,nextBus)
                    
                        
        lock.release()
            
        

def Thread_sock_1(clnt,addr): ## raspberry
    global busll
    print ('(1)Connected with ' + addr[0] + ':' + str(addr[1]))
    topcheck = 0
    while 1:
        try:
            if topcheck == 1:
                clnt.settimeout(10)
                topcheck = 0
            elif busll.getSize() > 0:
                clnt.settimeout(6)
            else:
                 clnt.settimeout(None)
            data = clnt.recv(4).decode('utf-8')
            if len(data) <= 0:
                raise Exception
      
        except socket.timeout:
            print('맨 앞이 출발했습니다.')
            if busll.getSize() > 1:
                topcheck = 1
            busll.removeNode(busll.head)
            continue
        except:
            break
        ch = lisenceCheck(data)
        if ch is not None:
            lock.acquire()
            if busll.head is not None:
                offCamera(busll.head.getData().getKey())
                busll.head.setData(ch)
                callCamera(ch.getKey())
            else:
                busll.addNode(ch)
            lock.release()
            
        else:
            if busll.head is not None:
                if busll.findNode2(data) is not False:
                       while 1:
                            headn = busll.head.getData()
                            if headn.getLisence() == data:
                                break
                            else:
                                busll.removeNode(busll.head)
                                
                
                    
                        
    print ('Disconnected with ' + addr[0] + ':' + str(addr[1]))
    clnt.close()
    

def Thread_sock_2(clnt,addr): ## Android
    global lock
    global guest
    global busll
    print ('(2)Connected with ' + addr[0] + ':' + str(addr[1]))

    while 1:
        try:
            header = clnt.recv(1).decode('utf-8')
            if len(header) <= 0:
                raise Exception
        except:
            break
        
        if header == '1':
            busll.printNodes()
            busll.sendList(clnt)
            
    print ('Disconnected with ' + addr[0] + ':' + str(addr[1]))
    lock.acquire()
    guest-=1
    lock.release()
    clnt.close()
        
def Thread_sock_3(clnt,addr): ## Android in Bus
    print ('(3)Connected with ' + addr[0] + ':' + str(addr[1]))
    global guest
    global lock
    
    while 1:
        try:
            header = clnt.recv(1).decode('utf-8')
            if len(header) <= 0:
                raise Exception
        except:
            break
                           
        clnt.send((str(guest)+'\r\n').encode('utf-8'))
            
    print ('Disconnected with ' + addr[0] + ':' + str(addr[1]))
    clnt.close()
       
def list_refresh(stId):
    global sleep_time
    while 1:
        sleep_time = 300
        xmlparse(get_html(stId))
        print(str(sleep_time)+"초 후 재실행")
        time.sleep(sleep_time-40) 
    
HOST = '' #all available interfaces
PORT = 7777
STATION_ID = '121000532'

try:
    mainSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mainSock.connect(('127.0.0.1', 8888))

except socket.error as msg:
    print('메인 서버 연결 실패')
    sys.exit()

    
mainSock.send('1'.encode('utf-8')) #클라이언트 타입 1
mainSock.send(STATION_ID.encode('utf-8')) #정류장 아이디 인증
bus_thread = threading.Thread(target=list_refresh,args=(STATION_ID,))
bus_thread.daemon = True
bus_thread.start()
TOPBUS_thread = threading.Thread(target=Thread_BusList)
TOPBUS_thread.daemon = True
TOPBUS_thread.start()

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

check_bus['2617']=Bus('273','2617','123456789') # test DATA 번호판 4538 노선 752 버스ID 123456789
check_bus['9800']=Bus('11-2','9800','111111111')
check_bus['4524']=Bus('753','4524','987654321')

while 1:
    clnt, addr = serverSock.accept()
    sock_type=clnt.recv(1).decode('utf-8')
    clnt_thread = None
    if(sock_type=='1'):
        clnt_thread = threading.Thread(target=Thread_sock_1,args=(clnt,addr))
    
    
    elif(sock_type=='2'):
        lock.acquire()
        guest+=1
        print('guest:',guest)
        lock.release()
        clnt_thread = threading.Thread(target=Thread_sock_2,args=(clnt,addr))
        sock_list_2.append(clnt_thread)
        
        
    elif(sock_type=='3'):
        clnt_thread = threading.Thread(target=Thread_sock_3,args=(clnt,addr))
        sock_list_3.append(clnt_thread)
    
    if(clnt_thread is not None):
        clnt_thread.start()

serverSock.close()


# In[ ]:





# In[ ]:




