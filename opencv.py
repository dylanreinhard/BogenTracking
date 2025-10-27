import cv2
import numpy
from PIL import Image
import math
import time  # <-- Added for time tracking

from pandas.core.interchange.from_dataframe import primitive_column_to_ndarray

from util import get_limits
import seaborn as sns
import matplotlib.pyplot as plt

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

marker_length = 0.02

# Definiere die Farbwerte im BGR-Farbraum
yellow = [26, 214, 232]
blue = [255, 255, 139]
purple = [213, 131, 250]
green = [161, 223, 145]
dark_green = [91, 129, 41]

bow_location = []
bow_time = []

cap = cv2.VideoCapture(1)
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = cv2.resize(frame, (640, 480))

    bboxYellow = 0 # Marker 0 and 1
    bboxBlue = 0   # Marker 1 and 2
    bboxGreen = 0 # Marker 2 and 3

    alphayellow = 0 # Winkel für gelbe Markierung
    alphablue = 0   # Winkel für blaue Markierung
    alphagreen = 0  # Winkel für dunkel grüne Markierung
    areayellow = 0  # Fläche der gelben Markierung
    areablue = 0    # Fläche der blauen Markierung
    areagreen = 0   # Fläche der dunkel grünen Markierung
    purpledot_y = 0 # y-Koordinate Marker 1
    greendot_y = 0  # y-Koordinate Marker 3
    e_contact_point = (310, 300)
    a_contact_point = (330, 300)
    d_contact_point = (350, 300)
    g_contact_point = (360, 300)
    half_bow = 31
    quarter_bow = 15
    full_bow = 62
    darkgreen_dot = 50 # Marker 2
    blue_dot = 35 # Marker 1
    yellow_dot = 4 # Marker 0

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = detector.detectMarkers(gray)

    MARKER_IDS = {0, 1, 2, 3}
    marker_pixels = {mid: None for mid in MARKER_IDS}

    if ids is not None:
        for i, corner in enumerate(corners):
            mid = int(ids[i][0])
            if mid in MARKER_IDS:
                pts = corner.reshape((4, 2))  # four (x, y) corners
                cx, cy = pts.mean(axis=0)  # centroid as floats
                marker_pixels[mid] = (int(round(cx)), int(round(cy)))

    # print only detected markers
    for mid, coords in marker_pixels.items():
        if coords is not None:
            print(f"id {mid}: {coords}")

    # example: read marker 0 coords safely
    coords0 = marker_pixels.get(0)
    if coords0:
        x_pixel, y_pixel = coords0

    xYellow = marker_pixels.get(1)[0] - marker_pixels.get(0)[0]
    yYellow = marker_pixels.get(1)[1] - marker_pixels.get(0)[1]
    alphayellow = math.atan2(xYellow, yYellow) * 180 / math.pi
    areayellow = abs(xYellow * yYellow)

    xBlue = marker_pixels.get(2)[0] - marker_pixels.get(1)[0]
    yBlue = marker_pixels.get(2)[1] - marker_pixels.get(1)[1]
    alphablue = math.atan2(xBlue, yBlue) * 180 / math.pi
    areablue = abs(xBlue * yBlue)

    xDarkGreen = marker_pixels.get(3)[0] - marker_pixels.get(2)[0]
    yDarkGreen = marker_pixels.get(3)[1] - marker_pixels.get(2)[1]
    alphagreen = math.atan2(xDarkGreen, yDarkGreen) * 180 / math.pi
    areagreen = abs(xDarkGreen * yDarkGreen)

    purpledot_y = marker_pixels.get(0)[1]
    greendot_y = marker_pixels.get(3)[1]

    if areayellow > 1500:
        if 60 < alphayellow < 90:
            if (purpledot_y > 300 and purpledot_y != 0) or (greendot_y < 300 and greendot_y != 0):
                #print("D Saite")
                yellowPixelDistance = math.sqrt((xYellow) ** 2 + (yYellow) ** 2)
                yellowDistanceRatio = half_bow / yellowPixelDistance
                # print(yellowDistanceRatio)
                distance = math.sqrt((d_contact_point[0] - xYellow) ** 2 + (d_contact_point[1] - yYellow) ** 2)
                realDistance = distance * yellowDistanceRatio

                if xYellow > d_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Yellow")

                if vorzeichen == "-":
                    now = time.time()
                    bow_location.append(yellow_dot - realDistance)
                    bow_time.append(now)
                elif vorzeichen == "+":
                    now = time.time()
                    bow_location.append(yellow_dot + realDistance)
                    bow_time.append(now)
            elif (purpledot_y < 300 and purpledot_y != 0) or (greendot_y > 300 and greendot_y != 0):
                #print("A Saite")
                yellowPixelDistance = math.sqrt((xYellow) ** 2 + (yYellow) ** 2)
                yellowDistanceRatio = half_bow / yellowPixelDistance
                #print(yellowDistanceRatio)
                distance=math.sqrt((a_contact_point[0] - xYellow) ** 2 + (a_contact_point[1] - yYellow) ** 2)
                realDistance=distance*yellowDistanceRatio

                if xYellow > a_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Yellow")

                if vorzeichen == "-":
                    now = time.time()
                    bow_location.append(yellow_dot - realDistance)
                    bow_time.append(now)
                elif vorzeichen == "+":
                    now = time.time()
                    bow_location.append(yellow_dot + realDistance)
                    bow_time.append(now)
        if alphayellow < 60:
            if (purpledot_y > 300 and purpledot_y != 0) or (greendot_y < 300 and greendot_y != 0):
                #print("G Saite")
                yellowPixelDistance = math.sqrt((xYellow) ** 2 + (yYellow) ** 2)
                yellowDistanceRatio = half_bow / yellowPixelDistance
                # print(yellowDistanceRatio)
                distance = math.sqrt((g_contact_point[0] - xYellow) ** 2 + (g_contact_point[1] - yYellow) ** 2)
                realDistance = distance * yellowDistanceRatio

                if xYellow > g_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Yellow")

                if vorzeichen == "-":
                    now = time.time()
                    bow_location.append(yellow_dot - realDistance)
                    bow_time.append(now)
                elif vorzeichen == "+":
                    now = time.time()
                    bow_location.append(yellow_dot + realDistance)
                    bow_time.append(now)
            elif (purpledot_y < 300 and purpledot_y != 0) or (greendot_y > 300 and greendot_y != 0):
                #print("E Saite")
                yellowPixelDistance = math.sqrt((xYellow) ** 2 + (yYellow) ** 2)
                yellowDistanceRatio = half_bow / yellowPixelDistance
                # print(yellowDistanceRatio)
                distance = math.sqrt((e_contact_point[0] - xYellow) ** 2 + (e_contact_point[1] - yYellow) ** 2)
                realDistance = distance * yellowDistanceRatio

                if xYellow > e_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Yellow")

                if vorzeichen == "-":
                    now = time.time()
                    bow_location.append(yellow_dot - realDistance)
                    bow_time.append(now)
                elif vorzeichen == "+":
                    now = time.time()
                    bow_location.append(yellow_dot + realDistance)
                    bow_time.append(now)
    elif areablue > 150 and areayellow < 1500:
        if 65 < alphablue < 90:
            if (purpledot_y > 300 and purpledot_y != 0) or (greendot_y < 300 and greendot_y != 0):
                #print("D Saite")
                bluePixelDistance = math.sqrt((xBlue) ** 2 + (yBlue) ** 2)
                blueDistanceRatio = quarter_bow / bluePixelDistance
                distance = math.sqrt((d_contact_point[0] - xYellow) ** 2 + (d_contact_point[1] - yYellow) ** 2)
                realDistance = distance * blueDistanceRatio

                if xBlue > d_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Blue")

                if vorzeichen == "-":
                    now = time.time()
                    bow_location.append(blue_dot - realDistance)
                    bow_time.append(now)
                elif vorzeichen == "+":
                    now = time.time()
                    bow_location.append(blue_dot + realDistance)
                    bow_time.append(now)
            elif (purpledot_y < 300 and purpledot_y != 0) or (greendot_y > 300 and greendot_y != 0):
                #print("A Saite")
                bluePixelDistance = math.sqrt((xBlue) ** 2 + (yBlue) ** 2)
                blueDistanceRatio = quarter_bow / bluePixelDistance
                distance = math.sqrt((a_contact_point[0] - xBlue) ** 2 + (a_contact_point[1] - yBlue) ** 2)
                realDistance = distance * blueDistanceRatio

                if xBlue > a_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Blue")

                if vorzeichen == "-":
                    now = time.time()
                    bow_location.append(blue_dot - realDistance)
                    bow_time.append(now)
                elif vorzeichen == "+":
                    now = time.time()
                    bow_location.append(blue_dot + realDistance)
                    bow_time.append(now)
        if alphablue < 65:
            if (purpledot_y > 300 and purpledot_y != 0) or (greendot_y < 300 and greendot_y != 0):
                #print("G Saite")
                bluePixelDistance = math.sqrt((xBlue) ** 2 + (yBlue) ** 2)
                blueDistanceRatio = quarter_bow / bluePixelDistance
                distance = math.sqrt((g_contact_point[0] - xBlue) ** 2 + (g_contact_point[1] - yBlue) ** 2)
                realDistance = distance * blueDistanceRatio

                if xBlue > g_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Blue")

                if vorzeichen == "-":
                    now = time.time()
                    bow_location.append(blue_dot - realDistance)
                    bow_time.append(now)
                elif vorzeichen == "+":
                    now = time.time()
                    bow_location.append(blue_dot + realDistance)
                    bow_time.append(now)
            elif (purpledot_y < 300 and purpledot_y != 0) or (greendot_y > 300 and greendot_y != 0):
                #print("E Saite")
                bluePixelDistance = math.sqrt((xBlue) ** 2 + (yBlue) ** 2)
                blueDistanceRatio = quarter_bow / bluePixelDistance
                distance = math.sqrt((e_contact_point[0] - xBlue) ** 2 + (e_contact_point[1] - yBlue) ** 2)
                realDistance = distance * blueDistanceRatio

                if xBlue > e_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Blue")

                if vorzeichen == "-":
                    now = time.time()
                    bow_location.append(blue_dot - realDistance)
                    bow_time.append(now)
                elif vorzeichen == "+":
                    now = time.time()
                    bow_location.append(blue_dot + realDistance)
                    bow_time.append(now)
    elif areagreen > 150 and areablue < 150 and areayellow < 1500:
        if 70 < alphagreen < 90:
            if (greendot_y > 300 and greendot_y != 0):
                #print("D Saite")
                greenPixelDistance = math.sqrt((xDarkGreen) ** 2 + (yDarkGreen) ** 2)
                greenDistanceRatio = quarter_bow / greenPixelDistance
                distance = math.sqrt((d_contact_point[0] - xDarkGreen) ** 2 + (d_contact_point[1] - yDarkGreen) ** 2)
                realDistance = distance * greenDistanceRatio

                if xDarkGreen > d_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Green")

                if vorzeichen == "-":
                    now = time.time()
                    bow_location.append(darkgreen_dot - realDistance)
                    bow_time.append(now)
                elif vorzeichen == "+":
                    now = time.time()
                    bow_location.append(darkgreen_dot + realDistance)
                    bow_time.append(now)
        if alphagreen < 70:
            if (greendot_y > 300 and greendot_y != 0):
                #print("G Saite")
                greenPixelDistance = math.sqrt((xDarkGreen) ** 2 + (yDarkGreen) ** 2)
                greenDistanceRatio = quarter_bow / greenPixelDistance
                distance = math.sqrt((a_contact_point[0] - xDarkGreen) ** 2 + (a_contact_point[1] - yDarkGreen) ** 2)
                realDistance = distance * greenDistanceRatio

                if xDarkGreen > g_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Green")

                if vorzeichen == "-":
                    now = time.time()
                    bow_location.append(darkgreen_dot - realDistance)
                    bow_time.append(now)
                elif vorzeichen == "+":
                    now = time.time()
                    bow_location.append(darkgreen_dot + realDistance)
                    bow_time.append(now)
        if 60 < alphagreen < 90:
            if (greendot_y < 300 and greendot_y != 0):
                #print("A Saite")
                greenPixelDistance = math.sqrt((xDarkGreen) ** 2 + (yDarkGreen) ** 2)
                greenDistanceRatio = quarter_bow / greenPixelDistance
                distance = math.sqrt((g_contact_point[0] - xDarkGreen) ** 2 + (g_contact_point[1] - yDarkGreen) ** 2)
                realDistance = distance * greenDistanceRatio

                if xDarkGreen > a_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Green")

                if vorzeichen == "-":
                    now = time.time()
                    bow_location.append(darkgreen_dot - realDistance)
                    bow_time.append(now)
                elif vorzeichen == "+":
                    now = time.time()
                    bow_location.append(darkgreen_dot + realDistance)
                    bow_time.append(now)
        if alphagreen < 60:
            if (greendot_y < 300 and greendot_y != 0):
                #print("E Saite")
                greenPixelDistance = math.sqrt((xDarkGreen) ** 2 + (yDarkGreen) ** 2)
                greenDistanceRatio = quarter_bow / greenPixelDistance
                distance = math.sqrt((e_contact_point[0] - xDarkGreen) ** 2 + (e_contact_point[1] - yDarkGreen) ** 2)
                realDistance = distance * greenDistanceRatio

                if xDarkGreen > e_contact_point[0]:
                    vorzeichen = "-"
                else:
                    vorzeichen = "+"

                print(vorzeichen + f"{realDistance} away from Green")

                if vorzeichen == "-":
                    now = time.time()
                    bow_location.append(darkgreen_dot - realDistance)
                    bow_time.append(now)
                elif vorzeichen == "+":
                    now = time.time()
                    bow_location.append(darkgreen_dot + realDistance)
                    bow_time.append(now)

    cv2.imshow('frame', frame)


    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

