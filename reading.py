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
def writeToFile(snapString):
    #Call to write to a file  
    #unused 
    file = open("coords.txt", "w") 
    file.writelines(snapString)
    file.close() 

def getCord(min, max):
    #midpoint formulae 
    return (min + max)/2


def usingCSVData(dataFrame):
    #xCentre = [] 
    #yCentre = [] 
    polygonL = [] #list of coordinates, bad naming convention I know
    for index, row in dataFrame.iterrows():
        #row names ,xmin,ymin,xmax,ymax,confidence,class,name
        if(row["confidence"] >= 0.2 and row["class"] == 0):
            #Gets the midpoint of xmin and xmax, and ymin and ymax, appending it to the list polygonL as a list of coordinates
            xMid = getCord(row["xmin"], row["xmax"])
            yMid = getCord(row["ymin"], row["ymax"])
            polygonL.append((float(xMid), float(yMid)))
    return polygonL

def getSignData(dataFrame):
    polygonL = [] #list of coordinates
    for index, row in dataFrame.iterrows():
        #row names ,xmin,ymin,xmax,ymax,confidence,class,name
        if(row["confidence"] >= 0.2 and row["class"] != 0): #ebery single class except 
            #Gets the midpoint of xmin and xmax, and ymin and ymax, appending it to the list polygonL as a list of coordinates
            xMid = getCord(row["xmin"], row["xmax"])
            yMid = getCord(row["ymin"], row["ymax"])
            polygonL.append((float(xMid), float(yMid)))
    
    return polygonL

def overlayimage(scale, leftLane, rightLane, laneCenter, image):
    #takes list and turns it into polygon
    alpha = 0.5 #transparency for overlay
    #print(len(leftLane + rightLane))
    if(len(leftLane + rightLane) >= 4):
        #Enough Coordinates to make a polygon 
        
        leftLane.reverse()
        polygonTo = Polygon(rightLane + leftLane) #converts to a polygon, hence polygonTo (horrible naming convention i know)
        leftLane.reverse()
        #FOLLOWING CODE USES:
        #https://stackoverflow.com/questions/13574751/overlay-polygon-on-top-of-image-in-python 
        int_coords = lambda x: np.array(x).round().astype(np.int32)
        exterior = [int_coords(polygonTo.exterior.coords)]
        overlay = image.copy()
        cv2.fillPoly(overlay, exterior, color=(150, 255, 0)) #RGB - fills polygon with the colour
        #CODE DUPLICATION BELOW
        if len(leftLane) >= 1:
            i = 0
            for line in leftLane:
                if i == 0:
                    i =+ 1
                    x0, y0 = line
                else: 
                    x2, y2 = line 
                    cv2.line(overlay, ((int)(x0), (int)(y0)), ((int)(x2), (int)(y2)), (255, 0, 0), 10) #draws lines 
                    i =+ 1
                    x0 = x2
                    y0 = y2
                
        if len(rightLane) >= 1:
            i = 0
            for line in rightLane:
                if i == 0:
                    i =+ 1
                else: 
                    x2, y2 = line 
                    cv2.line(overlay, ((int)(x0), (int)(y0)), ((int)(x2), (int)(y2)), (0, 0, 255), 10) #draws lines 
                    i =+ 1
                x0, y0 = line
        y = (int)(400*scale)
        cv2.circle(overlay, ((int)(laneCenter), (y)), 10, (125, 125, 0), -1)
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image) #overlaays the image with the polygon
    # overlay = image.copy()
    # y = (int)(400*scale)
    # cv2.circle(overlay, ((int)(laneCenter), (y)), 10, (125, 125, 0), -1)
    # cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image) #overlaays the image with the polygon
    return image

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

def calcScale(num):
    #calculates scale using midx 960
    scaled = (num / 960) 
    return scaled
def minimum(matrix):
    #return the minimum sized number in a array
    min = 9999999999999999 # +ve infinity 
    for array in matrix:
        for x in array:
            if (x < min):
                min = x
    return min 

def sortByDistance(array):
    thisList = []
    idx = 0 
    if len(array) <= 1 :
        return []
    
    thisList.append(array[0])
    x = array[idx]
    while idx < len(array)  - 1: 
        idx = idx+ 1 
        y = array[idx] 
        i, j = y
        if getDist(x,y) < 200:
            thisList.append(y)
            x = y
    #DEBUG print(thisList)
    return thisList

            
        
def doesLeftOrRightExist(leftLane, rightLane, scale, oldMemory):
    #use lane gradients to determine if a lane exists
    #helps for defining centre and turns
    #Left lane = -ve gradient
    #Right Lane = +ve gradient

    ###############################################
    # Cur working ver: 4/03/2025
    # Author Rafael Skellett
    # Instead of taking the end of one list and comparing it with the start of another
    # We now take the average x coordinate of each list and check if it's less than a 
    # lane's length from each other 
    # Returns: newMemory (laneMemory)
    #       
    ################################################
    dist = 0
    leftExist = False
    rightExist = False 
    #Validating that left and right lanes exist and are correctly defined
    # leftCopy = leftLane.copy()
    # rightCopy = rightLane.copy()
    # leftLane = sortByDistance(leftCopy + rightCopy)
    # rightLane = sortByDistance(rightCopy + leftCopy)
    if len(leftLane) > 1:
        gradLeft = lineOfBest(leftLane)
    else: 
        gradLeft = 0
    if len(rightLane) > 1: 
        gradRight = lineOfBest(rightLane)
    else:
        gradRight = 0
    if gradLeft < 0: #-ve
        leftExist = True
    if gradRight > 0: #+ve
        rightExist = True
    
    if len(leftLane) >= 1 and len(rightLane) >= 1: #if 0 then line of best calculation will crash when no lines are detected
        #check distance using cdist
        matrix = distance.cdist(leftLane, rightLane, metric='euclidean')
        min = minimum(matrix) 
        #we check distance to ensure that the lanes are apporiately separated 
        #this distance checking grabs the minimum distance between all points of both lanes
        #it works but if there are many many points in the definition it will run gradually slower as it needs to sort through
        #what is effectively a 2d array
        #if (min < 390 * scale):
        # FIXME: FIXME: FIXME: 
        if oldMemory.leftExist == True and oldMemory.rightExist == False and 0 > lineOfBest(leftLane + rightLane): #turning right 
            leftExist = True
            rightExist = False
            leftLane.extend(rightLane)
            rightLane.clear() 
        elif oldMemory.rightExist == True and oldMemory.leftExist == False and 0 < lineOfBest(leftLane + rightLane): #turning left
            rightExist = True
            leftExist = False
            rightLane.extend(leftLane)
            leftLane.clear() 
                    
    newMemory = laneMemory(leftExist, rightExist, leftLane, rightLane)
    #DEBUG print("LE ", leftExist, "\nRE ", rightExist, "\nLL: ", leftLane, "\nRR: ",rightLane, "\ndist ", dist, "\ngradLeft ", gradLeft, "\ngradRight ", gradRight)
    return newMemory


