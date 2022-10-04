#!/bin/env python 
import sys
import socket
import time

# My library
from Received import *
from Motor import *
import BSSconfig

# information of collision between BM and Gonio
class IntensityMonitor:
    def __init__(self, server):
        self.bssconf = BSSconfig.BSSconfig('/isilon/blconfig/bl41xu/bss/bss.config')
        self.bl_object = self.bssconf.getBLobject()

        self.s = server
        self.axis_name = "st2_monitor_1_z"
        self.mon_z = Motor(self.s, "bl_%s_%s"%(self.bl_object, self.axis_name),"pulse")
        self.v2p_x, self.sense = self.bssconf.getPulseInfo(self.axis_name)

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
        if self.isPrep == False: 
            self.getEvacuate()
        self.mon_z.move(self.on_pulse)

    def off(self):
        if self.isPrep == False: 
            self.getEvacuate()
        self.mon_z.move(self.off_pulse)

    def goOn(self):
        self.mon_z.nageppa(self.on_pos)

    def go(self, value):
        self.mon_z.nageppa(value)

    def goOff(self):
        self.mon_z.nageppa(self.off_pos)

if __name__ == "__main__":
    host = '172.24.242.54'
    port = 10101

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    monitor = IntensityMonitor(s)
    monitor.getPosition()
    monitor.getEvacuate()
    monitor.on()
    monitor.off()

    s.close()