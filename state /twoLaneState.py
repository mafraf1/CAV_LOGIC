class twoLaneState:
    #Init State
    def __init__(self, laneState):
        self.laneState = laneState
        # self.left = left #Left Lane exists: Boolean
        # self.right = right #Right Lane exists: Boolean
        #BOTH SHOULD BE TRUE 

    #Change state when only one lane is being detected
    def changeState(self):
        self.laneState.state =  self.laneState.twolanestate