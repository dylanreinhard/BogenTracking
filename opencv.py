import cv2
import numpy as np
from PIL import Image
import math
#import time  # <-- Removed for using video FPS

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

cap = cv2.VideoCapture(r'C:\Users\dylan\PycharmProjects\BogenTracking\2025-11-29 11-39-43.mp4')  # put your file path here
if not cap.isOpened():
    print("Cannot open video file")
    exit(1)
video_fps = cap.get(cv2.CAP_PROP_FPS)
if not video_fps or video_fps <= 0:
    video_fps = 60.0  # fallback FPS
frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    frame_time = frame_idx / video_fps  # timestamp for this frame
    frame_idx += 1

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
    areaorange = 0
    alphaorange = 0
    e_contact_point = (325, 300)
    a_contact_point = (345, 300)
    d_contact_point = (360, 300)
    g_contact_point = (380, 300)
    half_bow = 31
    quarter_bow = 14.5
    full_bow = 62
    orange_dot = 50
    darkgreen_dot = 35.5 # Marker 2
    blue_dot = 21.5 # Marker 1
    yellow_dot = 7 # Marker 0

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = detector.detectMarkers(gray)

    MARKER_IDS = {0, 1, 2, 3, 4}
    marker_pixels = {mid: None for mid in MARKER_IDS}

    if ids is not None:
        for i, corner in enumerate(corners):
            mid = int(ids[i][0])
            if mid in MARKER_IDS:
                pts = corner.reshape((4, 2))  # four (x, y) corners
                cx, cy = pts.mean(axis=0)  # centroid as floats
                marker_pixels[mid] = (int(round(cx)), int(round(cy)))

    # print only detected markers
    # for mid, coords in marker_pixels.items():
    #     if coords is not None:
    #         print(f"id {mid}: {coords}")

    # example: read marker 0 coords safely
    coords0 = marker_pixels.get(0)
    if coords0:
        x_pixel, y_pixel = coords0

    if marker_pixels.get(1) is not None and marker_pixels.get(0) is not None:
        xYellow = marker_pixels[1][0] - marker_pixels[0][0]
        yYellow = marker_pixels[1][1] - marker_pixels[0][1]
        alphayellow = math.atan2(xYellow, yYellow)
        areayellow = abs(xYellow * yYellow)
        #print(f"Alpha: {alphayellow}, Area: {areayellow}")

    if marker_pixels.get(2) is not None and marker_pixels.get(1) is not None:
        xBlue = marker_pixels[2][0] - marker_pixels[1][0]
        yBlue = marker_pixels[2][1] - marker_pixels[1][1]
        alphablue = math.atan2(xBlue, yBlue) * 180 / math.pi
        areablue = abs(xBlue * yBlue)
        #print(f"Alpha: {alphablue}, Area: {areablue}")

    if marker_pixels.get(3) is not None and marker_pixels.get(2) is not None:
        xDarkGreen = marker_pixels[3][0] - marker_pixels[2][0]
        yDarkGreen = marker_pixels[3][1] - marker_pixels[2][1]
        alphagreen = math.atan2(xDarkGreen, yDarkGreen) * 180 / math.pi
        areagreen = abs(xDarkGreen * yDarkGreen)
        #print(f"Alpha: {alphagreen}, Area: {areagreen}")

    if marker_pixels.get(4) is not None and marker_pixels.get(3) is not None:
        xOrange = marker_pixels[4][0] - marker_pixels[3][0]
        yOrange = marker_pixels[4][1] - marker_pixels[3][1]
        alphaorange = math.atan2(xOrange, yOrange) * 180 / math.pi
        areaorange = abs(xOrange * yOrange)
        #print(f"Alpha: {alphaorange}, Area: {areaorange}")

    if marker_pixels.get(0) is not None:
        purpledot_y = marker_pixels[0][1]
        purpledot_x = marker_pixels[0][0]
    if marker_pixels.get(4) is not None:
        greendot_y = marker_pixels[4][1]
        greendot_x = marker_pixels[4][0]

    if areayellow > 150:
        if 70 < alphayellow < 90:
            # print("D Saite")
            # use absolute marker position as reference and pixel distances
            ref_x, ref_y = marker_pixels[0]  # use the absolute pixel position of the measured marker
            yellowPixelDistance = math.sqrt(xYellow**2 + yYellow**2)
            yellowDistanceRatio = quarter_bow / yellowPixelDistance
            distance_px = math.hypot(d_contact_point[0] - ref_x, d_contact_point[1] - ref_y)
            realDistance = distance_px * yellowDistanceRatio

            if ref_x > d_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Yellow")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(yellow_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(yellow_dot + realDistance)
                bow_time.append(now)
        if 90 < alphayellow < 110:
            # print("A Saite")
            ref_x, ref_y = marker_pixels[0]
            yellowPixelDistance = math.sqrt(xYellow**2 + yYellow**2)
            yellowDistanceRatio = quarter_bow / yellowPixelDistance
            distance_px = math.hypot(a_contact_point[0] - ref_x, a_contact_point[1] - ref_y)
            realDistance = distance_px * yellowDistanceRatio

            if ref_x > a_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Yellow")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(yellow_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(yellow_dot + realDistance)
                bow_time.append(now)
        if alphayellow < 70:
            # print("G Saite")
            ref_x, ref_y = marker_pixels[0]
            yellowPixelDistance = math.sqrt(xYellow**2 + yYellow**2)
            yellowDistanceRatio = quarter_bow / yellowPixelDistance
            distance_px = math.hypot(g_contact_point[0] - ref_x, g_contact_point[1] - ref_y)
            realDistance = distance_px * yellowDistanceRatio

            if ref_x > g_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Yellow")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(yellow_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(yellow_dot + realDistance)
                bow_time.append(now)
        if 110 < alphayellow:
            # print("E Saite")
            ref_x, ref_y = marker_pixels[0]
            yellowPixelDistance = math.sqrt(xYellow**2 + yYellow**2)
            yellowDistanceRatio = quarter_bow / yellowPixelDistance
            distance_px = math.hypot(e_contact_point[0] - ref_x, e_contact_point[1] - ref_y)
            realDistance = distance_px * yellowDistanceRatio

            if ref_x > e_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Yellow")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(yellow_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(yellow_dot + realDistance)
                bow_time.append(now)
    elif areablue > 150 > areayellow:
        if 70 < alphablue < 90:
            # print("D Saite")
            ref_x, ref_y = marker_pixels[1]
            bluePixelDistance = math.sqrt(xBlue**2 + yBlue**2)
            blueDistanceRatio = quarter_bow / bluePixelDistance
            distance_px = math.hypot(d_contact_point[0] - ref_x, d_contact_point[1] - ref_y)
            realDistance = distance_px * blueDistanceRatio

            if ref_x > d_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Blue")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(blue_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(blue_dot + realDistance)
                bow_time.append(now)
        if 90 < alphablue < 110:
            # print("A Saite")
            ref_x, ref_y = marker_pixels[1]
            bluePixelDistance = math.sqrt(xBlue**2 + yBlue**2)
            blueDistanceRatio = quarter_bow / bluePixelDistance
            distance_px = math.hypot(a_contact_point[0] - ref_x, a_contact_point[1] - ref_y)
            realDistance = distance_px * blueDistanceRatio

            if ref_x > a_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Blue")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(blue_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(blue_dot + realDistance)
                bow_time.append(now)
        if alphablue < 70:
            # print("G Saite")
            ref_x, ref_y = marker_pixels[1]
            bluePixelDistance = math.sqrt(xBlue**2 + yBlue**2)
            blueDistanceRatio = quarter_bow / bluePixelDistance
            distance_px = math.hypot(g_contact_point[0] - ref_x, g_contact_point[1] - ref_y)
            realDistance = distance_px * blueDistanceRatio

            if ref_x > g_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Blue")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(blue_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(blue_dot + realDistance)
                bow_time.append(now)
        if 110 < alphablue:
            # print("E Saite")
            ref_x, ref_y = marker_pixels[1]
            bluePixelDistance = math.sqrt(xBlue**2 + yBlue**2)
            blueDistanceRatio = quarter_bow / bluePixelDistance
            distance_px = math.hypot(e_contact_point[0] - ref_x, e_contact_point[1] - ref_y)
            realDistance = distance_px * blueDistanceRatio

            if ref_x > e_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Blue")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(blue_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(blue_dot + realDistance)
                bow_time.append(now)
    elif areagreen > 150 and areablue < 150 and areayellow < 1500:
        if 70 < alphagreen < 95:
            # print("D Saite")
            ref_x, ref_y = marker_pixels[2]
            greenPixelDistance = math.sqrt(xDarkGreen**2 + yDarkGreen**2)
            greenDistanceRatio = quarter_bow / greenPixelDistance
            distance_px = math.hypot(d_contact_point[0] - ref_x, d_contact_point[1] - ref_y)
            realDistance = distance_px * greenDistanceRatio

            if ref_x > d_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Green")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(darkgreen_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(darkgreen_dot + realDistance)
                bow_time.append(now)
        if alphagreen < 70:
            # print("G Saite")
            ref_x, ref_y = marker_pixels[2]
            greenPixelDistance = math.sqrt(xDarkGreen ** 2 + yDarkGreen ** 2)
            greenDistanceRatio = quarter_bow / greenPixelDistance
            distance_px = math.hypot(a_contact_point[0] - ref_x, a_contact_point[1] - ref_y)
            realDistance = distance_px * greenDistanceRatio

            if ref_x > g_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Green")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(darkgreen_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(darkgreen_dot + realDistance)
                bow_time.append(now)
        if 95 < alphagreen < 115:
            # print("A Saite")
            ref_x, ref_y = marker_pixels[2]
            greenPixelDistance = math.sqrt(xDarkGreen ** 2 + yDarkGreen ** 2)
            greenDistanceRatio = quarter_bow / greenPixelDistance
            distance_px = math.hypot(g_contact_point[0] - ref_x, g_contact_point[1] - ref_y)
            realDistance = distance_px * greenDistanceRatio

            if ref_x > a_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Green")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(darkgreen_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(darkgreen_dot + realDistance)
                bow_time.append(now)
        if alphagreen > 115:
            # print("E Saite")
            ref_x, ref_y = marker_pixels[2]
            greenPixelDistance = math.sqrt(xDarkGreen ** 2 + yDarkGreen ** 2)
            greenDistanceRatio = quarter_bow / greenPixelDistance
            distance_px = math.hypot(e_contact_point[0] - ref_x, e_contact_point[1] - ref_y)
            realDistance = distance_px * greenDistanceRatio

            if ref_x > e_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Green")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(darkgreen_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(darkgreen_dot + realDistance)
                bow_time.append(now)
    elif areaorange > 150 and areagreen < 150 and areablue < 150 and areayellow < 1500:
        if 70 < alphaorange < 95:
            # print("D Saite")
            ref_x, ref_y = marker_pixels[3]
            greenPixelDistance = math.sqrt(xOrange**2 + yOrange**2)
            greenDistanceRatio = quarter_bow / greenPixelDistance
            distance_px = math.hypot(d_contact_point[0] - ref_x, d_contact_point[1] - ref_y)
            realDistance = distance_px * greenDistanceRatio

            if ref_x > d_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Green")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(orange_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(orange_dot + realDistance)
                bow_time.append(now)
        if alphaorange < 70:
            # print("G Saite")
            ref_x, ref_y = marker_pixels[3]
            greenPixelDistance = math.sqrt(xOrange ** 2 + yOrange ** 2)
            greenDistanceRatio = quarter_bow / greenPixelDistance
            distance_px = math.hypot(a_contact_point[0] - ref_x, a_contact_point[1] - ref_y)
            realDistance = distance_px * greenDistanceRatio

            if ref_x > g_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Green")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(orange_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(orange_dot + realDistance)
                bow_time.append(now)
        if 95 < alphaorange < 115:
            # print("A Saite")
            ref_x, ref_y = marker_pixels[3]
            greenPixelDistance = math.sqrt(xOrange ** 2 + yOrange ** 2)
            greenDistanceRatio = quarter_bow / greenPixelDistance
            distance_px = math.hypot(g_contact_point[0] - ref_x, g_contact_point[1] - ref_y)
            realDistance = distance_px * greenDistanceRatio

            if ref_x > a_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Green")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(orange_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(orange_dot + realDistance)
                bow_time.append(now)
        if alphaorange > 115:
            # print("E Saite")
            ref_x, ref_y = marker_pixels[3]
            greenPixelDistance = math.sqrt(xOrange ** 2 + yOrange ** 2)
            orangeDistanceRatio = quarter_bow / greenPixelDistance
            distance_px = math.hypot(e_contact_point[0] - ref_x, e_contact_point[1] - ref_y)
            realDistance = distance_px * orangeDistanceRatio

            if ref_x > e_contact_point[0]:
                vorzeichen = "-"
            else:
                vorzeichen = "+"

            print(vorzeichen + f"{realDistance} away from Green")

            if vorzeichen == "-":
                now = frame_time
                bow_location.append(orange_dot - realDistance)
                bow_time.append(now)
            elif vorzeichen == "+":
                now = frame_time
                bow_location.append(orange_dot + realDistance)
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
MAX_VELOCITY = 100