def sortByDist(givenList,scale):
    #SORTS OUT THE POINTS TO DISCARD OF OUTLIERS 
    #CORDS IN (X, Y) FORMAT
    #using https://codereview.stackexchange.com/questions/224704/grouping-sorted-coordinates-based-on-proximity-to-each-other
    groupList = []
    while givenList: #not empty
        farPoints = []
        ref = givenList.pop()
        groupList.append(ref)
        for point in givenList:
            d = getDist(ref, point)
            if d < (300*scale): #change distance param here 
                #more specifically this says if the point is less than 70 pixels from the last point the append it to the list 
                groupList.append(point)
            else: 
                farPoints.append(point)
        givenList = farPoints

    return groupList

def splitLaneByImg(coordList, midX, scale):
    leftLane = []
    rightLane = []
    #DEBUGGING STUFF
    #print("Overall gradient: ", lineOfBest(coordList))
    for point in coordList:
        x, y = point 
        if x < midX and y > (900*scale): #TOP LEFT IS 0,0 and bottm rught is +ve, +ve
            leftLane.append(point)
        elif x >= midX and y > (900*scale) : #300 when using https/webcam --- 500 with video
            rightLane.append(point)
    return leftLane, rightLane

def getDist(ref, point):
    #using https://codereview.stackexchange.com/questions/224704/grouping-sorted-coordinates-based-on-proximity-to-each-other
    x1, y1 = ref
    x2, y2 = point
    return math.hypot(x2 - x1, y2 - y1)   #H^2 = A^2 + B^2
       

def lineOfBest(coordList):
    #finds the line of best fit and returns it 
    xList = []
    yList = []
    for line in coordList:
        x0, y0 = line
        xList.append(x0)
        yList.append(y0)
    x = np.array(xList)
    y = np.array(yList)
    #find line of best fit

    a, b = np.polyfit(x, y, 1)
    #add points to plot
    plt.scatter(x, y)
    #add line of best fit to plot
    plt.plot(x, a*x+b)
    return a 

def convertToXList(list):
    xList = []
    if(len(list) > 0):
        for line in list:
            x, y = line 
            xList.append(x)
    return xList

def findLaneCenter(leftLane, rightLane, laneWidth, midX, leftExist, rightExist, lastLaneCenter):
    #Justin's code adapted
    #finds lane center 
    laneCenter = midX

    #need to conver right lane and left lane to JUST x coordinates
    if rightLane:
        medianRightX = np.mean(convertToXList(rightLane))
    if leftLane:
        medianLeftX = np.mean(convertToXList(leftLane))

    if leftLane and rightLane:
        laneCenter = (medianRightX + medianLeftX)/2
    elif rightLane:
        laneCenter = medianRightX - (laneWidth/2)
    elif leftLane:
        laneCenter = medianLeftX + (laneWidth/2)
    else:
        laneCenter = lastLaneCenter
    return laneCenter

def marginOfError(scale, laneCenter, midX):
    if laneCenter > midX:
        margin = midX + (scale * 100)
    elif laneCenter < midX:
        margin = midX - (scale * 100)
    else:
        margin = midX
    return margin


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
    polygonList = usingCSVData(df)
    polygonList = sortByDist(polygonList, scale) #Gets rid of outliers
    margin = marginOfError(scale, laneCenter, midX) #For if the centre of the lane is left or right favoured
    leftLane, rightLane = splitLaneByImg(polygonList, margin, scale) #easiest way to split the list 
    # leftLane = sortByDistance(leftLane)
    # rightLane = sortByDistance(rightLane)
    #leftLane, rightLane = sortByDistance(polygonList)
    newMemory = doesLeftOrRightExist(leftLane, rightLane, scale, newMemory)
    #print("Left: ", leftExist, "  ", leftLane, "\nRight: ", rightExist, "  ", rightLane)
    laneCenter = findLaneCenter(newMemory.leftLane, newMemory.rightLane, 1000 * scale, midX, newMemory.leftExist, newMemory.rightExist, laneCenter)
    #print(laneCenter)
    newFrame = overlayimage(scale, newMemory.leftLane, newMemory.rightLane, laneCenter, frame)
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
                scale = calcScale(midX)
                newMemory = laneMemory(False, False, [], [])
                detections = 0
            if not ret:
                break
            ### ###
            oldMemory = newMemory
            detections += 1 #used for lane weighting 
            laneCenter, newMemory = laneState.proccess(frame, scale, model, midX, laneCenter, newMemory)
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
