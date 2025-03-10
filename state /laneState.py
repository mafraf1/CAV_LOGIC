#STATE PATTERN
#WILL BE ASSIGNED EITHER oneLaneState or twoLaneState 
import oneLaneState
import twoLaneState 

class laneState:

    def __init__(self):
        self.onelanestate = oneLaneState(self)
        self.twolanestate = twoLaneState(self)
        self.state = self.twolanestate 

    #Change the state of the objects held by lanestat3e
    def changeState(self):
        self.state.changeState() 