#Reads a source (has to be manually defined (a possible optimisation/QoL)) passes it through YoloV5, pulls the data from YoloV5 to be used elsewhere
#Left lane = -ve gradient
#Right Lane = +ve gradient
# 0,0 top left
import torch
import cv2
import pandas as pd
import numpy as np
#import matplotlib
#matplotlib.use("QtAgg")
from matplotlib import pyplot as plt
from shapely.geometry import Polygon
#import geopandas as gpd
#from adaption import *
#from laneFitting import *
import math
from laneMemory import laneMemory
from lanes import *
from scipy.spatial import distance
from statePattern import laneController as lc
from statePattern import sharedFunctions as sf
def writeToFile(snapString):
    #Call to write to a file  
    #unused 
    file = open("coords.txt", "w") 
    file.writelines(snapString)
    file.close() 

def getSignData(dataFrame):
    polygonL = [] #list of coordinates
    for index, row in dataFrame.iterrows():
        #row names ,xmin,ymin,xmax,ymax,confidence,class,name
        if(row["confidence"] >= 0.2 and row["class"] != 0): #ebery single class except 
            #Gets the midpoint of xmin and xmax, and ymin and ymax, appending it to the list polygonL as a list of coordinates
            xMid = sf.getCord(row["xmin"], row["xmax"])
            yMid = sf.getCord(row["ymin"], row["ymax"])
            polygonL.append((float(xMid), float(yMid)))
    
    return polygonL


def signDetails(image, list):
    alpha = 0.5 
    overlay = image.copy()
    #DEBUG print(list)
    for element in list: 
        #DEBUG print(element)
        x,y,z = element
        cv2.circle(overlay, (x,y), 10, (0, 125, 125), -1)
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image) #overlaays the image with the polygon
    return image


def openStream(name):
    #open the stream and return it
    print("writing")
    model_name='/home/raf/local/cuda/bin/lb2OO07.pt'
    #load model
    model = torch.hub.load('/home/raf/local/cuda/bin/yolov5', 'custom', source='local', path = model_name, force_reload = True)
    firstFrame = True
    #Opening with openCV
    capture = cv2.VideoCapture(name)
    return capture, model 

def proccess(frame, scale, model, midX, laneCenter, newMemory, displayName): 
    #frame = frame[(int)(2*frame.shape[0]/5): frame.shape[0], 0:frame.shape[1]] #y, x
    rFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model(rFrame)
    #DEBUG results.print() 

    df = pd.DataFrame(results.pandas().xyxy[0].sort_values("ymin")) #df = Data Frame, sorts x values left to right (not a perfect solution)
    df = df.reset_index() # make sure indexes pair with number of rows
    df.iterrows()
    polygonList = sf.usingCSVData(df)
    polygonList = sf.sortByDist(polygonList, scale) #Gets rid of outliers
    margin = sf.marginOfError(scale, laneCenter, midX) #For if the centre of the lane is left or right favoured
    leftLane, rightLane = sf.splitLaneByImg(polygonList, margin, scale) #easiest way to split the list 
    # leftLane = sortByDistance(leftLane)
    # rightLane = sortByDistance(rightLane)
    #leftLane, rightLane = sortByDistance(polygonList)
    newMemory = sf.doesLeftOrRightExist(leftLane, rightLane, scale, newMemory)
    #print("Left: ", leftExist, "  ", leftLane, "\nRight: ", rightExist, "  ", rightLane)
    laneCenter = sf.findLaneCenter(newMemory.leftLane, newMemory.rightLane, 1000 * scale, midX, newMemory.leftExist, newMemory.rightExist, laneCenter)
    #print(laneCenter)
    newFrame = sf.overlayimage(scale, newMemory.leftLane, newMemory.rightLane, laneCenter, frame)
    cv2.imshow(displayName, newFrame)
    return laneCenter, newMemory

