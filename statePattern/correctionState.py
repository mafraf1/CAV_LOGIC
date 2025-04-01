import cv2
import pandas as pd
import sharedFunctions as sf
from laneMemory import laneMemory
import torch
from cameraWidget import * 
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

    def assignPresistentMemory(self, newMem):
        self.presistentMemory = newMem

    #change state to two lane state when both lanes are able to be detected
    def changeStateTwoLane(self):
        print("State changed to two lanes")
        self.idx = 0
        self.laneState.state =  self.laneState.twolanestate
    
    def getState(self):
        return 3
    
    #an unique proccess that continues to turn for a bit, but if it goes too long enter a search functionality
    def proccess(self, frame, scale, model, df, midX, laneCenter, newMemory, cameras):
        if self.idx == 0: 
            #First entered state 
            self.assignPresistentMemory(newMemory)
            if self.presistentMemory.leftExist == True: 
                camera_stream = cameras[2] #right 
                otherStream = cameras[1]
                print("Assigned Right")
            else: 
                camera_stream = cameras[1] #left
                otherStream = cameras[2]
                print("Assigned Lefts")
            self.idx = 1
             
        
        #CHECK MAIN CAMERA
        #OTHERWISE CHECK OTHER CAMERA
        polygonList = sf.usingCSVData(df)
        margin = sf.marginOfError(scale, laneCenter, midX) #For if the centre of the lane is left or right favoured
        leftLane, rightLane = sf.splitLaneByImg(polygonList, margin, scale) #easiest way to split the list 
        newMemory = sf.doesLeftOrRightExist(leftLane, rightLane, scale, newMemory)
        #Check main camera 
        
        if newMemory.leftExist == True and newMemory.rightExist == True:
            self.changeStateTwoLane() 
            laneCenter = sf.findLaneCenter(newMemory.leftLane, newMemory.rightLane, 1000 * scale, midX, laneCenter)
            
        else:
            if camera_stream is None: 
                pass
            else: 
                nFrame = camera_stream.returnFrame() 
                # if nFrame: #if it exists 
                rFrame = cv2.cvtColor(nFrame, cv2.COLOR_BGR2RGB)

                results = model(nFrame)
                df2 = pd.DataFrame(results.pandas().xyxy[0].sort_values("ymin")) #df = Data Frame, sorts x values left to right (not a perfect solution)
                df2 = df2.reset_index() # make sure indexes pair with number of rows
                df2.iterrows()
                polygonList2 = sf.usingCSVData(df2)
                newMemory = laneMemory(self.presistentMemory.leftExist, self.presistentMemory.rightExist, leftLane, rightLane)
                if len(polygonList2) > 4: #gross simplification
                    laneCenter = frame.shape[1]/4
                else:
                    laneCenter = 3*frame.shape[1]/4
                cv2.imshow("side_cam", rFrame)
    
        newFrame = sf.overlayimage(scale, newMemory.leftLane, newMemory.rightLane, laneCenter, frame)
        
        cv2.imshow("final", newFrame)
        return laneCenter, newMemory
    
def openSideStream(camera_stream):
    #opens the side camera stream as needed 
    print("opening side camera")
    capture = cv2.VideoCapture(camera_stream, cv2.CAP_GSTREAMER)
    #raise error 
    if not capture.isOpened():
        raise ValueError(f"Failed to open camera stream: {camera_stream}")
    return capture

  