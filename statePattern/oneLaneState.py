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
        #self.assignPresistentMemory(laneMemory(False,False,[],[]))
        self.laneState.state =  self.laneState.twolanestate
    
    def changeStateCorrection(self):
        print("State changed to correction state")
        self.idx = 0
        #self.assignPresistentMemory(laneMemory(False,False,[],[]))
        self.laneState.state = self.laneState.correctionstate


    def getState(self):
        return 1
    
    #an unique proccess that continues to turn for a bit, but if it goes too long enter a search functionality
    def proccess(self, frame, scale, model, df, midX, laneCenter, newMemory, cameras):
        
        if self.idx == 0: 
            #First entered state 
            print("ENTERED ONE LANE REASSIGNMENT")
            self.assignPresistentMemory(laneMemory(False,False,[],[]))
            self.idx = 1
            self.assignPresistentMemory(newMemory)
        polygonList = sf.usingCSVData(df)
        margin = sf.marginOfError(scale, laneCenter, midX) #For if the centre of the lane is left or right favoured
        leftLane, rightLane = sf.splitLaneByImg(polygonList, margin, scale) #easiest way to split the list 
        newMemory = sf.doesLeftOrRightExist(leftLane, rightLane, scale, newMemory)
        
        if newMemory.leftExist == True and newMemory.rightExist == True: #two lane exit
            self.changeStateTwoLane() 
        elif self.idx > (15) and (laneCenter >= 3*frame.shape[1]/8 and laneCenter <= 5*frame.shape[1]/8): #switches over after 15 detections and if the laneCenter is defined in the center of the screen 
            #makes sure Correction state is correctly defined 
            leftLane, rightLane = self.defineList(leftLane + rightLane)
            #print("LL: ", newMemory.leftExist, "RL: ", newMemory.rightExist)
            newMemory = laneMemory(self.presistentMemory.leftExist, self.presistentMemory.rightExist, leftLane, rightLane)
            self.changeStateCorrection()
            #print("lah", newMemory.leftExist, "bah ", newMemory.rightExist )
            self.idx = 0
        else:
            leftLane, rightLane = self.defineList(leftLane + rightLane)
            #print("LL: ", newMemory.leftExist, leftLane, "RL: ", newMemory.rightExist, rightLane)
            newMemory = laneMemory(self.presistentMemory.leftExist, self.presistentMemory.rightExist, leftLane, rightLane)
            self.idx = self.idx + 1
        laneCenter = sf.findLaneCenter(newMemory.leftLane, newMemory.rightLane, 1000 * scale, midX, laneCenter)
        newFrame = sf.overlayimage(scale, newMemory.leftLane, newMemory.rightLane, laneCenter, frame)
        
        rightFrame = cameras[1].returnFrame()  # one = right, 2 = left
        leftFrame = cameras[2].returnFrame()
        if (rightFrame is not None and leftFrame is not None) : #if it exists 
            rPL = sf.getPolygonList(rightFrame, model) 
            lPL = sf.getPolygonList(leftFrame, model)
           

            cv2.imshow("right_cam", rightFrame)
            cv2.imshow("right_cam", leftFrame)
       
        cv2.imshow("final", newFrame)
        print("OLS INDEX ", self.idx, "PRESISTANT ", self.presistentMemory.leftExist, " ", self.presistentMemory.rightExist)
        return laneCenter, newMemory

    
    def defineList(self, polygonList):
        leftLane = []
        rightLane = []
        if self.presistentMemory.leftExist == True:
            leftLane = polygonList
        elif self.presistentMemory.rightExist == True:
            rightLane = polygonList
        return leftLane, rightLane


def compareRightCamAndLeftCam(rPL, lPL, lc):
    # compares the polygon list of both right and left cameras, and uses it to judge where the CAV is in relation to the road   
    # adds/removes 30 pixels to the lane center in order to help rebalance 
    # rPL = right Polygon List
    # lPL = left Polygon List 
    # lc  = lane Center 
    # IF X AVG OF rPL ~= lPl (moe of 99) then we are in the centre of the frame 
    pass 