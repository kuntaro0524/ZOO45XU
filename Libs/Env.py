import sys,os

class Env():
    def __init__(self):
        self.beamline = "BL45XU"
        self.ms_address = '172.24.242.59'
        self.ms_port=10101
        self.bss_address = '192.168.231.2'
        self.bss_port=5555
        # This is for BL41XU
        if self.beamline=="BL41XU":
            self.zoom_up_pulse=4448
            self.mono_axis="tc1_stmono_1"
            # Intensity monitor z axis
            self.intensity_monitor_axis = "st2_monitor_1_z"
            #ON/OFF pulses
            self.int_mon_off=0
            self.int_mon_on=0

        elif self.beamline=="BL45XU":
            self.zoom_up_pulse=3200
            self.mono_axis="tc1_mono_1"
            # Intensity monitor z axis
            self.intensity_monitor_axis = "st2_light_1_z"
            #ON/OFF pulses
            self.int_mon_off=24000
            self.int_mon_on=800

        self.beamline_zoo_path = "/isilon/%s/BLsoft/PPPP/"%self.beamline
        self.beamline_lower = self.beamline.lower()
        self.blconfig_path = os.environ["BLCONFIG"]
        self.bssconfig_path = os.path.join(self.blconfig_path, "bss/bss.config")
        self.camerainf_path = os.path.join(self.blconfig_path, "video/camera.inf")

        if os.path.exists(self.camerainf_path): print("OKAY")
        if os.path.exists(self.bssconfig_path): print("OKAY")

