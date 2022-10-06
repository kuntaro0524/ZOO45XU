#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *
import BSSconfig
import Env

# information of collision between BM and Gonio
class IntensityMonitor:
    def __init__(self, server):
        env = Env.Env()
        self.bssconf = BSSconfig.BSSconfig(env.bssconfig_path)
        self.s = server
        self.bl_object = self.bssconf.getBLobject()

        self.s = server
        self.mon_z = Motor(self.s, "bl_%s_%s"%(self.bl_object, env.intensity_monitor_axis),"pulse")
        print(self.mon_z)
        # self.v2p_x, self.sense = self.bssconf.getPulseInfo(self.mon_z)

        self.on_pulse=env.int_mon_on
        self.off_pulse=env.int_mon_off
        self.isPrep = False

    def getEvacuate(self):
        self.on_pulse, self.off_pulse = self.bssconf.getEvacInfo(self.axis_name)
        self.isPrep = True

    def getPosition(self):
        curr_pos = self.sense*self.mon_z.getPosition()[0]
        return curr_pos

    def goDown(self):
        curr_pos = self.sense*self.mon_z.getPosition()[0]
        target_pos = curr_pos + self.sense*1000
        self.mon_z.move(target_pos)

    def setPosition(self, def_position):
        self.mon_z.move(def_position*self.sense)

    def relDown(self):
        curr_pos = self.mon_z.getPosition()[0]
        target_pos = curr_pos - 100
        self.mon_z.move(target_pos)

    def on(self):
        # Temp removed 2022/10/6 BL45XU K.Hirata
        # if self.isPrep == False: 
            # self.getEvacuate()
        self.mon_z.move(self.on_pulse)

    def off(self):
        # Temp removed 2022/10/6 BL45XU K.Hirata
        # if self.isPrep == False: 
            # self.getEvacuate()
        # if self.isPrep == False: 
            # self.getEvacuate()
        self.mon_z.move(self.off_pulse)

    def goOn(self):
        self.mon_z.nageppa(self.on_pos)

    def go(self, value):
        self.mon_z.nageppa(value)

    def goOff(self):
        self.mon_z.nageppa(self.off_pos)

if __name__ == "__main__":
    host = '172.24.242.59'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    monitor = IntensityMonitor(s)
    # monitor.getPosition()
    # monitor.getEvacuate()
    monitor.on()
    monitor.off()

    s.close()
