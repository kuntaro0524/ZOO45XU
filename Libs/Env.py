import sys,os

class Env():
    def __init__(self):
        self.beamline = "BL41XU"
        self.ms_address = '172.24.242.59'
        self.ms_port=10101
        self.bss_address = '192.168.231.2'
        self.bss_port=5555
        # This is for BL41XU
        if self.beamline=="BL41XU":
            self.zoom_up_pulse=4448
        elif self.beamline=="BL45XU":
            self.zoom_up_pulse=3200
# 192.168.231.2
        self.beamline_zoo_path = "/isilon/%s/BLsoft/PPPP/"%self.beamline
        self.beamline_lower = self.beamline.lower()
        self.blconfig_path = os.environ["BLCONFIG"]
        self.bssconfig_path = os.path.join(self.blconfig_path, "bss/bss.config")
        self.camerainf_path = os.path.join(self.blconfig_path, "video/camera.inf")

        if os.path.exists(self.camerainf_path): print("OKAY")
        if os.path.exists(self.bssconfig_path): print("OKAY")