totalDistance = 0

print(bow_location)

filtered_locations = []
filtered_times = []

MIN_VELOCITY = 0
MAX_VELOCITY = 75

filtered_locations = []
filtered_times = []

for i in range(len(bow_location) - 1):
    loc1, loc2 = bow_location[i], bow_location[i + 1]
    t1, t2 = bow_time[i], bow_time[i + 1]
    time_diff = t2 - t1

    if time_diff > 0:
        velocity = abs((loc2 - loc1) / time_diff)
        if MIN_VELOCITY <= velocity <= MAX_VELOCITY:
            filtered_locations.append(loc2)
            filtered_times.append(t2)

print(filtered_locations)

velocities = []
for i in range(len(filtered_locations) - 1):
    difference = abs(filtered_locations[i+1] - filtered_locations[i])
    time_diff = filtered_times[i+1] - filtered_times[i]
    totalDistance += difference
    velocities.append(difference / time_diff)


print("Total Distance", totalDistance, "cm")
print("Velocities:", velocities)

if velocities:
    avg_velocity = sum(velocities) / len(velocities)
    print("Average velocity:", avg_velocity)

plt.figure(figsize=(10, 4))
sns.histplot(filtered_locations, bins=31, kde=True, binrange=(0, 62))
plt.title("Bow Location Frequency")
plt.xlabel("Bow Location (cm)")
plt.ylabel("Frequency")
plt.xlim(0, 62)
plt.show()

