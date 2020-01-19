# required imports
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import screeninfo
import threading
import winsound
import pygame
# setting a kick drum beat in the background using winsound
class soun(threading.Thread):
    def run(self):
        self.keeprunning = True
        while self.keeprunning:
            winsound.PlaySound('Kick Drum.wav', winsound.SND_FILENAME|winsound.SND_NOWAIT)
a=soun()
a.start()
pygame.init()  # initializing pygame for playing audio
# importing audio files
rightDrum = pygame.mixer.Sound("sou.ogg")
tom1=pygame.mixer.Sound("tom1 final.ogg")
tom2=pygame.mixer.Sound("tom2 final.ogg")
cymbals=pygame.mixer.Sound("cymbals final.ogg")
hiHat=pygame.mixer.Sound("hi hat final.ogg")
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the green and pink drum stick heads, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
pinkLower = (100, 100, 125)
pinkUpper = (170, 255, 255)
pts1 = deque(maxlen=args["buffer"])
pts2 = deque(maxlen=args["buffer"])

# starting webcam video capture
vs = VideoStream(src=0).start()

# allow the camera or video file to warm up
time.sleep(2.0)

# keep looping as long as program is running
while True:
    # grab the current frame
    frame = vs.read()
    # resize the frame, blur it, and convert it to the HSV color space
    screen = screeninfo.get_monitors()[0]
    width, height = screen.width, screen.height
    frame = imutils.resize(frame, height=900, width=1440)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    frame = cv2.flip(frame, 1)  # flipping to have foreground and background in the right orientation
    # importing foreground image (drums)
    foreground = cv2.imread('final_drums_bgimg.png')
    window_name = 'Air Drums'
    overlay = cv2.addWeighted(frame[:900, :1440], 0.4, foreground[:, :], 0.6, 0)
    frame[:900, :1440] = overlay
    frame = frame[:900, :1440]
    frame = cv2.flip(frame, 1)  # flipping back so tracking appears correct

    

    # construct a mask for the color "green" and "pink", then perform a series of dilations and erosions to
    # remove any small blobs left in the mask
    mask1 = cv2.inRange(hsv, greenLower, greenUpper)
    mask1 = cv2.erode(mask1, None, iterations=2)
    mask1 = cv2.dilate(mask1, None, iterations=2)
    mask2 = cv2.inRange(hsv, pinkLower, pinkUpper)
    mask2 = cv2.erode(mask2, None, iterations=2)
    mask2 = cv2.dilate(mask2, None, iterations=2)

    # find contours in the mask and initialize the current (x, y) center of each of the drum stick head
    cnts1 = cv2.findContours(mask1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts1 = imutils.grab_contours(cnts1)
    center1 = None
    cnts2 = cv2.findContours(mask2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts2 = imutils.grab_contours(cnts2)
    center2 = None

    # only proceed if at least one contour was found
    if len(cnts1) > 0:
        # find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
        c = max(cnts1, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center1 = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size (prevents small background interference)
        if radius > 10:
            # draw the circle and centroid on the frame, then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center1, 5, (0, 0, 255), -1)

    # update the points queue
    pts1.appendleft(center1)

    # loop over the set of tracked points
    for i in range(1, len(pts1)//20):
        # if either of the tracked points are None, ignore them
        if pts1[i - 1] is None or pts1[i] is None:
            continue

        # otherwise, compute the thickness of the line and draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)))
        
        # plays the required sounds when the drum stick heads enter specific regions shown by the drum image
        if 70<x<270 and 720<y<875 :  # these numbers have been found by trial and error
            cv2.line(frame, pts1[i - 1], pts1[i], (255, 255, 0), thickness)
            pygame.mixer.Sound.play(cymbals)
            pygame.mixer.music.stop()
           
        elif 275<x<560 and 520<y<720:
            cv2.line(frame, pts1[i - 1], pts1[i], (255, 0, 255), thickness)
            pygame.mixer.Sound.play(tom1)
            pygame.mixer.music.stop()
            
        elif 600<x<875 and 520<y<700:
            cv2.line(frame, pts1[i - 1], pts1[i], (0, 255, 255), thickness)
            pygame.mixer.Sound.play(tom2)
            pygame.mixer.music.stop()
           
        elif 880<x<1110 and 700<y<865:
            cv2.line(frame, pts1[i - 1], pts1[i], (0, 255, 0), thickness)
            pygame.mixer.Sound.play(rightDrum)
            pygame.mixer.music.stop()            
        elif 1010<x<1410 and 300<y<525:
            cv2.line(frame, pts1[i - 1], pts1[i], (255, 255, 255), thickness)
            pygame.mixer.Sound.play(hiHat)
            pygame.mixer.music.stop()
           
        else:
            cv2.line(frame, pts1[i - 1], pts1[i], (0, 0, 255), thickness)
           

        
    if len(cnts2) > 0:
        # find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
        c2 = max(cnts2, key=cv2.contourArea)
        ((x2, y2), radius2) = cv2.minEnclosingCircle(c2)
        M2 = cv2.moments(c2)
        center2 = (int(M2["m10"] / M2["m00"]), int(M2["m01"] / M2["m00"]))

        # only proceed if the radius meets a minimum size
        # same logic as above, but this time for the pink drum stick head
        if radius2 > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x2), int(y2)), int(radius2), (0, 255, 255), 2)
            cv2.circle(frame, center2, 5, (0, 0, 255), -1)

    # update the points queue
    pts2.appendleft(center2)

    # loop over the set of tracked points
    for i in range(1, len(pts2)//20):
        # if either of the tracked points are None, ignore
        # them
        if pts2[i - 1] is None or pts2[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)))
        if 70<x2<270 and 720<y2<875 :
            cv2.line(frame, pts2[i - 1], pts2[i], (255, 255, 0), thickness)
            pygame.mixer.Sound.play(cymbals)
            pygame.mixer.music.stop()
            
        elif 275<x2<560 and 520<y2<720:
            cv2.line(frame, pts2[i - 1], pts2[i], (255, 0, 255), thickness)
            pygame.mixer.Sound.play(tom1)
            pygame.mixer.music.stop()
        elif 600<x2<875 and 520<y2<700:
            cv2.line(frame, pts2[i - 1], pts2[i], (0, 255, 255), thickness)
            pygame.mixer.Sound.play(tom2)
            pygame.mixer.music.stop()
            
        elif 880<x2<1110 and 700<y2<865:
            cv2.line(frame, pts2[i - 1], pts2[i], (0, 255, 0), thickness)
            pygame.mixer.Sound.play(rightDrum)
            pygame.mixer.music.stop()
           
        elif 1010<x2<1410 and 300<y2<525:
            cv2.line(frame, pts2[i - 1], pts2[i], (255, 255, 255), thickness)
            pygame.mixer.Sound.play(hiHat)
            pygame.mixer.music.stop()
            
        else:
            cv2.line(frame, pts2[i - 1], pts2[i], (0, 0, 255), thickness)
            
    # show the frame to our screen
    frame = cv2.flip(frame, 1)  # flipping it again so it appears mirrored to the user's actions
    cv2.imshow(window_name, frame)  # showing the frame of this loop iteration
    key = cv2.waitKey(1) & 0xFF  # waits for key input or moves on to the next frame in a microsecond

    # if the 'q' or 'esc' key is pressed, stop the loop
    if key == ord("q") or key == 27:  #instantly stops the program in the frame it was pressed
        break

vs.stop()  # stopping video capture once the loop has ended
a.keeprunning=False  # stops the kick drum beat in the background
cv2.destroyAllWindows()  # close all open windows, ending the program
