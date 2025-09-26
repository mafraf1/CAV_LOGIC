# CAV_LOGIC

TO RUN;
    You will need:
        - A pytorch file for lane detection
        - yolov5 in the same directory with detect.py since we use their LLM to train lane detection
        - All files neccessary for a run are: 
            - all files in the statePattern Folder. -> They handle logic for different driving states the CAV may be in. 
            - adaption.py -> This is the MAIN file that CAV runs off. Handles initilasing of PID, CAMERAS and the YOLOv5 model, and contains the main for loop which all logic is held.
            - cameraWidget.py -> Specifies a camera object and inits each personal thread a camera would run off of.
            - cavErrors.py -> Customs errors for the CAV. 
            - gstreamerPipeline.py -> Specifies the pycams for setting up a camera object. 
            - laneMemory.py -> An object which holds information relating to the current detection instance. 
            - reading.py -> needed for local testing. 
            - sharedFunctions.py -> Contains misc functions used by multiple files. E.g. Functions used by the statePattern.py, adaption.py, and reading.py 
            - speed.py -> contains basic logic for determining the speed the CAV should drive at. 
            - test.py -> a testing file used for testing specific feature or local testing. 
    
    COMMANDS: 

    python3.8 adaption.py
     
     
TO CANCEL RUN;
    Press 'q' on a camera window.

IMPORTANT:
At the moment certain conditions are hardcoded. These include:
-Which Cameras are being called in
-Model Name (Currently using pytorch)


And you will need to manually change it in the code before running,
if runnning just for video (no CAV); test.py -> writeToCSV()
if running on CAV with GPIO and Motor; adaption.py -> selfDriveAdapt()

The reason why they are separate is because all actions are currently being determined off 
the while loop, so therefore for now, selfDriveAdapt() exists specifically for running on the CAV.
With selfDriveAdapt() checking and connecting to the serial ports and sending data to the GPIO.

*************************************************************************
*AUTHOR -> Rafael Skellett, 21498314, UPDATED: 26/9/25                  *
*************************************************************************

REFERENCES:
Uses yolov5 https://github.com/ultralytics/yolov5
