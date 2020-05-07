#-*- coding:utf-8 -*-

import cv2
import re
import imutils
import numpy as np
import pytesseract
from PIL import Image

import sys

#????코드
import socket
import threading

def send_lisence(sock,lisence) :
    sock.send(lisence.encode('utf-8'))

def th_send(sock, lisence):
    Send_Thread = threading.Thread(target=send_lisence,args=(sock,lisence))
    Send_Thread.start()
      
#CONNECNTION
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.137.3',7777)) # ???????????? ?????
sock.send('1'.encode('utf-8')) # ????????????1



#Bus DeTect
print('Project Topic : BUS DETECTION FOR BLIND by VTS')

cascade_src = 'Bus_front.xml'
video_src = 'busvideo.mp4'


cap = cv2.VideoCapture(-1)

car_cascade = cv2.CascadeClassifier(cascade_src)
while True:
   # print(hy) 
    
    ret, img = cap.read()
    
    if (type(img) == type(None)):
        break
  #  tempimg = cv2.resize(img,dsize=(0,0),fx=0.5,fy=0.5,interpolation=cv2.INTER_LINEAR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    cars = car_cascade.detectMultiScale(gray, 1.16, 1)
    
   # temp = cv2.resize(cars,dsize(0,0),fx=0.5,fy=0.5,interpolation=cv2.INTER_LINEAR)
    check = False
    for (x,y,w,h) in cars:
        
        
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
        crop_img = img[y+int(h/3):(y+h),x:x+w]
        cv2.imwrite('/home/pi/license_plate/mybus.jpg',crop_img)
        cv2.imshow('video',img)
        check = True
        print(y,y+h,x,x+w)
        
    if cv2.waitKey(33) == 27:
        break



    if check is False:
      print('No img')
      continue
      
    else:

      reload(sys)
      sys.setdefaultencoding('utf-8')
      
      img = cv2.imread('mybus.jpg', cv2.IMREAD_COLOR)
      img = cv2.resize(img, (320, 240))
      
      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to grey scale
     # cv2.imwrite('/home/pi/license_plate/mygrayscale.jpg',gray)
      gray = cv2.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise
     # cv2.imwrite('/home/pi/license_plate/myblur.jpg',gray)
      edged = cv2.Canny(gray, 30, 200) #Perform Edge detection
     # cv2.imwrite('/home/pi/license_plate/mycanny.jpg',edged)
      cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
      cnts = imutils.grab_contours(cnts)
      cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
      screenCnt = None
      
      # loop over our contours
      for c in cnts :
      # approximate the contour
          peri = cv2.arcLength(c, True)
          approx = cv2.approxPolyDP(c, 0.018 * peri, True)
      
      # if our approximated contour has four points, then
      # we can assume that we have found our screen
          if len(approx) == 4:
              screenCnt = approx
              break
      
      
      print('check1')
      
      
      if screenCnt is None :
          detected = 0
          print "No contour detected"
          continue
      else:
          detected = 1
      
      if detected == 1 :
          cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)
      
      # Masking the part other than the number plate
      mask = np.zeros(gray.shape, np.uint8)
      try:
          cv2.drawContours(mask,[screenCnt],0,225,-1)
      except:
         print('draw')
         continue
      
      print('cbeck2')

      new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1, )
     
      
     
      new_image = cv2.bitwise_and(img, img, mask = mask)
      
      # Now crop
      (x, y) = np.where(mask == 255)
      (topx, topy) = (np.min(x), np.min(y))
      (bottomx, bottomy) = (np.max(x), np.max(y))
      Cropped = gray[topx:bottomx + 1, topy : bottomy + 1]
      
      
     # cv2.imwrite('/home/pi/license_plate/license.jpg',Cropped)
      
      kernel = np.ones((3,3),np.uint8)
      er_plate = cv2.erode(Cropped,kernel,iterations=1)
   #   er_plate = cv2.dilate(er_plate,kernel,iterations=1)
      cv2.imwrite('/home/pi/license_plate/new.jpg',er_plate)
      
      
      newcrop = cv2.imread('new.jpg')
      n_h,n_w,_ =newcrop.shape
      
     # crop1 = newcrop[0:int(n_h/3),0:n_w]
      crop2 = newcrop[int(n_h/3):n_h,int(n_w/5):n_w]
      cv2.imwrite('newcrop.jpg',crop2)
      
     # result1 = pytesseract.image_to_string(crop1,config='--psm 10 tessedit_chat_whitelist=0123456789')
      #nresult1 = int(re.findall('\d+',result1)[0])
      
     # print(result1)
      
      #print(nresult1)
     

      print('before tesseacta')

      result2 = pytesseract.image_to_string(crop2,config='--psm 10 tessedit_chat_whitelist=0123456789')
      if result2.find('26') == 0:
        result2 = 2617
      elif result2.find('4') == 0:
        result2 = 4614
      else : 
        continue
      print(result2)
      
           
      inp = str(result2) #번호??4글????
      th_send(sock,inp)
sock.close()