filtered_locations = []
filtered_times = []
velocities = []

for i in range(len(bow_location) - 1):
    loc1, loc2 = bow_location[i], bow_location[i + 1]
    t1, t2 = bow_time[i], bow_time[i + 1]
    time_diff = t2 - t1
    if time_diff <= 0:
        continue
    v = (loc2 - loc1) / time_diff
    v_abs = abs(v)
    if MIN_VELOCITY <= v_abs <= MAX_VELOCITY:
        if not filtered_locations:  # keep start of first valid segment
            filtered_locations.append(loc1)
            filtered_times.append(t1)
        filtered_locations.append(loc2)
        filtered_times.append(t2)
        velocities.append(v)

print(filtered_locations)

for i in range(len(filtered_locations) - 1):
    difference = filtered_locations[i+1] - filtered_locations[i]
    time_diff = filtered_times[i+1] - filtered_times[i]
    totalDistance += abs(difference)


print("Total Distance", totalDistance, "cm")
print("Velocities:", velocities)

# Total elapsed time
elapsed_time = filtered_times[-1] - filtered_times[0]

print("Elapsed Time:", elapsed_time, "s")

# Average speed over entire motion (distance / total time)
avg_speed_path = totalDistance / elapsed_time

print (avg_speed_path)

positions = np.array(filtered_locations)
times = np.array(filtered_times)
times = times - times.min()
velocity = np.diff(positions) / np.diff(times)
vel_times = times[:-1]

