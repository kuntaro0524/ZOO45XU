import os,sys,glob
import time
import numpy as np
import socket
from MyException import *
import Zoo

if __name__ == "__main__":
    zoo=Zoo.Zoo()
    zoo.connect()
    zoo.doRaster(sys.argv[1])
    zoo.waitTillReady()
    zoo.disconnect()
