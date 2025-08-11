import cv2
import pandas as pd
import sharedFunctions as sf
from laneMemory import laneMemory
import speed as sp

class noLaneState:
    #initalise lane state 
    def __init__(self, laneState):
        self.laneState = laneState
        self.presistentMemory = laneMemory(False, False,[],[])
        self.idx = 0
        self.speed = "S13\n"
    
    def assignPresistentMemory(self, newMem):
        self.presistentMemory = newMem

    #change state to two lane state when both lanes are able to be detected
    def changeStateTwoLane(self):
        print("State changed to two lanes")
        self.idx = 0
        self.laneState.state =  self.laneState.twolanestate

    #Chnge state to Correction state when only one lane is detected 
    def changeStateCorrection(self):
        print("State changed to correction state")
        self.idx = 0
        self.laneState.state = self.laneState.correctionstate

    def changeStateTurning(self):
        print("Now entering turning state")
        self.idx = 0
        self.laneState.state = self.laneState.turningstate

    def getState(self):
        return "No Lane State"
    
    def getSpeed(self):
        return self.speed
    
    #an unique proccess that continues to turn for a bit, but if it goes too long enter a search functionality

    # CONFIRM NO DETECTIONS 
    # CHECK BOTH SIDE CAMERAS
    # CHOOSE THE ONE WITH THE MOST DETECTIONS  
    # MOVE TOWARDS THAT (at a set speed) SIDE CAMERA UNTIL THE MAIN CAMERA CAN SEE A LANE
    # IF NOTHING DETECTED REPEAT ELSE CHANGE STATE 
    def proccess(self, frame, scale, model, df, midX, laneCenter, newMemory, cameras):
        if self.idx == 0: 
            #First entered state 
            print("ENTERED NO LANE STATE")
            self.assignPresistentMemory(laneMemory(False,False,[],[]))
            self.idx = 1
            self.assignPresistentMemory(newMemory)
        polygonList = sf.usingCSVData(df)
        margin = sf.marginOfError(scale, laneCenter, midX) #For if the centre of the lane is left or right favoured
        leftLane, rightLane = sf.splitLaneByImg(polygonList, margin, scale) #easiest way to split the list 
        newMemory = sf.doesLeftOrRightExist(leftLane, rightLane, scale, newMemory)

        if newMemory.leftExist == True and newMemory.rightExist == True: #two lane exit
            self.changeStateTwoLane() 
        elif newMemory.leftExist == True or newMemory.rightExist == True and not (newMemory.leftExist == True and newMemory.rightExist == True):
            newMemory = laneMemory(self.presistentMemory.leftExist, self.presistentMemory.rightExist, leftLane, rightLane)
            self.changeStateCorrection()
            self.idx = 0
        else:
            leftLane, rightLane = self.defineList(leftLane + rightLane)
            newMemory = laneMemory(self.presistentMemory.leftExist, self.presistentMemory.rightExist, leftLane, rightLane)
            self.idx = self.idx + 1
        laneCenter = sf.findLaneCenter(newMemory.leftLane, newMemory.rightLane, 900 * scale, midX, laneCenter)
        command = sp.calc_speed(newMemory.leftLane, newMemory.rightLane, scale)
        newFrame = sf.overlayimage(scale, newMemory.leftLane, newMemory.rightLane, laneCenter, frame) 
        rightFrame = cameras[1].returnFrame()  # one = right, 2 = left
        leftFrame = cameras[2].returnFrame()
        if (rightFrame is not None and leftFrame is not None) : #if it exists 
            rPL = sf.getPolygonList(rightFrame, model) 
            lPL = sf.getPolygonList(leftFrame, model)
            laneCenter = compareRightCamAndLeftCam(rPL, lPL, laneCenter, frame.shape[1])
            rightFrame = sf.overlaySideImage(rPL, rightFrame)
            leftFrame = sf.overlaySideImage(lPL, leftFrame)
            cv2.imshow("right_cam", rightFrame)
            cv2.imshow("left_cam", leftFrame)
        cv2.imshow("final", newFrame)
        return laneCenter, newMemory, command