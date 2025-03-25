import cv2
import pandas as pd
import sharedFunctions as sf

class twoLaneState:
    #Init State
    def __init__(self, laneState):
        self.laneState = laneState
        # self.left = left #Left Lane exists: Boolean
        # self.right = right #Right Lane exists: Boolean
        #BOTH SHOULD BE TRUE 

    #Change state when only one lane is being detected
    def changeState(self):
        print("State changed to one lane")
        self.laneState.state =  self.laneState.onelanestate
        
    def getState(self):
        return 2
    
    #Follows the original process 
    def proccess(self, frame, scale, df, midX, laneCenter, newMemory):
        polygonList = sf.usingCSVData(df)
        polygonList = sf.sortByDist(polygonList, scale) #Gets rid of outliers
        margin = sf.marginOfError(scale, laneCenter, midX) #For if the centre of the lane is left or right favoured
        leftLane, rightLane = sf.splitLaneByImg(polygonList, margin, scale) #easiest way to split the list 
        #leftLane, rightLane = self.betterSort(leftLane,rightLane)
        # rightLane, leftLane = self.betterSort(rightLane,leftLane)
        newMemory = sf.doesLeftOrRightExist(leftLane, rightLane, scale, newMemory)
        laneCenter = sf.findLaneCenter(newMemory.leftLane, newMemory.rightLane, 1000 * scale, midX, laneCenter)
        newFrame = sf.overlayimage(scale, newMemory.leftLane, newMemory.rightLane, laneCenter, frame)
        cv2.imshow("final", newFrame)
        if newMemory.leftExist == False or newMemory.rightExist == False:
            self.changeState()
        return laneCenter, newMemory
    
    def betterSort(self, leftLane, rightLane):
        #iterate through list and ensure correct placement 
        looping = True 
        
        idx = 0
        thisList = []
        
        totalList = (leftLane + rightLane)
        thisList.append(totalList[0])
        x = totalList[idx]
        while idx < len(totalList)  - 1: 
            idx = idx+ 1 
            y = totalList[idx] 
            if sf.getDist(x,y) < 40:
                thisList.append(y)
                if y in rightLane:
                    rightLane.remove(y)
                x = y
        return thisList, rightLane


