import cv2
import pandas as pd
from statePattern.sharedFunctions import * 

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
        polygonList = usingCSVData(df)
        polygonList = sortByDist(polygonList, scale) #Gets rid of outliers
        margin = marginOfError(scale, laneCenter, midX) #For if the centre of the lane is left or right favoured
        leftLane, rightLane = splitLaneByImg(polygonList, margin, scale) #easiest way to split the list 
        newMemory = doesLeftOrRightExist(leftLane, rightLane, scale, newMemory)
        laneCenter = findLaneCenter(newMemory.leftLane, newMemory.rightLane, 1000 * scale, midX, laneCenter)
        newFrame = overlayimage(scale, newMemory.leftLane, newMemory.rightLane, laneCenter, frame)
        cv2.imshow("final", newFrame)
        if newMemory.leftExist == False or newMemory.rightExist == False:
            self.changeState()
        return laneCenter, newMemory