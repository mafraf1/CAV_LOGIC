#STATE PATTERN
#WILL BE ASSIGNED EITHER oneLaneState or twoLaneState 
from statePattern import oneLaneState as ol
from statePattern import twoLaneState as tl 
from statePattern import correctionState as cs
class laneController:

    def __init__(self):
        self.onelanestate = ol.oneLaneState(self)
        self.twolanestate = tl.twoLaneState(self)
        self.correctionstate = cs.correctionState(self)
        self.state = self.twolanestate 

    #Change the state of the objects held by lanestat3e
    def changeState(self):
        self.state.changeState() 

    #To tell us what state it is in
    def getState(self):
        return self.state.getState()
    
    #Calls an unique process depending on the state 
    def proccess(self, frame, scale, model, midX, laneCenter, newMemory): 
        return self.state.proccess(frame, scale, model, midX, laneCenter, newMemory)
