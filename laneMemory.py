class laneMemory: 
    # Creation 29.08.2024 
    # Last Changed: 4.4.2025 -- removed unused function 
    # PURP: Defines a snapshot of a processed lane
    # VAR: leftExist, rightExist, leftLane, rightLane
    # may contain methods in handling comparison between two lane Memories 
    # AIM:  to help fix some on the inconsistencies with the current lane detection

    def __init__(self):
        #Default Constructor
        self.leftExist = False
        self.rightExist = False
        self.leftLane = []
        self.rightLane = []
        self.laneCentreList = [] #List of previous lane centres

    def __init__(self, pLeftExist, pRightExist, pLeftLane, pRightLane, pLaneCentreList):
        #Constructor with parameters 
        self.leftExist = pLeftExist
        self.rightExist = pRightExist
        self.leftLane = pLeftLane
        self.rightLane = pRightLane
        self.laneCentreList = pLaneCentreList

    def updateLaneCentreList(self, newCentre):
        self.laneCentreList.append(newCentre)
        if len(self.laneCentreList) > 5:
            self.laneCentreList.pop(0)
    
