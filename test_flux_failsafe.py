#!/bin/env python
# Test for the fail safe in Device.measureFlux (2026/11/13)
# usage:
#   python test_flux_failsafe.py            : step check + Device.measureFlux()
#   python test_flux_failsafe.py --no-beam  : shutter.open() is disabled,
#                                             measureFlux() should raise MyException
import sys
import socket
import time

sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")

import Device
import MyException

host = '172.24.242.59'
port = 10101

simulate_no_beam = "--no-beam" in sys.argv

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

dev = Device.Device(s, bl="bl45xu")
dev.init()

if simulate_no_beam:
    print "=== Simulation: shutter.open() is disabled (X-ray does not reach the sample) ==="
    dev.shutter.open = lambda: None
else:
    # Step check: shutter state and PIN counts
    print "=== Step check ==="
    dev.prepMeasureFlux()
    try:
        for state in ["close", "open", "close", "open"]:
            if state == "close":
                dev.shutter.close()
            else:
                dev.shutter.open()
            time.sleep(0.5)
            is_open = dev.shutter.isOpen()
            ipin, iic = dev.countPin(pin_ch=1)
            print "shutter %-5s -> isOpen()=%s PIN count=%d" % (state, is_open, ipin)
    finally:
        dev.finishMeasureFlux()
    print "shutter after finishMeasureFlux: isOpen()=%s" % dev.shutter.isOpen()

print "=== Device.measureFlux() ==="
try:
    phosec = dev.measureFlux()
    print "Flux: %e photons/sec" % phosec
    if simulate_no_beam:
        print "NG: MyException was not raised"
except MyException.MyException, e:
    print "MyException: %s" % e.args[0]
    if simulate_no_beam:
        print "OK: fail safe stopped the measurement"
print "shutter after measureFlux: isOpen()=%s" % dev.shutter.isOpen()

s.close()
