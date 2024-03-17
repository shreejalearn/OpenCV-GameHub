import cv2
from cvzone.HandTrackingModule import HandDetector
import mouse
import numpy as np
import pyautogui as pt


cap=cv2.VideoCapture(0)
cam_w, cam_h = 680, 480
cap.set(3,cam_w)
cap.set(4,cam_h)
frameR = 100

detector = HandDetector(maxHands=1,detectionCon=0.65)

from screeninfo import get_monitors
for m in get_monitors():
    print(str(m))


while True:
    ret,frame=cap.read()
    frame = cv2.flip(frame, 1)
    hands, frame = detector.findHands(frame)

    cv2.rectangle(frame, (frameR, frameR), (cam_w - frameR, cam_h - frameR), (255, 0, 255), 2)

    if(hands):
        hand1 = hands[0]
        lmList1 = hand1['lmList']
        ind_x = lmList1[8][0]
        ind_y = lmList1[8][1]
        cv2.circle(frame, (lmList1[8][0], lmList1[8][1]), 15, (255, 0, 255), cv2.FILLED)
        conv_x = int(np.interp(ind_x, (frameR, cam_w-frameR), (0, 1920)))

        conv_y = int(np.interp(ind_y, (frameR, cam_h-frameR), (0, 1080)))
        mouse.move(conv_x,conv_y)
        fingers=detector.fingersUp(hand1)
        if(fingers[4]==1):
            pt.mouseDown()


    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