def signDetect(frame, model):
    rFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = model(rFrame)
    #DEBUG results.print() 
    df = pd.DataFrame(results.pandas().xyxy[0].sort_values("ymin")) #df = Data Frame, sorts x values left to right (not a perfect solution)
    df = df.reset_index() # make sure indexes pair with number of rows
    df.iterrows()
    polygonList = getSignData(df)
    if len(polygonList) >0 : #not empty
        frame = signDetails(polygonList, frame)
    cv2.imshow("Signs", frame)
    
def convertBird(frame):
    #take a region of an image and convert it to birdseye view
    #CREDIT: Nikolasent -- Bird's Eye View Transfromation 
    #https://nikolasent.github.io/opencv/2017/05/07/Bird's-Eye-View-Transformation.html
    if frame.all() == None: #guard condition
        return 
    
    imageH = frame.shape[0]
    imageW = frame.shape[1]
    #DEBUG print("imageH ", imageH)
    #ISSUE WITH DETECTION IS HERE 
    src = np.float32([[0, imageH], [(1207/1080) * imageH, imageH], [0,0], [imageW, 0]]) # source image
    dst = np.float32([[(469/1080) * imageH, imageH], [(1207/1080) * imageH, imageH], [0,0], [imageW, 0]]) # roi
    M = cv2.getPerspectiveTransform(src,dst) #transformation matrix
    Minv = cv2.getPerspectiveTransform(dst, src) #inverse transformation
    #SLICE THAT IMAGE 
    img = frame[(int)(450/1080*imageH):((int)(450/1080*imageH)+imageH), 0:imageW] # apply np slicing for ROI crop
    warpedImg = cv2.warpPerspective(img, M,(imageW,imageH)) #image warping
    nwIm = warpedImg #cv2.cvtColor(warpedImg, cv2.COLOR)
    # cv2.imshow("BE",nwIm)
    return nwIm
  
def processEachFrame():
    #BREAKING DOWN writeToCSV()
    capture, model = openStream("/home/raf/local/cuda/bin/vivs/vid.webm")
    firstFrame = True 
    frame_count = 0
    leftLane = []
    rightLane = []
    laneState = lc.laneController() 
    #Processing each frame
    try:
        while capture.grab():
            ret, frame = capture.retrieve()
            if firstFrame:
                midX = int((frame.shape[1])/2)
                firstFrame = False
                laneCenter = midX
                scale = sf.calcScale(midX)
                newMemory = laneMemory(False, False, [], [])
                detections = 0
            if not ret:
                break
            ### ###
            oldMemory = newMemory
            detections += 1 #used for lane weighting 
            rFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model(rFrame)
            df = pd.DataFrame(results.pandas().xyxy[0].sort_values("ymin")) #df = Data Frame, sorts x values left to right (not a perfect solution)
            df = df.reset_index() # make sure indexes pair with number of rows
            df.iterrows()
            laneCenter, newMemory = laneState.proccess(frame, scale, df, midX, laneCenter, newMemory)
            #signDetect(frame,model)
            #imCopy = frame.copy()
            #proccess(imCopy, scale, model, midX, laneCenter, newMemory, "test")
            #frame = convertBird(frame)
            # laneCenter, newMemory = proccess(frame, scale, model, midX, laneCenter, newMemory, "final")
            # print("Current State: ", laneState.getState()) 
            # #LOGIC TO HANDLE STATE CHANGES 
            # if laneState.getState() == 1:
            #     if newMemory.leftExist == True and newMemory.rightExist == True:
            #         laneState.changeState()
            # elif laneState.getState() == 2: 
            #     if newMemory.leftExist == False or newMemory.rightExist == False:
            #         laneState.changeState()
            # else: 
            #     pass #do nothing, error handling 
        
            if cv2.waitKey(1) == ord('q'):#diplays the image for a set amount of time 
                break
            frame_count += 1
            if(detections >= 3): 
                    newMemory = laneMemory(oldMemory.leftExist, oldMemory.rightExist, [], [])
                    detections = 0
            ### ### ### ### ### ### ### ### ###
    except KeyboardInterrupt:
        pass
    #Close
    capture.release()
    cv2.destroyAllWindows()
