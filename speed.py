#File Used to handle all functions related to the speed of the CAV
#Speed must be sent in the form of "S[value]\n"
#Max of S100, Min of S-100
#Negaives will reverse, S0 is stop

#CONSTANTS 
MAX_SPEED = 18 #straight aways with high vision - might be too quick 
MIN_SPEED = 13 #turning - very slow
dx = 0 
change = 0.2 

def calc_speed(leftlane, rightlane):
    command = "S0\n"
    #determine a speed based on how far up the highest point is and whether or not both lanes are detected 
    
    if len(leftlane) > 0 or len(rightlane) > 0: 
        pass
    
    return command