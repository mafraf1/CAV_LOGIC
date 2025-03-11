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
    
    def proccess(self, frame, scale, model, midX, laneCenter, newMemory):
        pass

    