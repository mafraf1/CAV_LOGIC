#STATE PATTERN
#WILL BE ASSIGNED EITHER oneLaneState or twoLaneState 
from statePattern import oneLaneState as ol
from statePattern import twoLaneState as tl 

class laneController:

    def __init__(self):
        self.onelanestate = ol.oneLaneState(self)
        self.twolanestate = tl.twoLaneState(self)
        self.state = self.twolanestate 

    #Change the state of the objects held by lanestat3e
    def changeState(self):
        self.state.changeState() 

    def getState(self):
        return self.state.getState()