plt.figure(figsize=(10, 2))

# Histogram with many bins
hist, bins = np.histogram(positions, bins=80, range=(0, 62))

# Turn histogram into heatmap-style bar
plt.imshow(hist[np.newaxis, :],
           cmap="coolwarm",
           aspect="auto",
           extent=[0, 62, 0, 1])

plt.yticks([])
plt.xlabel("Bogenposition (cm)")
plt.title("Heatmap der Bogenposition (Häufigkeit)")

plt.colorbar(label="Häufigkeit")
plt.show()

plt.figure(figsize=(10,4))
plt.plot(times, positions, linewidth=1)
plt.xlabel("Zeit (s)")
plt.ylabel("Position auf dem Bogen (cm)")
plt.title("Bogenposition über Zeit")
plt.grid(True)
plt.show()

plt.figure(figsize=(10,4))
plt.plot(vel_times, velocity, linewidth=1)
plt.xlabel("Zeit (s)")
plt.ylabel("Geschwindigkeit (cm/s)")
plt.title("Bogengeschwindigkeit über Zeit")
plt.grid(True)
plt.show()

plt.figure(figsize=(10,4))
plt.scatter(positions[:-1], velocity, s=4)
plt.xlabel("Position auf dem Bogen (cm)")
plt.ylabel("Geschwindigkeit (cm/s)")
plt.title("Geschwindigkeit in Abhängigkeit der Bogenposition")
plt.grid(True)
plt.show()


