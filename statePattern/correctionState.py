import cv2
import pandas as pd
from statePattern.sharedFunctions import * 

#Enters in after a time limit in oneLaneState
#the aim is to reposition the CAV into seeing two lanes 

class correctionState:
    #initalise lane state 
    def __init__(self, laneState):
        self.laneState = laneState
        self.presistentMemory = laneMemory(False, False,[],[])
        self.idx = 0
        # self.left = left #Left Lane exists: Boolean
        # self.right = right #Right Lane exists: Boolean
        # #Ideally one one should ever be true 