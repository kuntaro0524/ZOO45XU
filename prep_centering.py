import sys,os,math,socket
import datetime
import numpy as np

sys.path.append("./Libs")
import Env
env = Env.Env()
sys.path.append(env.beamline_zoo_path)
from MyException import *

from File import *
import Capture
import Device

if __name__ == "__main__":
    ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ms.connect(("172.24.242.59", 10101))

    dev = Device.Device(ms)
    dev.init()
    dev.prepCentering()
