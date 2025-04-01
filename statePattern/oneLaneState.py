import cv2
import pandas as pd
import sharedFunctions as sf
from laneMemory import laneMemory

class oneLaneState:
    #initalise lane state 
    def __init__(self, laneState):
        self.laneState = laneState
        self.presistentMemory = laneMemory(False, False,[],[])
        self.idx = 0
        # self.left = left #Left Lane exists: Boolean
        # self.right = right #Right Lane exists: Boolean
        # #Ideally one one should ever be true 
    
    def assignPresistentMemory(self, newMem):
        self.presistentMemory = newMem

    #change state to two lane state when both lanes are able to be detected
    def changeStateTwoLane(self):
        print("State changed to two lanes")
        self.idx = 0
        self.laneState.state =  self.laneState.twolanestate
    
    def changeStateCorrection(self):
        print("State changed to correction state")
        self.idx = 0
        self.laneState.state =  self.laneState.correctionstate
    def getState(self):
        return 1
    
    #an unique proccess that continues to turn for a bit, but if it goes too long enter a search functionality
    def proccess(self, frame, scale, model, df, midX, laneCenter, newMemory, cameras):
        if self.idx == 0: 
            #First entered state 
            self.idx = 1
            self.assignPresistentMemory(newMemory)
        polygonList = sf.usingCSVData(df)
        margin = sf.marginOfError(scale, laneCenter, midX) #For if the centre of the lane is left or right favoured
        leftLane, rightLane = sf.splitLaneByImg(polygonList, margin, scale) #easiest way to split the list 
        newMemory = sf.doesLeftOrRightExist(leftLane, rightLane, scale, newMemory)
        
        if newMemory.leftExist == True and newMemory.rightExist == True:
            self.changeStateTwoLane() 
        elif self.idx > 120:
            self.changeStateCorrection()
        else:
            leftLane, rightLane = self.defineList(leftLane + rightLane)
            print("LL: ", newMemory.leftExist, "RL: ", newMemory.rightExist)
            newMemory = laneMemory(self.presistentMemory.leftExist, self.presistentMemory.rightExist, leftLane, rightLane)

        laneCenter = sf.findLaneCenter(newMemory.leftLane, newMemory.rightLane, 1000 * scale, midX, laneCenter)
        newFrame = sf.overlayimage(scale, newMemory.leftLane, newMemory.rightLane, laneCenter, frame)
        self.idx = self.idx + 1
        cv2.imshow("final", newFrame)
        return laneCenter, newMemory

    
    def defineList(self, polygonList):
        leftLane = []
        rightLane = []
        if self.presistentMemory.leftExist == True:
            leftLane = polygonList
        elif self.presistentMemory.rightExist == True:
            rightLane = polygonList
        return leftLane, rightLane