import cv2
from cvzone.HandTrackingModule import HandDetector
import pyautogui as auto

# Function to control lighting
def control_lighting(length):
    if length < 25:
        auto.press('up')  # Simulating pressing the 'up' key for lighting control

# Main code
cap = cv2.VideoCapture(0)
hd = HandDetector(maxHands=1)

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (1080, 720))

    hand, frame = hd.findHands(frame)

    if hand:
        hands = hand[0]
        lmlist = hands['lmList']

        length, info, frame = hd.findDistance(lmlist[4][0:2], lmlist[8][0:2], frame)
        length = round(length)
        
        control_lighting(length)  # Call the function to control lighting based on hand gesture

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
