import cv2
import mediapipe as mp
import numpy as np
import autopy
import time
import pyautogui

class HandDetector():
    def __init__(self):
        self.handDetector = mp.solutions.hands.Hands()
        self.drawer = mp.solutions.drawing_utils

    def process(self, img, draw = True):
        # function: 获取关节点并将关节点和关节点连线显示在视频框中
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 将GBR格式转换为RGB格式
        self.handsData = self.handDetector.process(imgRGB)  # 获取手势数据
        # 如果获取到手势数据，且draw=True，则将手势数据显示在窗口中
        if draw:
            if self.handsData.multi_hand_landmarks:
                for handLandmarks in self.handsData.multi_hand_landmarks:
                    self.drawer.draw_landmarks(img, handLandmarks, mp.solutions.hands.HAND_CONNECTIONS)
                    # :param1:img                                  图像
                    # :param2:handLandmarks                        关节点
                    # :param3:mp.solutions.hands.HAND_CONNECTIONS  关节点连线

    def findPosition(self, img):
        # function: 识别手部关节点及位置坐标
        h, w, c = img.shape
        position = {'Left':{},'Right':{}}
        if self.handsData.multi_hand_landmarks:
            i = 0
            for point in self.handsData.multi_handedness:
                score = point.classification[0].score      # score 表示置信度
                if score >= 0.8:
                    label = point.classification[0].label  # label 表示哪只手
                    # 取出每个关节点的位置数据（x，y，z），存到handLandmarks中
                    handLandmarks = self.handsData.multi_hand_landmarks[i].landmark
                    for id, lm in enumerate(handLandmarks):
                        # :param1 id 表示哪个关节点的数据
                        # :param2 lm 取用位置坐标
                        x, y = int(lm.x * w), int(lm.y * h)  # x,y 是关节点在窗口中的坐标
                        position[label][id] = (x, y)
                i = i + 1
        return position

    def fingersUp(self, img):
        # function: 返回值是由5个元素构成的列表，元素为1代表该手指竖起，0代表手指弯下
        # eg: [0,1,1,0,0] 就代表食指和中指竖起，其他手指弯下。
        # statement: 对于本程序，只检测右手手指

        upFingers = [0, 0, 0, 0, 0]  # 设定初值为0，表示不立起
        position = self.findPosition(img)
        # 对每根手指检测关节点的y坐标顺序，顺序错误则将对应的upFinger值置为0
        for i in range(0, 5):  # 0--4
            j = i * 4 # 0 4 8 12 16
            rightFinger1 = position['Right'].get(j + 1, None)
            rightFinger2 = position['Right'].get(j + 2, None)
            rightFinger3 = position['Right'].get(j + 3, None)
            rightFinger4 = position['Right'].get(j + 4, None)
            if rightFinger1 and rightFinger2 and rightFinger3 and rightFinger4:
                if rightFinger4[1] < rightFinger3[1] < rightFinger2[1] < rightFinger1[1]:
                    upFingers[i] = 1
        return upFingers



class HandController():
    def mouseMove(self, img, rightForeFingerT, pt1, pt2, scrWidth, scrHigh):
        cv2.circle(img, (rightForeFingerT[0], rightForeFingerT[1]), 10, (0, 0, 255), cv2.FILLED)
        x = np.interp(rightForeFingerT[0], (pt1[0], pt2[0]), (0, scrWidth))
        y = np.interp(rightForeFingerT[1], (pt1[1], pt2[1]), (0, scrHigh))
        # 此处加条件判断，避免手不在显示框中或光标到达屏幕边界时程序终止
        if x > 0 and x < scrWidth and y > 0 and y < scrHigh:
            autopy.mouse.move(x, y)

    def mouseClick(self, img, rightForeFingerT, rightMidFingerT, rightRingFingerT, rightForeFingerR, rightMidFingerR, last_time, button, freq):
        cv2.circle(img, (rightForeFingerT[0], rightForeFingerT[1]), 10, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (rightMidFingerT[0], rightMidFingerT[1]), 10, (255, 0, 0), cv2.FILLED)
        if freq == "Double":
            cv2.circle(img, (rightRingFingerT[0], rightRingFingerT[1]), 10, (255, 0, 0), cv2.FILLED)

        current_time = time.time()
        # 避免出现重复点击的情况
        if current_time - last_time > 1.0:
            if freq == "Single":
                autopy.mouse.click(button)
            else:
                pyautogui.doubleClick()

    def mouseWheel(self, img, rightThumbT, direction):
        if rightThumbT:
            cv2.circle(img, (rightThumbT[0], rightThumbT[1]), 10, (0, 128, 0), cv2.FILLED)
            if direction == "up":
                pyautogui.scroll(50)
            else:
                pyautogui.scroll(-50)


























