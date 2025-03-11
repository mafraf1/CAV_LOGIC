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
    def proccess(frame, scale, model, midX, laneCenter, newMemory):
        pass