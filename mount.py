import Zoo
import MXserver
from MyException import *
import os
import sys
import glob
import time
import numpy as np
import socket
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")

if __name__ == "__main__":
    zoo = Zoo.Zoo()
    zoo.connect()
    zoo.getSampleInformation()

    trayid= sys.argv[1]
    pinid= sys.argv[2]
    zoo.mountSample(trayid, pinid)
    zoo.waitTillReady()

    zoo.disconnect()
