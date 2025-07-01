#A state to very handle merging in a very basic manner 
#Will need to use game theory to decide how the CAV will merge into the lane if there are other vehicles 
import laneMemory 

#HOW WILL WE KNOW WHEN TO MERGE 
#HOW WILL WE KNOW THAT WE HAVE MERGERD?

class mergeState: 
    def __init__(self, laneState):
        self.laneState = laneState
        self.presistentMemory = laneMemory(False, False,[],[])
        self.idx = 0
        self.speed = "S15\n"
        self.mergeLeft = False 
        self.mergeRight = False

    def getState(self):
        if self.mergeLeft:
            return 5
        elif self.mergeRight:
            return 6 
        else:
            return -2 #error state 
    
    def getSpeed(self):
        return self.speed