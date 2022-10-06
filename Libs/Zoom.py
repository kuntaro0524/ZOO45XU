#!/bin/env python
import sys
import socket
import time

from Motor import *
import BSSconfig
import Env

class Zoom:
    def __init__(self, server):
        env = Env.Env()
        self.bssconf = BSSconfig.BSSconfig(env.bssconfig_path)
        self.bl_object = self.bssconf.getBLobject()

        self.s = server
        self.zoom_info = self.bssconf.readZoomOption()
        # The minimum zoom -> Zoom out pulse
        self.out_lim = int(self.zoom_info[0][1])
        print("ZoomOut pulse=", self.out_lim)

        self.axis = "bl_%s_st2_coax_1_zoom" % self.bl_object
        print(self.axis)
        self.zoom = Motor(self.s, self.axis, "pulse")

        self.qcommand = "get/" + self.axis + "/" + "query"

        self.in_lim = "0"  # pulse
        # self.out_lim = "1480"  # pulse

    def go(self, pvalue):
        self.zoom.nageppa(pvalue)

    def move(self, pvalue):
        self.zoom.move(pvalue)

    def zoomIn(self):
        self.zoom.move(self.in_lim)

    def getPosition(self):
        return self.zoom.getPosition()[0]

    def zoomOut(self):
        min_ratio = 99999.9999
        min_pulse = 0
        for zoom,zoom_pulse in self.zoom_info:
           if min_ratio > zoom:
               min_ratio = zoom 
               min_pulse = zoom_pulse
               self.out_lim = min_pulse
        print("moving to %s" % self.out_lim)
        self.zoom.move(self.out_lim)

    def isMoved(self):
        isZoom = self.zoom.isMoved()

        if isZoom == 0:
            return True
        if isZoom == 1:
            return False

    def stop(self):
        command = "put/" + self.axis + "/stop"
        self.s.sendall(command)
        tmpstr = self.s.recv(8000)


if __name__ == "__main__":
    env=Env.Env()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((env.ms_address, env.ms_port))

    zoom = Zoom(s)
    print("Initialization finished")
    start = zoom.getPosition()
    zoom.zoomOut()
    # print start
    #zoom.move(950)
    #zoom.zoomOut()
    # zoom.inZoom()
    # time.sleep(5)
    s.close()
