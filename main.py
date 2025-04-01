from cameraWidget import cameraStreamWidget
from reading import *

def main():
    # p1 = multiprocessing.Process(target=writeToCSV, args=())
    # p2 = multiprocessing.Process(target=test, args=())
    # # writeToCSV()
    # # test()
    # p2.start()
    # #p2.start()
    # p2.join
    #p2.join
    # cameras = []
    # cameras.append(cameraStreamWidget("/home/raf/local/cuda/bin/vivs/vid.webm", "One"))
    # cameras.append(cameraStreamWidget("/home/raf/local/cuda/bin/vivs/vid3.webm", "Three"))
    # while True:
    #     try:
    #         for cam in cameras:
    #             cam.show_frame()
    #     except AttributeError:
    #         pass
    #cameras.append(cameraStreamWidget())
    processEachFrame()
    print("Completed")

main()
    