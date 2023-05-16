import numpy as np
import time
import autopy
import cv2
from handUtils import HandDetector
from handUtils import HandController
import pyautogui

# 获取电脑屏幕的宽高
scrWidth, scrHigh = autopy.screen.size()  # (1536.0, 864.0)
# 定义显示框的宽高
cameraWidth, cameraHigh = 1280, 720
# 定义手势识别框的左上、右下顶点坐标（对屏幕宽高做等比缩放）
pt1 = (int((cameraWidth - scrWidth / 2) / 2), 50)
pt2 = (int((cameraWidth + scrWidth / 2) / 2), int(scrHigh / 2 + 50))

camera = cv2.VideoCapture(0)  # 调用电脑摄像头
camera.set(3, cameraWidth)  # 设置显示框的宽度为1280
camera.set(4, cameraHigh)  # 设置显示框的高度为720

handDetector = HandDetector()
handController = HandController()

# 用于判定执行鼠标单击的次数
last_time = 0


toggleFlag = False



# 处理每一帧图像
while True:
    success, img = camera.read()
    # :return param1:success 读取是否成功
    # :return param2:img     图像（视频是由图像组成）

    #cv2.rectangle(img, pt1, pt2, (0, 255, 255), 5)

    if success:
        img = cv2.flip(img, 1)      # 将图像做镜像翻转（库中以视频窗口的左侧的手定义为“Left”）
        handDetector.process(img)
        # 如果不想画关节点及连线
        # handDetector.process(img, False)
        position = handDetector.findPosition(img)
        """
        此时，手的关节点的位置数据都被储存在 字典position 中
        字典position的格式如下：（以右手为例）
        {‘Left’:{},'Right':{0:(x0, y0), 1:(x1, y0),...}}
        """

        # 用upFinger列表接收右手手指是否立起的信息
        upFingers = handDetector.fingersUp(img)

        rightThumbT = position['Right'].get(4, None)
        # 4 是拇指指尖的位置；取不到则返回None
        # rightThumb 储存了一个元组（x4， y4）
        rightForeFingerT = position['Right'].get(8, None)
        # 8 是食指指尖的位置；取不到则返回None
        # rightForeFinger 储存了一个元组（x8， y8）
        rightMidFingerT = position['Right'].get(12, None)
        # 12 是中指指尖的位置；取不到则返回None
        # rightMidFinger 储存了一个元组（x12， y12）
        rightRingFingerT = position['Right'].get(16, None)
        # 16 是无名指指尖的位置；取不到则返回None
        # rightRingFinger 储存了一个元组（x16， y16）
        rightForeFingerR = position['Right'].get(5, None)
        # 5 是食指指尖的位置；取不到则返回None
        # rightForeFinger 储存了一个元组（x5， y5）
        rightMidFingerR = position['Right'].get(9, None)
        # 9 是中指指尖的位置；取不到则返回None
        # rightMidFinger 储存了一个元组（x9， y9）


        # 鼠标左键松开
        if not (upFingers[1:5] == [1, 1, 0, 0] and abs(rightMidFingerR[0] - rightForeFingerR[0]) > abs(rightMidFingerT[0] - rightForeFingerT[0])):
            if toggleFlag == True:
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
                toggleFlag = False

        # 光标移动
        # 食指立起
        if upFingers[1:5] == [1, 0, 0, 0]:
            handController.mouseMove(img, rightForeFingerT, pt1, pt2, scrWidth, scrHigh)

        # 鼠标左键单击/鼠标右键单击
        # 食指中指立起，且食指位于中指左侧，且食指中指根部的距离小于食指中指指尖的距离 / 食指中指立起，且食指位于中指右侧、且食指中指根部的距离小于食指中指指尖的距离
        if (upFingers[1:5] == [1, 1, 0, 0] and abs(rightMidFingerR[0] - rightForeFingerR[0]) < abs(rightMidFingerT[0] - rightForeFingerT[0])):
            if rightMidFingerT[0] > rightForeFingerT[0]:
                handController.mouseClick(img, rightForeFingerT, rightMidFingerT, rightRingFingerT, rightForeFingerR,
                                                rightMidFingerR, last_time, autopy.mouse.Button.LEFT, "Single")
            else:
                handController.mouseClick(img, rightForeFingerT, rightMidFingerT, rightRingFingerT, rightForeFingerR,
                                                rightMidFingerR, last_time, autopy.mouse.Button.RIGHT, "Single")
            last_time = time.time()

        # 鼠标左键双击
        # 食指、中指、无名指立起
        if upFingers[1:5] == [1, 1, 1, 0]:
            handController.mouseClick(img, rightForeFingerT, rightMidFingerT, rightRingFingerT, rightForeFingerR,
                                                rightMidFingerR, last_time, autopy.mouse.Button.LEFT, "Double")

        # 鼠标左键按住并拖动，且食指中指根部的距离大于食指中指指尖的距离（食指中指指尖贴紧的姿势）
        if (upFingers[1:5] == [1, 1, 0, 0] and abs(rightMidFingerR[0] - rightForeFingerR[0]) > abs(rightMidFingerT[0] - rightForeFingerT[0])):
            if toggleFlag == False:
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)
                toggleFlag = True
            handController.mouseMove(img, rightForeFingerT, pt1, pt2, scrWidth, scrHigh)


        # 鼠标滚轮
        # 向上：只有拇指立起（姿势：右手手心向屏幕做握拳状，拇指自然立起）
        if upFingers == [1,0,0,0,0]:
            handController.mouseWheel(img, rightThumbT, "up")
        # 向下：没有手指立起（姿势：右手手心向屏幕做握拳状，拇指自然弯曲）
        elif upFingers == [0,0,0,0,0]:
            handController.mouseWheel(img, rightThumbT, "down")


        cv2.imshow('Video', img)    # 创建视频窗口“Video”

    k = cv2.waitKey(1)              # 每1ms内等待输入
    if k == ord('q'):               # 表示按下‘q’键后，窗口关闭
        break

camera.release()         # 释放摄像头
cv2.destroyAllWindows()  # 关闭所有cv2打开的窗口



























