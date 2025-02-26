import LoopMeasurement as LM
import BLFactory
import os
import Zoo

root_dir= "./"
blf = BLFactory.BLFactory()
blf.initDevice()
dev = blf.device

prefix="data01"

# prep centering
dev.prepCentering()

lm = LM.LoopMeasurement(blf, root_dir, prefix)
lm.prepDataCollection()

backimage = "/staff/bl44xu/BLsoft/TestZOO/BackImages/back.ppm"

rwidth,rheight=lm.centering(backimage, 600, offset_angle=0.0, height_add=0.0)

x,y,z,sphi = dev.gonio.getXYZPhi()
center_xyz = [x,y,z]

scan_id="scan"
scan_mode="2D"

scanv_um=rwidth
scanh_um=rheight
vstep_um=20
hstep_um=20

cond = {'dist_raster':300, 'exp_raster':0.1, 
        'raster_roi':0, 'raster_vbeam': 50, 'raster_hbeam':50, 'att_raster':0.05,
        'wavelength':1.0}

schfile, raspath = lm.rasterMaster(scan_id, scan_mode, center_xyz, 
                                   scanv_um, scanh_um, vstep_um, hstep_um, sphi, cond)


# Doing the experiment
zoo = Zoo.Zoo()
zoo.connect()
zoo.doRaster(raspath)
zoo.waitTillReady()
zoo.disconnect()