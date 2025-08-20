import cv2
import numpy
from PIL import Image
import math
from util import get_limits

yellow = [26, 214, 232]  # yellow in BGR colorspace
blue = [226, 177, 45]  # blue in BGR colorspace
purple = [213, 131, 250]  # green in BGR colorspace
green = [161, 223, 145]  # green in BGR colorspace
dark_green = [91, 129, 41]  # light green in BGR colorspace
cap = cv2.VideoCapture(1)
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = cv2.resize(frame, (640, 480))
    hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lowerLimit, upperLimit = get_limits(color=yellow)
    lowerLimit2, upperLimit2 = get_limits(color=blue)
    lowerLimit3, upperLimit3 = get_limits(color=purple)
    lowerlimit4, upperlimit4 = get_limits(color=green)
    lowerLimit5, upperLimit5 = get_limits(color=dark_green)
    mask = cv2.inRange(hsvImage, lowerLimit, upperLimit)
    mask2 = cv2.inRange(hsvImage, lowerLimit2, upperLimit2)
    mask3 = cv2.inRange(hsvImage, lowerLimit3, upperLimit3)
    mask4 = cv2.inRange(hsvImage, lowerlimit4, upperlimit4)
    mask5 = cv2.inRange(hsvImage, lowerLimit5, upperLimit5)
    mask_ = Image.fromarray(mask)
    mask2_ = Image.fromarray(mask2)
    mask3_ = Image.fromarray(mask3)
    mask4_ = Image.fromarray(mask4)
    mask5_ = Image.fromarray(mask5)
    bbox = mask_.getbbox()
    bbox2 = mask2_.getbbox()
    bbox3 = mask3_.getbbox()
    bbox4 = mask4_.getbbox()
    bbox5 = mask5_.getbbox()

    alphayellow = 0
    alphablue = 0
    alphagreen = 0
    areayellow = 0
    areablue = 0
    areagreen = 0
    purpledot_y = 0
    greendot_y = 0

    if bbox is not None:
        x1, y1, x2, y2 = bbox
        frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)
        #print(bbox)
        x = x2-x1
        y = y2-y1
        alphayellow = math.atan(x/y)*180/math.pi
        areayellow = x*y
        #print(areayellow)
        #print(x)
        #print(y)
        #print(alpha)

    if bbox2 is not None:
        x11, y11, x22, y22 = bbox2  # <-- use bbox2 here
        frame = cv2.rectangle(frame, (x11, y11), (x22, y22), (0, 0, 255), 5)
        xblue = x22-x11
        yblue = y22-y11
        alphablue = math.atan(xblue/yblue)*180/math.pi
        areablue = xblue*yblue

    if bbox3 is not None:
        x111, y111, x222, y222 = bbox3
        frame = cv2.rectangle(frame, (x111, y111), (x222, y222), (255, 0, 0), 5)
        purpledot_y = y111
        #print(purpledot_y)

    if bbox4 is not None:
        x1111, y1111, x2222, y2222 = bbox4
        frame = cv2.rectangle(frame, (x1111, y1111), (x2222, y2222), (0, 255, 255), 5)
        greendot_y = y1111
        #qprint(greendot_y)

    if bbox5 is not None:
        x11111, y11111, x22222, y22222 = bbox5
        frame = cv2.rectangle(frame, (x11111, y11111), (x22222, y22222), (255, 255, 0), 5)
        xgreen = x22222-x11111
        ygreen = y22222-y11111
        alphagreen = math.atan(xgreen/ygreen)*180/math.pi
        areagreen = xgreen*ygreen
        #print(bbox5)

    if areayellow > 150:
        if alphayellow < 90 and alphayellow > 60:
            if purpledot_y > 300 and purpledot_y != 0 or greendot_y < 300 and greendot_y != 0:
                print("A Saite")
            elif purpledot_y < 300 and purpledot_y != 0 or greendot_y > 300 and greendot_y != 0:
                print("D Saite")
        if alphayellow < 60:
            if purpledot_y > 300 and purpledot_y != 0 or greendot_y < 300 and greendot_y != 0:
                print("E Saite")
            elif purpledot_y < 300 and purpledot_y != 0 or greendot_y > 300 and greendot_y != 0:
                print("G Saite")
    elif areablue > 150:
        #print(alphablue)
        if alphablue < 90 and alphablue > 65:
            if purpledot_y > 300 and purpledot_y != 0 or greendot_y < 300 and greendot_y != 0:
                print("A Saite")
            elif purpledot_y < 300 and purpledot_y != 0 or greendot_y > 300 and greendot_y != 0:
                print("D Saite")
        if alphablue < 65:
            if purpledot_y > 300 and purpledot_y != 0 or greendot_y < 300 and greendot_y != 0:
                print("E Saite")
            elif purpledot_y < 300 and purpledot_y != 0 or greendot_y > 300 and greendot_y != 0:
                print("G Saite")
    elif areagreen > 150:
        print(alphagreen)



    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
