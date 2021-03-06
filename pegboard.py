import numpy as np
import cv2
import math
import sounddevice as sd
import soundfile as sf
import os

threshold = 185
fail, _ = sf.read(os.path.join('audio','almost_there.wav'))
# Detect and store the coordinates of all the black rectangles
#   Input: initImg, grayscale image
#   Output: List of rectangle coordinates of the pegboard hole positions
def initPegboard(initImg):

    kernel = np.ones((5, 5), np.float32) / 25
    initImg = cv2.filter2D(initImg, -1, kernel)

    myList = []

    # Everything higher than the threshold is set to white
    ret, thresh = cv2.threshold(initImg, threshold, 255, 0)
    _, contours0, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.imshow('image', thresh)
    cv2.waitKey()
    # Min and Max area for the rectangles
    minArea = 200.0
    maxArea = 600.0

    for i in range(len(contours0)): #range(6):
        area = cv2.contourArea(contours0[i])
        tempMat = initImg.copy()
        if (area > minArea) & (area < maxArea):
            print(area)
            cv2.drawContours(tempMat, contours0, i, color=255, thickness=-1)

            # Access the image pixels and create a 1D numpy array then add to list
            pts = np.where(tempMat == 255)
            tempMat = initImg.copy()

            myList.append(pts)

    # cv2.imshow('image', initImg)
    return myList

# Check if a rectangle is occupied by a peg
#   Input: initImg, initial image of the board
#   Input: rect, list containing pixels of the rectangle to consider
#   Input: currImg, current image to check for
#   Output: List of rectangle coordinates of the pegboard hole positions
def checkRectOccupancy(initImg, currImg, rect):

    ret, thresh = cv2.threshold(initImg, threshold, 255, 0)
    ret, thresh2 = cv2.threshold(currImg, threshold, 255, 0)
    diffMat = thresh[rect].astype(np.double) - thresh2[rect].astype(np.double)
    return np.sum(np.abs(diffMat))/(len(diffMat)*255.0)

# Asses the routine
def assessRoutine(initImg, currImg, rectList):
    score = np.zeros((len(rectList),1))
    for i in range(len(rectList)):
        score[i]=checkRectOccupancy(initImg, currImg, rectList[i])
        if score[i] < 0.2:
            # sd.play(fail, 16000, blocking=True)
            break

    return score
