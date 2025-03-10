class twoLaneState:
    def __init__(self, left, right):
        self.left = left #Left Lane exists: Boolean
        self.right = right #Right Lane exists: Boolean
        #BOTH SHOULD BE TRUE 


    #Change state when only one lane is being detected
    def changeState(self):
        pass 