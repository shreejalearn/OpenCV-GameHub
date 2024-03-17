import cv2
import numpy as np
import time
import os
import handTrackingModule as htm


cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = htm.handDetector(detectionCon=0.85)
drawColor = (255, 0, 255)
brushThickness = 15
eraserThickness = 50

xPrevious, yPrevious = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        indexX1, indexY1 = lmList[8][1:]
        middleX1, middleY2 = lmList[12][1:]

        fingers = detector.fingersUp()

        if fingers[1] and fingers[2]:
            xPrevious, yPrevious = 0, 0

            if indexY1 < 125:
                if 250 < indexX1 < 450:
                    drawColor = (255, 0, 255)
                elif 550 < indexX1 < 750:
                    drawColor = (255, 0, 0)
                elif 800 < indexX1 < 950:
                    drawColor = (0, 0, 255)
                elif 800 < indexX1 < 1200:
                    drawColor = (0, 0, 0)

            cv2.rectangle(img, (indexX1, indexY1 - 25),
                          (middleX1, middleY2 + 25), drawColor, cv2.FILLED)

        if fingers[1] and (fingers[2] == False):
            cv2.circle(img, (indexX1, indexY1), 10, drawColor, cv2.FILLED)

            if xPrevious == 0 and yPrevious == 0:
                xPrevious, yPrevious = indexX1, indexY1
            if drawColor == (0, 0, 0):
                cv2.line(img, (xPrevious, yPrevious),
                         (indexX1, indexY1), drawColor, eraserThickness)
                cv2.line(imgCanvas, (xPrevious, yPrevious),
                         (indexX1, indexY1), drawColor, eraserThickness)
            else:
                cv2.line(img, (xPrevious, yPrevious),
                         (indexX1, indexY1), drawColor, brushThickness)
                cv2.line(imgCanvas, (xPrevious, yPrevious),
                         (indexX1, indexY1), drawColor, brushThickness)

            xPrevious, yPrevious = indexX1, indexY1

    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2RGB)

    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
