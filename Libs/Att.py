# -*- coding: utf-8 -*-
import sys
import socket
import time
import math
import Env
import BSSconfig
from numpy import *

# My library
from Motor import *


class Att:
    def __init__(self, server):
        self.s = server
        # ビームラインの名前など
        self.env = Env.Env()
        self.bssconf = BSSconfig.BSSconfig(self.env.bssconfig_path)
        self.bl_object = self.bssconf.getBLobject()
        # 大文字のビームライン名
        self.beamline = self.env.beamline

        # BL41XUは２つある/BL45XUは１つ
        self.att1_name = "st2_att_1_rx"
        if self.beamline == "BL41XU":
            self.att2_name = "st2_att_2_rx"
            self.att1 = Motor(self.s, "bl_%s_%s" %
                              (self.bl_object, self.att1_name), "pulse")
            self.att2 = Motor(self.s, "bl_%s_%s" %
                              (self.bl_object, self.att2_name), "pulse")

            # BL41XU ハードコードをしてしまう
            self.att1_noatt_pulse = -20
            self.att2_noatt_pulse = 0

        else:
            self.att1 = Motor(self.s, "bl_%s_%s" %
                              (self.bl_object, self.att1_name), "pulse")
            # BL45XU ハードコードをしてしまう
            self.att1_noatt_pulse = 3500

        self.isInit = False

    # BL41XU専用
    def setNoAtt(self):
        self.att1.move(self.att1_noatt_pulse)
        self.att2.move(self.att2_noatt_pulse)

    # 220323 'init' function does not read 'bss.config' because
    # アッテネータを変更するのはBSSでやれば良いので
    # フラックスを測定するときだけ 0 アッテネータを実現できれば良い
    # というわけでこの関数の中身を変えてしまう
    # Get Thick - Index - Pulse
    def init(self):
        confile = open(self.bssconf, "r")
        lines = confile.readlines()
        confile.close()
        self.isInit = True

    def setAttThick(self, thick):
        # BL41XUのやつは複雑なのでゼロアッテネータにしか対応しない
        if self.beamline=="BL41XU":
            if thick == 0.0:
                self.setNoAtt()
            else:
                print("Please do not modify attenuator thickness other than 0.0 mm")
                sys.exit()
        # 他のビームラインはbssconfigから読んでも問題はない
        # BL45XUの最新のコードはこれになっているので倣う
        else:
            # BSS config から該当のパラメタを読む
            if self.isInit == False:
                self.init()
            for t_conf, p_conf in zip(self.att_thick, self.att_pulse):
                if thick == t_conf:
                    print("Set thickness to %5d [um]" % thick)
                    self.move(p_conf)
                    return True
        return False

    def getAttList(self):
        if self.isInit == False:
            self.init()
        return self.att_thick

    def getBestAtt(self, wl, transmission):

        if not self.isInit:
            self.init()
        attlist = self.att_thick
        cnfac = self.cnFactor(wl)
        mu = self.calcMu(wl, cnfac)
        thickness = (-1.0 * math.log(transmission) / mu) * 10000

        print "IDEAL thickness: %8.1f[um]" % thickness

        idx = 0
        for att in attlist:
            if thickness < att:
                if att - thickness < 1000.0:
                    return att
                else:
                    return attlist[idx - 1]
            idx += 1

    def getBestExpCondition(self, wl, transmission):
        if self.isInit == False:
            self.readBSSconfig()
        attlist = self.att_thick
        cnfac = self.cnFactor(wl)
        mu = self.calcMu(wl, cnfac)
        thickness = (-1.0 * math.log(transmission) / mu) * 10000

        print "IDEAL thickness: %8.1f[um]" % thickness

        near_idx = 0
        for att in attlist:
            if thickness < att:
                break
            near_idx += 1

        for i in range(near_idx - 2, near_idx + 1):
            if i >= len(attlist):
                i = len(attlist) - 1
            # print "Aimed:",transmission
            curr_trans = self.calcAttFac(wl, attlist[i])
            exptime = transmission / curr_trans
            if exptime <= 1.5 and exptime > 0.2:
                print attlist[i], curr_trans, exptime
                return attlist[i], exptime

    def getAttBefore(self, althick):
        if self.isInit == False:
            self.readBSSconfig()
        attlist = self.att_thick

        idx = 0
        for att in attlist:
            if althick == att:
                return attlist[idx - 1]
            idx += 1

    def setAttTrans(self, wl, trans):
        best_att = self.getBestAtt(wl, trans)
        print "Set Al thickness to ", best_att, "[um]"
        self.setAtt(best_att)
        return best_att

    def move(self, pls_bss):
        self.att.move(-pls_bss)

    def getAttIndexConfig(self, t):
        if t == 0.0:
            return 0
        if self.isInit == False:
            self.init()
        for i, thick in zip(self.att_idx, self.att_thick):
            if thick == t:
                return i
        print "Something wrong: No attenuator at this beamline"
        return -9999

    def cnFactor(self, wl):
        cnfac = 0.028 * math.pow(wl, 5) - 0.188 * math.pow(wl, 4) + 0.493 * math.pow(wl, 3) - 0.633 * math.pow(wl,
                                                                                                               2) + 0.416 * math.pow(
            wl, 1) + 0.268
        return cnfac

    def calcMu(self, wl, cnfac):
        mu = 38.851 * math.pow(wl, 3) - 2.166 * math.pow(wl, 4) + 1.3 * cnfac
        return mu

    def calcAttFac(self, wl, thickness, material="Al"):
        # thickness [um]
        if material == "Al":
            cnfac = self.cnFactor(wl)
            mu = self.calcMu(wl, cnfac)
            attfac = math.exp(-mu * thickness / 10000)
            return attfac
        else:
            return -1

    def calcThickness(self, wl, transmission, material="Al"):
        # thickness [um]
        if material == "Al":
            cnfac = self.cnFactor(wl)
            mu = self.calcMu(wl, cnfac)
            thickness = (-1.0 * math.log(transmission) / mu) * 10000
            return thickness
        else:
            return -1

    def isMoved(self):
        isAtt = self.att.isMoved()

        if isAtt == 0:
            return True
        if isAtt == 1:
            return False


if __name__ == "__main__":
    host = '172.24.242.54'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    att = Att(s)
    # att.setNoAtt()
    att.setAttThick(0.0)

    s.close()
