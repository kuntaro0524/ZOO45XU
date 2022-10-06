#!/bin/env python 
import sys
import socket
import time
import datetime
import Env
import BSSconfig

# from Count import *
# My library

class Shutter:
    def __init__(self, server):
        env = Env.Env()
        self.bssconf = BSSconfig.BSSconfig(env.bssconfig_path)
        self.s = server
        self.bl_object = self.bssconf.getBLobject()

        self.openmsg = "put/bl_%s_st2_shutter_1/on" % self.bl_object
        self.clsmsg = "put/bl_%s_st2_shutter_1/off" % self.bl_object
        self.qmsg = "get/bl_%s_st2_shutter_1/status" % self.bl_object

    def open(self):
        self.s.sendall(self.openmsg)
        print self.s.recv(8000)  # dummy buffer

    # self.query()

    def close(self):
        self.s.sendall(self.clsmsg)
        print self.s.recv(8000)  # dummy buffer

    # self.query()

    def query(self):
        self.s.sendall(self.qmsg)
        return self.s.recv(8000)  # dummy buffer

    def isOpen(self):
        strstr = self.query()
        cutf = strstr[:strstr.rfind("/")]
        final = cutf[cutf.rfind("/") + 1:]
        if final == "off":
            return 0
        else:
            return 1


if __name__ == "__main__":
    env = Env.Env()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((env.ms_address, env.ms_port))

    shutter = Shutter(s)
    # shutter.open()
    print(shutter.isOpen())
    shutter.open()  
    time.sleep(5.0)
    print(shutter.isOpen())
    time.sleep(5.0)
    shutter.close()
    time.sleep(5.0)
    shutter.open()  
    print(shutter.isOpen())
    s.close()
