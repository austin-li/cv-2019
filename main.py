from Target import Target
from TargetDetector import TargetDetector as Detector
from TargetProcessor import TargetProcessor as Processor
from Network import Network
from networktables import NetworkTables
import numpy as np
import cv2

rectActualWidth = 2.54 * 8
minThreshold = np.array([80, 35, 85], np.uint8)
maxThreshold = np.array([255, 255, 255], np.uint8)
lightblue = (255, 221, 0)                                                       # variable for the lightblue color
focalLength = 720                                                               # focal length of camera
degrees = u'\N{DEGREE SIGN}'                                                    # for degree sign usage
centimeters = " cm"
NetworkTables.initialize(server = "roboRIO-3341-FRC.local")
table = NetworkTables.getTable("cv")

leftCenter = 0
rightCenter = 0
center = 0
# method that prints out the values in a nice format
def displayValues():
    cv2.putText(frame, "Distance: " + str(proc.getDistance()/2.54) + centimeters, (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    cv2.putText(frame, "Azimuth: " + str(proc.getAzimuth()), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    cv2.putText(frame, "Altitude: " + str(proc.getAltitude()), (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    # for printing in terminal
    # print("\n"+"Distance = " + str(proc.getDistance())+centimeters)
    # print("Azimuth = " + str(proc.getAzimuth())+degrees)
    # print("Angle of Altitude = "+ str(proc.getAltitude())+degrees+"\n")

#------------------------------- FOR LIVE VIDEO -------------------------------#
cam = cv2.VideoCapture(1)

while(True):                                                                    # while loop for continuous analyzation of frames through video capture
    ret, frame = cam.read()
    if not ret:                                                                 # checks if boolean value ret is false
        continue
    h, w = frame.shape[:2]                                                       # gets the height and width of the frame for analyzation purposes
    imgXcenter = w/2
    imgYcenter = h/2
    det = Detector()                                                            # makes a new TargetDetector object
    proc = Processor()                                                          # makes a new TargetProcessor object

    threshold = det.threshold(minThreshold, maxThreshold, frame)                  # getting thresholded frame
    det.contours(threshold)                                                     # finding contours based on thresholded frame
    det.filterContours()                                                        # filtering the contours by size and number
    corners = det.getCorners()                                  # getting the array of corners
    
    if corners is not None:                                                   # checking if the corners array returned is not null
        target = Target(corners)                                                # making a new Target object
        imageWidth = target.getWidth()
        xMid, yMid = target.getCenter()
        cv2.line(frame, (xMid, yMid), (xMid, yMid), lightblue, 5)
        if det.leftRect is not None:
            leftCenter = (int)((det.leftRect[0][0][0] + det.leftRect[2][0][0])/2)
            cv2.line(frame, (det.leftRect[0][0][0], det.leftRect[0][0][1]), (det.leftRect[2][0][0], det.leftRect[2][0][1]), lightblue, 5)
        if det.rightRect is not None:
            rightCenter = (int)((det.rightRect[0][0][0] + det.rightRect[2][0][0])/2)
            cv2.line(frame, (det.rightRect[0][0][0], det.rightRect[0][0][1]), (det.rightRect[2][0][0], det.rightRect[2][0][1]), lightblue, 5)
        if leftCenter != 0 and rightCenter != 0:
            center = (leftCenter + rightCenter)/2
            #proc.calculate(focalLength,rectActualWidth,imageWidth,xMid-imgXcenter,imgYcenter-yMid)
            proc.calculate(focalLength, rectActualWidth, imageWidth, imgXcenter - center, imgYcenter - yMid)
            cv2.line(frame, ((int)(center), 0), ((int)(center), h), lightblue, 10)
            leftCenter = 0
            rightCenter = 0
            table.putValue('rectAzi', proc.getAzimuth())
        else:
            table.putValue('rectAzi', -100)

    displayValues()                                                             # method displays values in terminal
    cv2.imshow("frame", frame)
    cv2.imshow("threshold", threshold)
    cv2.moveWindow("frame", 0, 20)
    cv2.moveWindow("threshold", 650, 20)
    key = cv2.waitKey(10)

    if key == 27:
        cv2.destroyAllWindows()
        break
