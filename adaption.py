
#Takes the data points taken from reading.py (functions likely called from reading.py itself) and adapts it into Justin's orginal code 

#using selfDrive.py as a point of reference
import time
import numpy as np
import cv2
import serial
import matplotlib.pyplot as plt
import Jetson.GPIO as GPIO  # Change this if you use a different library
from reading import *
import multiprocessing
from laneMemory import *
import sharedFunctions as sf
class PIDController:
    #Ctrl + C  & Ctrl + V
    def __init__(self, kp, ki, kd,integral_limit):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.last_error = 0
        self.integral_limit = integral_limit
    
    def update(self, error, dt):
        self.integral += error * dt
        # Clamp the integral to prevent windup
        self.integral = max(min(self.integral, self.integral_limit), -self.integral_limit)
        derivative = (error - self.last_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.last_error = error
        return output
    
def angleToDutyCycle(angle):
    return (angle / 180.0) * 10 + 2.5

def main():
    #
    selfDrvieAdapt()

def send_data(command):
    #sends data to serial port
    ser.write(f"{command}\n".encode())
    ser.flush()

def sendAngle(pwm, angle):
    #changes the angle the CAV is steering at
    pwm.ChangeDutyCycle(angle)


def drive(memory, midX, laneCenter, previousCommand,pid, frame_rate, commandQueue, angleQueue):
    previousCommand = command
    error = midX - laneCenter
    steering_adjustment = pid.update(error, 0.1/frame_rate)
    angle = 90 + (steering_adjustment * (-0.5)) 
    if memory.leftExist or memory.rightExist:
        command = 'F'
        print("Forward Sent")
    else:
        command = 'S'
        print("stop Sent")
    ##Creating processes 
    if(previousCommand != command): #to handle buffer
        commandQueue.put(command)
    clip_angle = max(20, min(160, angle))
    if 20 <= clip_angle <= 160: #change 30 and 160 to 20 and 160 respectively
        duty_cycle = angleToDutyCycle(clip_angle)
        print(f'duty cycle: {duty_cycle}, clipped angle: {clip_angle}')
    elif 0 <= clip_angle < 20: #new addition, covering cases that were generalised into else, hope this helps
        duty_cycle = angleToDutyCycle(20)  #left
        print("HARD LEFT -- Duty Cycle: {duty_cycle}  Clip Angle: {clip_angle}")
    elif 160 <= clip_angle <= 180: #right
        duty_cycle = angleToDutyCycle(160)
        print("HARD RIGHT-- Duty Cycle: {duty_cycle}  Clip Angle: {clip_angle}")
    else:
        duty_cycle = angleToDutyCycle(90.01)
    angleQueue.put(duty_cycle)

    return previousCommand

def mainLoop():
    #Define PID Controller 
    pid = PIDController(kp = 0.3, ki = 0.2, kd = 0.0002, integral_limit = 100)
    #
    GPIO.setwarnings(False)
    servoPin = 33
    GPIO.setmode(GPIO.BOARD)  # Use physical pin numberintrimmed.webmg
    GPIO.setup(servoPin, GPIO.OUT)
    pwm = GPIO.PWM(servoPin, 50)
    pwm.start(0) #Intialisation with 0% duty cycle 
    frame_rate = 30
    capture, model = openStream("/dev/video0")
    firstFrame = True 
    frame_count = 0
    ###### Multiprocessing Shenagans  -- https://stackoverflow.com/questions/29571671/basic-multiprocessing-with-while-loop
    #Create a manager
    manager = multiprocessing.Manager()
    #Data strcutres
    commandQueue = manager.Queue()
    angleQueue = manager.Queue()
    p1 = multiprocessing.Process(target=commandSender, args=(commandQueue, ))
    p2 = multiprocessing.Process(target=angleSender, args=(angleQueue, pwm, ))
    p2.start()
    p1.start()
    #Processing each frame
    try:
        while capture.isOpened():
            ret, frame = capture.read()
            if firstFrame:
                midX = int((frame.shape[1])/2)
                firstFrame = False
                laneCenter = midX
                scale = sf.calcScale(midX)
                newMemory = laneMemory(False, False, [], [])
                detections = 0
            if not ret:
                break
            ### ###
            oldMemory = newMemory
            frame = convertBird(frame)
            laneCenter, newMemory = proccess(frame, scale, model, midX, laneCenter, newMemory)
            if cv2.waitKey(1) == ord('q'):#diplays the image for a set amount of time 
                break
            frame_count += 1 #used for lane weighting 
            if frame_count > 10:
                previousCommand = drive(newMemory, midX, laneCenter, previousCommand, pid, frame_rate, commandQueue, angleQueue)
            if(detections >= 3): 
                    newMemory = laneMemory(oldMemory.leftExist, oldMemory.rightExist, [], [])
                    detections = 0
            ### ### ### ### ### ### ### ### ###
    except KeyboardInterrupt:
        pass
    #Close
    commandQueue.put("END")
    angleQueue.put("END")
    p1.join()
    p2.join()
    capture.release()
    cv2.destroyAllWindows()
def commandSender(commandQueue):
    #https://stackoverflow.com/questions/29571671/basic-multiprocessing-with-while-loop
    while True:
        newVal = commandQueue.get() #Block until something is plaves on the queue
        if newVal == "END": #Terminate Queue on this condition
            break 
        send_data(newVal)
    return 
def angleSender(angleQueue, pwm):
    #https://stackoverflow.com/questions/29571671/basic-multiprocessing-with-while-loop
    while True:
        newVal = angleQueue.get() #Block until something is plaves on the queue
        if newVal == "END": #Terminate Queue on this condition
            break 
        sendAngle(pwm, newVal)
    return 

def selfDrvieAdapt():
    #Define PID Controller 
    pid = PIDController(kp = 0.3, ki = 0.2, kd = 0.0002, integral_limit = 100)
    #
    GPIO.setwarnings(False)
    servoPin = 33
    GPIO.setmode(GPIO.BOARD)  # Use physical pin numberintrimmed.webmg
    GPIO.setup(servoPin, GPIO.OUT)
    pwm = GPIO.PWM(servoPin, 50)
    pwm.start(0) #Intialisation with 0% duty cycle 
    frame_rate = 30
    #Testing reading prediction output 
    #Takes the base line from writetoCSV and adapts selfDive.py over it 
    print("Starting...")
    snapString = 'NULL'
    model_name='../lb2OO07.pt' #manual replace with our current model here 
    command = 's'
    #load model
    model = torch.hub.load('../yolov5', 'custom', source='local', path = model_name, force_reload = True)
    laneState = lc.laneController()
    ###### Multiprocessing Shenagans  -- https://stackoverflow.com/questions/29571671/basic-multiprocessing-with-while-loop
    #Create a manager
    manager = multiprocessing.Manager()
    #Data strcutres
    commandQueue = manager.Queue()
    angleQueue = manager.Queue()
    p1 = multiprocessing.Process(target=commandSender, args=(commandQueue, ))
    p2 = multiprocessing.Process(target=angleSender, args=(angleQueue, pwm, ))
    p2.start()
    p1.start()
    videoPath = "../dev/video0"
    #videoPath = "http://172.25.0.46:9001/camera.cgi" #remoting via vpn 
    firstFrame = True
    #Opening with openCV
    capture = cv2.VideoCapture(videoPath)
    frame_count = 0
    capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    #Processing each frame
    try:
        while capture.grab():
            ret, frame = capture.retrieve()
            if not ret: 
                break #bad practice to have a break here, this however is the only remaining line from when I used chatgpt as a point of reference
            if frame_count % 3 == 0: ####Say the fps is 30, runs ten times a second 
               
                if firstFrame:
                    midX = int((frame.shape[1])/2)
                    firstFrame = False
                    laneCenter = midX
                    scale = sf.calcScale(midX)
                    newMemory = laneMemory(False,False,[],[])
              
                #Convert each frame into RBG
                frame = frame[(int)(2*frame.shape[0]/5): frame.shape[0], 0:frame.shape[1]]  #y , x
                rFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = model(rFrame)
                results.print() #prints to terminal (optional)
                #results.save() #saves the image to an exp file (optional)
                #results.xyxy[0]  # im redictions (tensor) 
                df = pd.DataFrame(results.pandas().xyxy[0].sort_values("ymin")) #df = Data Frame, sorts x values left to right (not a perfect solution)
                df = df.reset_index() # make sure indexes pair with number of rows
                df.iterrows()
    
                laneCenter, newMemory = laneState.proccess(frame, scale, df, midX, laneCenter, newMemory)
                if cv2.waitKey(1) == ord('q'):#diplays the image  a set amount of time 
                    break

                if frame_count > 10:
                    previousCommand = command
                    error = midX - laneCenter
                    steering_adjustment = pid.update(error, 0.1/frame_rate)
                    angle = 90 + (steering_adjustment * (-0.5)) 
                    if newMemory.leftExist or newMemory.rightExist:
                        command = 'F'
                        print("Forward Sent")
                    else:
                        command = 'S'
                        print("stop Sent")
                    ##Creating processes 
                    if(previousCommand != command): #to handle buffer
                        commandQueue.put(command)
                        
                    clip_angle = max(20, min(160, angle))
                    if 20 <= clip_angle <= 160: #change 30 and 160 to 20 and 160 respectively
                        duty_cycle = angleToDutyCycle(clip_angle)
                        print(f'duty cycle: {duty_cycle}, clipped angle: {clip_angle}')
                    elif 0 <= clip_angle < 20: #new addition, covering cases that were generalised into else, hope this helps
                        duty_cycle = angleToDutyCycle(20)  #left
                        print("HARD LEFT -- Duty Cycle: {duty_cycle}  Clip Angle: {clip_angle}")
                    elif 160 <= clip_angle <= 180: #right
                        duty_cycle = angleToDutyCycle(160)
                        print("HARD RIGHT-- Duty Cycle: {duty_cycle}  Clip Angle: {clip_angle}")
                    else:
                        duty_cycle = angleToDutyCycle(90.01)
                    angleQueue.put(duty_cycle)
            frame_count += 1
    except KeyboardInterrupt:
        pass
    #Close and release
    commandQueue.put("END")
    angleQueue.put("END")
    p1.join()
    p2.join()
    send_data('S')
    capture.release()
    cv2.destroyAllWindows()
    pwm.stop() 
    GPIO.cleanup()
    return 0


if __name__ == "__main__":
    # Open serial port
    try:
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        GPIO.setwarnings(False)
        time.sleep(2)  # wait for the serial connection to initialize
    except Exception as e:
        print(f"Could not open serial port: {e}")
        ser = None  # Ensure ser is defined even if the port couldn't be opened
    # Check CUDA availability
    if cv2.cuda.getCudaEnabledDeviceCount() == 0:
        print("CUDA not available - the program requires a GPU with CUDA.")
        exit()  # Exit if CUDA is not available
    print("Serial port is connected and GPU is available")
    time.sleep(1)
    main()
    print("end")
    # Close serial if open
    if ser is not None:
        ser.close()
