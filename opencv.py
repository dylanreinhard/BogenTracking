import cv2
import numpy
from PIL import Image
import math
from util import get_limits

# Definiere die Farbwerte im BGR-Farbraum
yellow = [26, 214, 232]
blue = [255, 255, 139]
purple = [213, 131, 250]
green = [161, 223, 145]
dark_green = [91, 129, 41]

bow_location = []

cap = cv2.VideoCapture(1)
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = cv2.resize(frame, (640, 480))
    hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lowerLimitYellow, upperLimitYellow = get_limits(color=yellow)
    lowerLimitBlue, upperLimitBlue = get_limits(color=blue)
    lowerLimitPurple, upperLimitPurple = get_limits(color=purple)
    lowerLimitGreen, upperLimitGreen = get_limits(color=green)
    lowerLimitDarkGreen, upperLimitDarkGreen = get_limits(color=dark_green)

    maskYellow = cv2.inRange(hsvImage, lowerLimitYellow, upperLimitYellow)
    maskBlue = cv2.inRange(hsvImage, lowerLimitBlue, upperLimitBlue)
    maskPurple = cv2.inRange(hsvImage, lowerLimitPurple, upperLimitPurple)
    maskGreen = cv2.inRange(hsvImage, lowerLimitGreen, upperLimitGreen)
    maskDarkGreen = cv2.inRange(hsvImage, lowerLimitDarkGreen, upperLimitDarkGreen)

    maskYellow_ = Image.fromarray(maskYellow)
    maskBlue_ = Image.fromarray(maskBlue)
    maskPurple_ = Image.fromarray(maskPurple)
    maskGreen_ = Image.fromarray(maskGreen)
    maskDarkGreen_ = Image.fromarray(maskDarkGreen)

    bboxYellow = maskYellow_.getbbox()
    bboxBlue = maskBlue_.getbbox()
    bboxPurple = maskPurple_.getbbox()
    bboxGreen = maskGreen_.getbbox()
    bboxDarkGreen = maskDarkGreen_.getbbox()

    alphayellow = 0 # Winkel für gelbe Markierung
    alphablue = 0   # Winkel für blaue Markierung
    alphagreen = 0  # Winkel für dunkel grüne Markierung
    areayellow = 0  # Fläche der gelben Markierung
    areablue = 0    # Fläche der blauen Markierung
    areagreen = 0   # Fläche der dunkel grünen Markierung
    purpledot_y = 0 # y-Koordinate des lila Punktes
    greendot_y = 0  # y-Koordinate des grünen Punktes
    e_contact_point = (310, 300)
    a_contact_point = (330, 300)
    d_contact_point = (350, 300)
    g_contact_point = (360, 300)
    half_bow = 31
    quarter_bow = 15
    darkgreen_dot = 50
    blue_dot = 35
    yellow_dot = 4

    x1Yellow, y1Yellow, x2Yellow, y2Yellow = 0,0,0,0

    x1Blue, y1Blue, x2Blue, y2Blue = 0,0,0,0

    x1Purple, y1Purple, x2Purple, y2Purple = 0,0,0,0

    x1Green, y1Green, x2Green, y2Green = 0,0,0,0

    x1DarkGreen, y1DarkGreen, x2DarkGreen, y2DarkGreen = 0,0,0,0

    if bboxYellow is not None:
        x1Yellow, y1Yellow, x2Yellow, y2Yellow = bboxYellow
        frame = cv2.rectangle(frame, (x1Yellow, y1Yellow), (x2Yellow, y2Yellow), (0, 255, 0), 5)
        xYellow = x2Yellow - x1Yellow
        yYellow = y2Yellow - y1Yellow
        alphayellow = math.atan(xYellow / yYellow) * 180 / math.pi
        areayellow = xYellow * yYellow
        #print(bboxYellow)

    if bboxBlue is not None:
        x1Blue, y1Blue, x2Blue, y2Blue = bboxBlue
        frame = cv2.rectangle(frame, (x1Blue, y1Blue), (x2Blue, y2Blue), (0, 0, 255), 5)
        xBlue = x2Blue - x1Blue
        yBlue = y2Blue - y1Blue
        alphablue = math.atan(xBlue / yBlue) * 180 / math.pi
        areablue = xBlue * yBlue

    if bboxPurple is not None:
        x1Purple, y1Purple, x2Purple, y2Purple = bboxPurple
        frame = cv2.rectangle(frame, (x1Purple, y1Purple), (x2Purple, y2Purple), (255, 0, 0), 5)
        purpledot_y = y1Purple

    if bboxGreen is not None:
        x1Green, y1Green, x2Green, y2Green = bboxGreen
        frame = cv2.rectangle(frame, (x1Green, y1Green), (x2Green, y2Green), (0, 255, 255), 5)
        greendot_y = y1Green

    if bboxDarkGreen is not None:
        x1DarkGreen, y1DarkGreen, x2DarkGreen, y2DarkGreen = bboxDarkGreen
        frame = cv2.rectangle(frame, (x1DarkGreen, y1DarkGreen), (x2DarkGreen, y2DarkGreen), (255, 255, 0), 5)
        xDarkGreen = x2DarkGreen - x1DarkGreen
        yDarkGreen = y2DarkGreen - y1DarkGreen
        alphagreen = math.atan(xDarkGreen / yDarkGreen) * 180 / math.pi
        areagreen = xDarkGreen * yDarkGreen

    if areayellow > 150:
        if 60 < alphayellow < 90:
            if (purpledot_y > 300 and purpledot_y != 0) or (greendot_y < 300 and greendot_y != 0):
                #print("D Saite")
                yellowPixelDistance = math.sqrt((x2Yellow - x1Yellow) ** 2 + (y2Yellow - y1Yellow) ** 2)
                yellowDistanceRatio = half_bow / yellowPixelDistance
                # print(yellowDistanceRatio)
                distance = math.sqrt((d_contact_point[0] - x1Yellow) ** 2 + (d_contact_point[1] - y2Yellow) ** 2)
                realDistance = distance * yellowDistanceRatio

                if x1Yellow > d_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Yellow")

                if vorzeichen == "-":
                    bow_location.append(yellow_dot - realDistance)
                elif vorzeichen == "+":
                    bow_location.append(yellow_dot + realDistance)
            elif (purpledot_y < 300 and purpledot_y != 0) or (greendot_y > 300 and greendot_y != 0):
                #print("A Saite")
                yellowPixelDistance = math.sqrt((x2Yellow - x1Yellow) ** 2 + (y2Yellow - y1Yellow) ** 2)
                yellowDistanceRatio = half_bow / yellowPixelDistance
                #print(yellowDistanceRatio)
                distance=math.sqrt((a_contact_point[0] - x1Yellow) ** 2 + (a_contact_point[1] - y2Yellow) ** 2)
                realDistance=distance*yellowDistanceRatio

                if x1Yellow > a_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Yellow")

                if vorzeichen == "-":
                    bow_location.append(yellow_dot - realDistance)
                elif vorzeichen == "+":
                    bow_location.append(yellow_dot + realDistance)
        if alphayellow < 60:
            if (purpledot_y > 300 and purpledot_y != 0) or (greendot_y < 300 and greendot_y != 0):
                #print("G Saite")
                yellowPixelDistance = math.sqrt((x2Yellow - x1Yellow) ** 2 + (y2Yellow - y1Yellow) ** 2)
                yellowDistanceRatio = half_bow / yellowPixelDistance
                # print(yellowDistanceRatio)
                distance = math.sqrt((g_contact_point[0] - x1Yellow) ** 2 + (g_contact_point[1] - y2Yellow) ** 2)
                realDistance = distance * yellowDistanceRatio

                if x1Yellow > g_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Yellow")

                if vorzeichen == "-":
                    bow_location.append(yellow_dot - realDistance)
                elif vorzeichen == "+":
                    bow_location.append(yellow_dot + realDistance)
            elif (purpledot_y < 300 and purpledot_y != 0) or (greendot_y > 300 and greendot_y != 0):
                #print("E Saite")
                yellowPixelDistance = math.sqrt((x2Yellow - x1Yellow) ** 2 + (y2Yellow - y1Yellow) ** 2)
                yellowDistanceRatio = half_bow / yellowPixelDistance
                # print(yellowDistanceRatio)
                distance = math.sqrt((e_contact_point[0] - x1Yellow) ** 2 + (e_contact_point[1] - y2Yellow) ** 2)
                realDistance = distance * yellowDistanceRatio

                if x1Yellow > e_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Yellow")

                if vorzeichen == "-":
                    bow_location.append(yellow_dot - realDistance)
                elif vorzeichen == "+":
                    bow_location.append(yellow_dot + realDistance)
    elif areablue > 150 and areayellow < 150:
        if 65 < alphablue < 90:
            if (purpledot_y > 300 and purpledot_y != 0) or (greendot_y < 300 and greendot_y != 0):
                #print("D Saite")
                bluePixelDistance = math.sqrt((x2Blue - x1Blue) ** 2 + (y2Blue - y1Blue) ** 2)
                blueDistanceRatio = quarter_bow / bluePixelDistance
                distance = math.sqrt((d_contact_point[0] - x1Yellow) ** 2 + (d_contact_point[1] - y2Yellow) ** 2)
                realDistance = distance * blueDistanceRatio

                if x1Blue > d_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Blue")

                if vorzeichen == "-":
                    bow_location.append(blue_dot - realDistance)
                elif vorzeichen == "+":
                    bow_location.append(blue_dot + realDistance)
            elif (purpledot_y < 300 and purpledot_y != 0) or (greendot_y > 300 and greendot_y != 0):
                #print("A Saite")
                bluePixelDistance = math.sqrt((x2Blue - x1Blue) ** 2 + (y2Blue - y1Blue) ** 2)
                blueDistanceRatio = quarter_bow / bluePixelDistance
                distance = math.sqrt((a_contact_point[0] - x1Yellow) ** 2 + (a_contact_point[1] - y2Yellow) ** 2)
                realDistance = distance * blueDistanceRatio

                if x1Blue > a_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Blue")

                if vorzeichen == "-":
                    bow_location.append(blue_dot - realDistance)
                elif vorzeichen == "+":
                    bow_location.append(blue_dot + realDistance)
        if alphablue < 65:
            if (purpledot_y > 300 and purpledot_y != 0) or (greendot_y < 300 and greendot_y != 0):
                #print("G Saite")
                bluePixelDistance = math.sqrt((x2Blue - x1Blue) ** 2 + (y2Blue - y1Blue) ** 2)
                blueDistanceRatio = quarter_bow / bluePixelDistance
                distance = math.sqrt((g_contact_point[0] - x1Blue) ** 2 + (g_contact_point[1] - y2Blue) ** 2)
                realDistance = distance * blueDistanceRatio

                if x1Blue > g_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Blue")

                if vorzeichen == "-":
                    bow_location.append(blue_dot - realDistance)
                elif vorzeichen == "+":
                    bow_location.append(blue_dot + realDistance)
            elif (purpledot_y < 300 and purpledot_y != 0) or (greendot_y > 300 and greendot_y != 0):
                #print("E Saite")
                bluePixelDistance = math.sqrt((x2Blue - x1Blue) ** 2 + (y2Blue - y1Blue) ** 2)
                blueDistanceRatio = quarter_bow / bluePixelDistance
                distance = math.sqrt((e_contact_point[0] - x1Yellow) ** 2 + (e_contact_point[1] - y2Yellow) ** 2)
                realDistance = distance * blueDistanceRatio

                if x1Blue > e_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Blue")

                if vorzeichen == "-":
                    bow_location.append(blue_dot - realDistance)
                elif vorzeichen == "+":
                    bow_location.append(blue_dot + realDistance)
    elif areagreen > 150 and areablue < 150 and areayellow < 150:
        if 70 < alphagreen < 90:
            if (greendot_y > 300 and greendot_y != 0):
                #print("D Saite")
                greenPixelDistance = math.sqrt((x2DarkGreen - x1DarkGreen) ** 2 + (y2DarkGreen - y1DarkGreen) ** 2)
                greenDistanceRatio = quarter_bow / greenPixelDistance
                distance = math.sqrt((d_contact_point[0] - x1DarkGreen) ** 2 + (d_contact_point[1] - y2DarkGreen) ** 2)
                realDistance = distance * greenDistanceRatio

                if x1DarkGreen > d_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Green")

                if vorzeichen == "-":
                    bow_location.append(darkgreen_dot - realDistance)
                elif vorzeichen == "+":
                    bow_location.append(darkgreen_dot + realDistance)
        if alphagreen < 70:
            if (greendot_y > 300 and greendot_y != 0):
                #print("G Saite")
                greenPixelDistance = math.sqrt((x2DarkGreen - x1DarkGreen) ** 2 + (y2DarkGreen - y1DarkGreen) ** 2)
                greenDistanceRatio = quarter_bow / greenPixelDistance
                distance = math.sqrt((a_contact_point[0] - x1DarkGreen) ** 2 + (a_contact_point[1] - y2DarkGreen) ** 2)
                realDistance = distance * greenDistanceRatio

                if x1DarkGreen > g_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Green")

                if vorzeichen == "-":
                    bow_location.append(darkgreen_dot - realDistance)
                elif vorzeichen == "+":
                    bow_location.append(darkgreen_dot + realDistance)
        if 60 < alphagreen < 90:
            if (greendot_y < 300 and greendot_y != 0):
                #print("A Saite")
                greenPixelDistance = math.sqrt((x2DarkGreen - x1DarkGreen) ** 2 + (y2DarkGreen - y1DarkGreen) ** 2)
                greenDistanceRatio = quarter_bow / greenPixelDistance
                distance = math.sqrt((g_contact_point[0] - x1DarkGreen) ** 2 + (g_contact_point[1] - y2DarkGreen) ** 2)
                realDistance = distance * greenDistanceRatio

                if x1DarkGreen > a_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Green")

                if vorzeichen == "-":
                    bow_location.append(darkgreen_dot - realDistance)
                elif vorzeichen == "+":
                    bow_location.append(darkgreen_dot + realDistance)
        if alphagreen < 60:
            if (greendot_y < 300 and greendot_y != 0):
                #print("E Saite")
                greenPixelDistance = math.sqrt((x2DarkGreen - x1DarkGreen) ** 2 + (y2DarkGreen - y1DarkGreen) ** 2)
                greenDistanceRatio = quarter_bow / greenPixelDistance
                distance = math.sqrt((e_contact_point[0] - x1DarkGreen) ** 2 + (e_contact_point[1] - y2DarkGreen) ** 2)
                realDistance = distance * greenDistanceRatio

                if x1DarkGreen > e_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Green")

                if vorzeichen == "-":
                    bow_location.append(darkgreen_dot - realDistance)
                elif vorzeichen == "+":
                    bow_location.append(darkgreen_dot + realDistance)


    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

totalDistance = 0

print(bow_location)

for i in range(len(bow_location) - 1):
    difference = math.sqrt((bow_location[i+1] - bow_location[i])**2)
    if difference < 15:
        totalDistance += difference

print(totalDistance)
