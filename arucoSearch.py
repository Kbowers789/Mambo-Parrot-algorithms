"""
Demo of the groundcam
Mambo takes off, takes a picture and shows a RANDOM frame, not the last one
Author: Valentin Benke, https://github.com/Vabe7
Author: Amy McGovern
"""

from pyparrot.Minidrone import Mambo
import cv2
import cv2.aruco as aruco
import numpy as np

mambo = Mambo(None, use_wifi=True)  # address is None since it only works with WiFi anyway
print("trying to connect to mambo now")
success = mambo.connect(num_retries=3)
print("connected: %s" % success)

# Aruco parameters for their respective methods
ARUCO_PARAMETERS = aruco.DetectorParameters_create()
ARUCO_DICT = aruco.Dictionary_get(aruco.DICT_7X7_50)

if (success):
    # get the state information
    print("sleeping")
    mambo.smart_sleep(1)
    mambo.ask_for_state_update()
    mambo.smart_sleep(1)
    mambo.safe_takeoff(5)

    found = False
    loop = 0
    dist = 0.1
    pictures = []

    # loop looking for marker
    while not found:
        # back-up deletion of mambo picture files in case there are any lingering in memory
        pictures = mambo.groundcam.get_groundcam_pictures_names()
        if len(pictures) > 0:
            for i in range(0, len(pictures)):
                mambo.groundcam._delete_file(pictures[i])

        # take the photo
        pic_success = mambo.take_picture()

        while len(pictures) == 0:
            pictures = mambo.groundcam.get_groundcam_pictures_names()
            mambo.smart_sleep(0.1)

        print(pictures)

        frame = mambo.groundcam.get_groundcam_picture(pictures[0], True)

        if frame is not None:
            if frame is not False:
                cv2.imshow("Groundcam", frame)
                cv2.waitKey(100)

                # switching to grayscale image
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # detecting and highlighting Aruco markers
                corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, ARUCO_DICT, parameters=ARUCO_PARAMETERS)
                frame = aruco.drawDetectedMarkers(frame, corners, ids)

                # processing images in a way we can interpret the location of the aruco shape
                # for reference:
                # x axis points right-left (width), and y axis points up-down (height)
                npframe = np.array(frame)
                print(npframe.shape)

                center_y = npframe.shape[0] / 2
                center_x = npframe.shape[1] / 2

                # determining if we see a marker, and if it is centered under the groundcam
                if ids is not None:
                    cv2.imshow("Groundcam", frame)
                    cv2.waitKey(100)
                    if len(ids) > 0:
                        # we found a marker - now need to determine it's relative location from the center of the image

                        upleft_corner = corners[0][0][0]
                        print(upleft_corner)

                        # Using a tuple to determine upper left corner of marker in terms of x and y axis
                        # 0 represents "within goal range"
                        # -1 represents a negative difference from goal range (left of and/or in front of)
                        # 1 represents a positive difference from goal range (right of and/or behind)
                        x_diff = center_x - upleft_corner[0]
                        y_diff = center_y - upleft_corner[1]
                        print("x-diff =", x_diff)
                        print("y-diff =", y_diff)

                        res = [0,0]

                        # finding res[] values
                        # x axis
                        if center_x - 100 < upleft_corner[0] <= center_x:
                            # we are within "landing range" on the x axis
                            res[0] = 0
                        elif x_diff < 0:
                            # we are too far left, and need to move right
                            res[0] = -1
                        else:
                            # we are too far right and need to move left
                            res[0] = 1
                        # y axis
                        if center_y - 100 < upleft_corner[1] <= center_y:
                            # we are within "landing range" on the y axis
                            res[1] = 0
                        elif y_diff < 0:
                            # we are too far "south", and need to move forward
                            res[1] = -1
                        else:
                            # we are too far "north" and need to move backward
                            res[1] = 1
                        print("res =", res)

                        if res == [0,0]:
                            found = True
                            mambo.groundcam._delete_file(pictures[0])
                            continue
                        if res[0] == 1:
                            print("moving more left")
                            mambo.turn_degrees(-90)
                            mambo.fly_direct(roll=0, pitch=30, yaw=0, vertical_movement=0, duration=0.2)
                            mambo.turn_degrees(90)
                        if res[0] == -1:
                            print("moving more right")
                            mambo.turn_degrees(90)
                            mambo.fly_direct(roll=0, pitch=30, yaw=0, vertical_movement=0, duration=0.2)
                            mambo.turn_degrees(-90)
                        if res[1] == -1:
                            print("moving backward")
                            mambo.fly_direct(roll=0, pitch=-25, yaw=0, vertical_movement=0, duration=0.1)
                        if res[1] == 1:
                            print("moving more forward")
                            mambo.fly_direct(roll=0, pitch=25, yaw=0, vertical_movement=0, duration=0.1)
                else:
                    # need to move a bit to take another picture
                    mambo.fly_direct(roll=0, pitch=30, yaw=0, vertical_movement=0, duration=dist)
                    mambo.turn_degrees(90)
                    loop += 1
                    if loop == 4:
                        dist += 0.1
                        loop = 0
                mambo.groundcam._delete_file(pictures[0])

    mambo.safe_land(5)
    mambo.disconnect()
