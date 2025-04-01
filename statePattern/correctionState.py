import cv2
import pandas as pd
import sharedFunctions as sf
from laneMemory import laneMemory
import torch
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
    def proccess(self, frame, scale, model, df, midX, laneCenter, newMemory, Icameras):
        if self.idx == 0: 
            #First entered state 
            self.idx = 1
            self.assignPresistentMemory(newMemory)
            # if self.presistentMemory.leftExist == True: 
            #     camera_stream = gstreamer_pipeline(sensor_id=1)
            # else: 
            #     camera_stream = gstreamer_pipeline(sensor_id=0)
            # capture = openSideStream(camera_stream)
            #capture = openSideStream("/home/raf/local/cuda/bin/vivs/vid.webm")
            #print("Success")
            #capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
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
            #capture.release()
        else:
            # ret, nFrame = capture.retrieve()
            # if nFrame: #if it exists 
            #     rFrame = cv2.cvtColor(nFrame, cv2.COLOR_BGR2RGB)

            #     results = model(nFrame)
            #     df2 = pd.DataFrame(results.pandas().xyxy[0].sort_values("ymin")) #df = Data Frame, sorts x values left to right (not a perfect solution)
            #     df2 = df2.reset_index() # make sure indexes pair with number of rows
            #     df2.iterrows()
            #     polygonList2 = sf.usingCSVData(df2)
            #     newMemory = laneMemory(self.presistentMemory.leftExist, self.presistentMemory.rightExist, leftLane, rightLane)
            #     if len(polygonList2) > 4: #gross simplification
            #         laneCenter = frame.shape[1]/4
            #     else:
            #         laneCenter = 3*frame.shape[1]/4
            #     cv2.imshow("side_cam", rFrame)
            pass
    
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

   
def gstreamer_pipeline( #camera stream
    sensor_id=0, #id 0 = right, id 1 = left
    capture_width=640,
    capture_height=480,
    display_width=640,
    display_height=480,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "videoconvert ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )
