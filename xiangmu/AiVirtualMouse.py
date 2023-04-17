import cv2
import math
import HandTrackingModule as htm
import autopy
import numpy as np
import time


def mouse_click(pmfingers,pmdistance):
    if pmdistance < 40:
        if pmfingers[1] and pmfingers[2]==False:
            autopy.mouseclick(autopy.mouse.Button.LEFT)
        elif pmfingers[1] and pmfingers[2]:
            autopy.mouse.click(autopy.mouse.Button.RIGHT)
        
        
def scrolling(pmfingers, pmlmList):
    if(not hasattr(scrolling, "last_posx", "last_posy")):   
        scrolling.last_posx,srolling.lastposy=pmlmList[8][1:]   
    posx,posy= pmlmList[8][1:]
    #食指中指同时举起
    if pmfingers[1] and pmfingers[2]:
        #判断位置
        if(scrolling.last_posy<posy-5):
            #下滑
            autopy.key.toggle(autopy.key.Code.UP_ARROW,True,[])
        elif(scrolling.last_posy>posy+5):
            autopy.key.toggle(autopy.key.Code.DOWN_ARROW,True,[])
        elif(posy-5<scrolling.lastposy<posy+5):
            autopy.key.toggle(autopy.key.Code.UP_ARROW,False,[])
            autopy.key.toggle(autopy.key.Code.DOWN_ARROW,False,[])
      
            
def forward_back(pmfingers, pmlmList):
    if(not hasattr(forward_back, "last_posx", "last_posy")):   
        forward_back.last_posx,forward_back.lastposy=pmlmList[8][1:]
    posx,posy= pmlmList[8][1:]
    #食指中指同时举起
    if pmfingers[1] and pmfingers[2]:
        #判断位置
        if(forward_back.last_posx<posx-5):
            #下滑
            autopy.key.tap(autopy.key.Code.LEFT_ARROW,[at.key.Modifier.ALT])
        elif(forward_back.last_posx>posx+5):
            autopy.key.tap(autopy.key.Code.RIGHT_ARROW,[at.key.Modifier.ALT])
        
##############################
global wCam, hCam = 1080, 720
global frameR = 100
global smoothening = 5
##############################
cap = cv2.VideoCapture(0)  # 若使用笔记本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

detector = htm.handDetector()
wScr, hScr = autopy.screen.size()
# print(wScr, hScr)




while True:
    success, img = cap.read()
    # 1. 检测手部 得到手指关键点坐标
    img = detector.findHands(img)
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (0, 255, 0), 2,  cv2.FONT_HERSHEY_PLAIN)
    lmList = detector.findPosition(img, draw=False)
    
    #find function
    #x is the raw distance y is the value in cm
    x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
    y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
 
    # Ax^2 + Bx + C
    if len(lmList) != 0:
        x1, y1 = lmList[5][:2]
        x2, y2 = lmList[17][:2]
        coff = np.polyfit(x, y, 2)
        distance = math.sqrt((y2-y1)**2 + (x2-x1)**2)
        A, B, C = coff
        distanceCM = A*distance**2 + B*distance + C
        print(distanceCM)
            
    
    # 2. 判断食指和中指是否伸出
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        fingers = detector.fingersUp()

        # 3. 若只有食指伸出 则进入移动模式
        if fingers[1] and fingers[2] == False:
            # 4. 坐标转换： 将食指在窗口坐标转换为鼠标在桌面的坐标
            # 鼠标坐标
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # smoothening values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # 5. 若是食指和中指都伸出 则检测指头距离 距离够短则对应鼠标点击
        if fingers[1] and fingers[2]:
            length, img, pointInfo = detector.findDistance(8, 12, img)
            if length < 40:
                cv2.circle(img, (pointInfo[4], pointInfo[5]),
                           15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'fps:{int(fps)}', [15, 25],
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
    cv2.imshow("Image", img)
    cv2.waitKey(1)