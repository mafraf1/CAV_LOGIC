import cv2
import pandas as pd
from statePattern.sharedFunctions import * 

class oneLaneState:
    #initalise lane state 
    def __init__(self, laneState):
        self.laneState = laneState
        # self.left = left #Left Lane exists: Boolean
        # self.right = right #Right Lane exists: Boolean
        # #Ideally one one should ever be true 
        
    #change state to two lane state when both lanes are able to be detected
    def changeState(self):
        print("State changed to two lanes")
        self.laneState.state =  self.laneState.twolanestate
    
    def getState(self):
        return 1
    
    #an unique proccess that continues to turn for a bit, but if it goes too long enter a search functionality
    def proccess(self, frame, scale, df, midX, laneCenter, newMemory):
        polygonList = usingCSVData(df)
        cv2.imshow("final", frame)
        if newMemory.leftExist == True and newMemory.rightExist == True:
            self.changeState()
        return laneCenter, newMemory

    