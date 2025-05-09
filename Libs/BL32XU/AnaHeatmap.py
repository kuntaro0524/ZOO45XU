import sys,os,math,numpy,scipy
import scipy.spatial as ss
import MyException
import time
import datetime
import DiffscanLog
import SummaryDat
import Crystal

class AnaHeatmap:
    def __init__(self,scan_path,cxyz,phi):
        self.scan_path=scan_path
        self.isRead=False
        self.isKind=False
        self.isList=False
        self.isScoreAbove=False
        self.diffscan_path="%s/"%self.scan_path
        self.summarydat_path="%s/_spotfinder/"%self.scan_path
        self.DEBUG=False
        self.cen_xyz=cxyz # Goniometer coordinate of this scan
        self.phi=phi

        # DEBUG option
        self.debug=False

        # Threshold for min/max score
        # Crystals with core ranging self.min_score to self.max_score
        # data collection is applied
        self.min_score=20
        self.max_score=80

        # prep flag
        self.isPrep=False
        self.crysize_mm=0.015

    def getDiffscanPath(self):
        return self.diffscan_path

    def setCrystalSize(self,size_mm):
        self.crysize_mm=size_mm
        self.search_radius_mm=size_mm/2.0+0.001

    #def prep(self,prefix):
    # prefix: scan_id in diffraction scan log
    def prep(self,prefix):
        dl=DiffscanLog.DiffscanLog(self.diffscan_path)
        dl.prep()
        # NDarray (V x H) map from diffscan.log
        # The 1st scan result will be analyzed
        dlmap=dl.getNumpyArray(scan_index=0)
        self.nv,self.nh=dl.getScanDimensions()
        print "Vertical  =",self.nv
        print "Horizontal=",self.nh
        # in [mm] steps
        self.v_step,self.h_step=dl.getScanSteps()
        print self.v_step,self.h_step

        nimages_all=self.nv*self.nh

        # From summary.dat
        # score heat map will be extracted
        sumdat=SummaryDat.SummaryDat(self.summarydat_path,self.cen_xyz,self.phi,self.nv,self.nh)
        sumdat.readSummary(prefix,nimages_all,1.00,timeout=120)
        # Score is arrayed to numpy.ndarray[N_Vertical,N_Horizontal]
        # 'SummaryDat' class sorts lines along with the image number
        tmp_heatmap=sumdat.process("n_spots")

        # Checking the heat map
        new_list=[]
        for v in range(0,self.nv):
            for h in range(0,self.nh):
                # diffscan.log map
                scanindex,imgnum,x,y,z=dlmap[v,h]
                new_list.append((scanindex,imgnum,x,y,z,tmp_heatmap[v,h]))
                #print "ORIGINAL:",v,h,tmp_heatmap[v,h]

        # ND array for XYZ coordinate(from diffscan.log)
        aa=numpy.array(new_list)
        self.heatmap=numpy.reshape(aa,(self.nv,self.nh,6))

        return self.heatmap

    def makeCheckMaps(self,prefix):
        # Preparation of self.heatmap
        if self.isPrep==False:
            self.prep(prefix)
            print "Heatmap shape=",self.heatmap.shape

        # A new map array is prepared here based on self.heatmap
        check_map_array=[]
        # KD tree map includes coordinates only
        kdtree_map_array=[]
        if self.debug:
            ofile=open("check_map.dat","w")
        for v in range(0,self.nv):
            for h in range(0,self.nh):
                scanindex,imgnum,x,y,z,score=self.heatmap[v,h]
                # Making the kdtree_map array
                kdtree_map_array.append((x,y,z))
                # Save the good grids to the check_map_array
                if score >= self.min_score and score <= self.max_score:
                    check_map_array.append((scanindex,imgnum,x,y,z,score))
                    if self.debug:
                        ofile.write("%5d %5d %5d\n"%(v,h,score))
                # 0 padding for the threshold-based NG grids
                else:
                    check_map_array.append((scanindex,imgnum,x,y,z,0))

        assert len(kdtree_map_array)==len(check_map_array)

        # Making numpy array for checking map and tree
        kdtree_map=numpy.array(kdtree_map_array)
        check_map=numpy.reshape(numpy.array(check_map_array),(self.nv,self.nh,6))
        print "TreeMap and CheckMap shep=",kdtree_map.shape,check_map.shape
        kdtree=scipy.spatial.cKDTree(kdtree_map)

        return kdtree_map,check_map,kdtree

    # mode: Multi
    # Function implemented
    # 1. Making 2D heat map as numpy 3D array
    # 2. KDTree array is setup
    # 3. Search loop
    # 3.1. Find the maximum score pixel
    # 3.2. Neighboring grids are listed and checked 
    # 3.3. If neighboring grid has larger score than the threshold,
    #      grouping them to the crystal spot
    def searchMulti(self,prefix,cry_size_mm):
        kdtree_map,check_map,kdtree=self.makeCheckMaps(prefix)

        #self.setCrystalSize(cry_size_mm)
        # 2019/02/06 search_radius_mm should be same as cry_size_mm
        # But this routine has 'setCrystalSize' function.
        # The routine calculates 'search_radius_mm' as the half length 
        # of the crystal size. This shoud be corrected but for helical
        # routine the function still works. So temporally, I modified
        # code here to set 'cry_size_mm' as 'search_radius_mm' in 
        # 'multiple small wedge data collection'
        self.search_radius_mm = cry_size_mm
        print "Distance threshold = ",self.search_radius_mm

        # Crystal array
        crystal_array=[]

        # Max score component
        if self.debug:
            ofile=open("tmp.dat","w")
        checked_grids=0
        while(1):
            print "\n\n"
            if self.debug:
                ofile.write("\n\n")
            # Get current maximum value from check_map
            h_max,v_max,maxindex,maxvalue=self.getMaxScoreIndex(check_map)
            # checked grids are set to 0.0. 
            if maxvalue==0.0:
                print "Complete!"
                break
            print "Checking %5d %5d"%(h_max,v_max)
            junk0,junk1,tx,ty,tz,score=check_map[v_max,h_max,:]
            # Searching 'near' grids within 'self.search_radius_mm'
            index=kdtree.query_ball_point((tx,ty,tz),self.search_radius_mm)
            print "kdtree.query indices=",index
            print "KDTree data=",kdtree_map[index]
            checked_grids+=len(index)
            # Making the Crystal class for storing good XYZ coordinates
            crystal=Crystal.Crystal(self.h_step,self.v_step)
            # Checking the score of neighboring grids
            for i in index:
                # index: heatmap vertical direction
                v_index=i/self.nh
                # index: heatmap horizontal direction
                h_index=i%self.nh
                # Checking the score
                check_score=check_map[v_index,h_index,5]
                # Already checked
                if check_score==0:
                    continue
                # This should be stored to Crystal class
                check_map[v_index,h_index,5]=0
                tmpxyz=check_map[v_index,h_index,:]
                crystal.addGrid(tx,ty,tz,h_index,v_index,score)
                if self.debug:
                    ofile.write("%8.3f %8.3f %8.3f %5d %5d %5d\n"%(tmpxyz[2],tmpxyz[3],tmpxyz[4],v_index,h_index,check_score))
            # append Crystal class to the crystal_list
            crystal_array.append(crystal)

        print "Number of found crystals=",len(crystal_array)
        print "Checked grids=",checked_grids
        for crystal in crystal_array:
            crystal.printAll()

        return crystal_array
    #searchMulti

    # searchPixelBunch
    # mode: multiple crystal (successive pixel maps) above score
    # Function implemented
    # 1. Making 2D heat map as numpy 3D array
    # 2. KDTree array is setup
    # 3. Search loop
    # 3.1. Find the maximum score pixel
    # 3.2. Neighboring grids are listed and checked 
    # 3.3. If neighboring grid has larger score than the threshold,
    #      grouping them to the crystal spot
    def searchPixelBunch(self,prefix,naname_include=True):
        # Making kdtree & check map
        kdtree_map,check_map,kdtree=self.makeCheckMaps(prefix)
        junk1,original_map,junk2=self.makeCheckMaps(prefix)

        if naname_include==True:
            # set the threshold of distance (Empirical value)
            size_for_bunch=2.0*(math.sqrt(2.0)*((self.v_step+self.h_step)/2.0))
            self.setCrystalSize(size_for_bunch)
            # This is very straight forward method (empilical function for robust 
            # search of helical crystals
            #self.search_radius_mm = math.sqrt(2.0)*((self.v_step+self.h_step)/2.0)
            print "Distance threshold = ",self.search_radius_mm
        else:
            # set the threshold of distance (Empirical value)
            if self.v_step > self.h_step:
                step_mm=self.v_step
            else:
                step_mm=self.h_step

            size_for_bunch=2.0*step_mm
            self.setCrystalSize(size_for_bunch)
            print "Distance threshold = ",self.search_radius_mm

        # If this scan is vertical or horizontal scan
        #   vertical scan: size_for_bunch should be set to 2.0 * vertical scan step
        # horizontal scan: size_for_bunch should be set to 2.0 * horizontal scan step
        if self.v_step==0.0:
            size_for_bunch=2.0*self.h_step
            self.setCrystalSize(size_for_bunch)
        elif self.h_step==0.0:
            size_for_bunch=2.0*self.v_step
            self.setCrystalSize(size_for_bunch)

        # Max score component
        crystal_list=[]
        while(1):
            cry_indices=[]
            print "\n\n"
            h_max,v_max,maxindex,maxvalue=self.getMaxScoreIndex(check_map)
            print "self.getMaxScoreIndex(H,V)=",h_max,v_max
            good_list=self.process_pixel(check_map,kdtree_map,kdtree,maxindex)
            if len(good_list)!=0:
                cry_indices+=good_list
            else:
                print "Process finished"
                break
            print "The first good_list=",good_list
            cycle_list=[]
            while(1):
                cycle_list=self.process_cycle(check_map,kdtree_map,kdtree,good_list)
                print "The next good_list=",cycle_list
                if len(cycle_list)!=0:
                    cry_indices+=cycle_list
                    good_list=cycle_list
                else:
                    break
            crystal_list.append(cry_indices)

        print "Number of found crystal=",len(crystal_list)

        # Logging
        logf=open("log_%f.dat"%size_for_bunch,"w")
        crystal_array=[]
        for crystal in crystal_list:
            logf.write("\n\n")
            # Making the Crystal class for storing good XYZ coordinates
            each_crystal=Crystal.Crystal(self.h_step,self.v_step)
            # Adding all XYZs to crystal
            for target_index in crystal:
                print "Target index=",target_index
                h_index,v_index=self.conv1Dto2D(target_index)
                # The pixel which has the maximum score 
                junk0,junk1,tx,ty,tz,score=original_map[v_index,h_index,:]
                each_crystal.addGrid(tx,ty,tz,h_index,v_index,score)
                #logf.write("%8.3f %8.3f %8.3f\n"%(tx,ty,tz))
                logf.write("%8.3f %8.3f %8.3f %5d %5d %5d\n"%(tx,ty,tz,v_index,h_index,score))
            crystal_array.append(each_crystal)
            logf.write( "\n\n")

        for each_crystal in crystal_array:
            each_crystal.printAll()

        return crystal_array

    def process_cycle(self,check_map,kdtree_map,kdtree,target_indices):
        cycle_list=[]
        for new_core in target_indices:
            good_list=self.process_pixel(check_map,kdtree_map,kdtree,new_core)
            cycle_list+=good_list
        return cycle_list

    def process_pixel(self,check_map,kdtree_map,kdtree,target_index):
        h_index,v_index=self.conv1Dto2D(target_index)
        # The pixel which has the maximum score 
        junk0,junk1,tx,ty,tz,score=check_map[v_index,h_index,:]
        # List up neighboring grids on a heat map
        neighbor_indices=kdtree.query_ball_point((tx,ty,tz),self.search_radius_mm)
        print "KDtree query ball points: target=",target_index,h_index,v_index
        print neighbor_indices
        print "KDtree query ball points"
        print kdtree_map[neighbor_indices]
        good_list=[]

        print "SEARCHING GOOD neigbor to ",h_index,v_index
        # Get the score from neighbor grids of the maximum grid
        for i in neighbor_indices:
            v_index=i/self.nh
            h_index=i%self.nh
            check_score=check_map[v_index,h_index,5]
            # If the score is already 0
            if check_score==0 or check_score==-1:
                continue
            # If the score is not 0 : good grids
            else:
                # score of checked grid is set to -1
                check_map[v_index,h_index,5]=-1
                # Get XYZ coordinates
                tmpxyz=check_map[v_index,h_index,:]
                # good_list of index 
                good_list.append(i)
                print "GOOD: %8.3f %8.3f %8.3f %5d %5d"%(tmpxyz[2],tmpxyz[3],tmpxyz[4],check_score,i)
        return good_list

    # Shape of the check_map (self.nv x self.nh)
    def getMaxScoreIndex(self,check_map):
        print "getMaxScoreIndex: check_map shape=",check_map.shape
        print "#### max #####"
        # slicing the column of the score
        # and get the maximum value and its index
        value = numpy.amax(check_map[:,:,-1])
        index = numpy.argmax(check_map[:,:,-1])
        print "getMaxScoreIndex.INDEX,MaxValue=",index,value

        h_index,v_index=self.conv1Dto2D(index)
        
        return h_index,v_index,index,value

    def conv1Dto2D(self,index):
        # index of the good group
        v_index=index/self.nh
        # index of the corresponding line
        h_index=index%self.nh

        if self.debug:
            print "conv1Dto2D: self.nh,h_index,v_index",self.nh,h_index,v_index
        
        return h_index,v_index

    def getCorners(self,prefix,kind="n_spots"):
        self.min_score=0.0
        self.reProcess(prefix,kind)
        
        # corner coordinate
        ymin=xmin=9999.9999
        ymax=xmax=-9999.9999

        # All of grids in this scan will be analyzed
        for i in numpy.arange(0,len(self.score_good)):
            x1,y1,score1,imgnum1=self.score_good[i]
            if x1 <= xmin:
                xmin=x1
            if x1 > xmax:
                xmax=x1
            if y1 <= ymin:
                ymin=y1
            if y1 > ymax:
                ymax=y1
        # L: Left   U: Down
        # R: Right  D: Up
        lu=(xmin,ymax)
        ld=(xmin,ymin)
        ru=(xmax,ymax)
        rd=(xmax,ymin)

        return lu,ld,ru,rd

    def getMaxScore(self,prefix,kind="n_spots"):
        self.min_score=0.0
        self.reProcess(prefix,kind)

        # All of grids in this scan will be analyzed
        max_score=-9999.9999
        for i in numpy.arange(0,len(self.score_good)):
            x1,y1,score1,imgnum=self.score_good[i]
            if score1 > max_score:
                max_score=score1
        return max_score

    def getMaxScoreImageNum(self,prefix,kind="n_spots"):
        self.min_score=0.0
        self.reProcess(prefix,kind)

        # All of grids in this scan will be analyzed
        max_score=-9999.9999
        i_max=-99999
        for i in numpy.arange(0,len(self.score_good)):
            x1,y1,score1,imgnum=self.score_good[i]
            if score1 > max_score:
                max_score=score1
                i_max=imgnum
        return i_max,max_score

    def getTotalScore(self,prefix,kind="n_spots"):
        print "AnaSHIKA.getTotalScore starts"
        self.min_score=0.0
        self.reProcess(prefix,kind)
        total_score=0

        # All of grids in this scan will be analyzed
        max_score=-9999.9999
        print "SCORE_GOOD len=",len(self.score_good)
        for i in numpy.arange(0,len(self.score_good)):
                x1,y1,score1,imgnum=self.score_good[i]
        total_score+=score1

        print "AnaSHIKA.getTotalScore ends"

        return total_score

    def getGravCenter(self,prefix,kind="n_spots"):
        self.min_score=0.0
        self.reProcess(prefix,kind)

        # All of grids in this scan will be analyzed
        sum_score=0.0
        sum_x_score=0.0
        sum_y_score=0.0
        for i in numpy.arange(0,len(self.score_good)):
            x1,y1,score1,imgnum1=self.score_good[i]
            sum_score+=score1
            sum_x_score+=x1*score1
            sum_y_score+=y1*score1

        grav_x=sum_x_score/sum_score
        grav_y=sum_y_score/sum_score

        return (grav_x,grav_y)

    def getTargetCorner(self,lu,ld,ru,rd,grav_xy):
        def calcDistance(code1,code2):
            x1,y1=code1
            x2,y2=code2
            dx=x1-x2
            dy=y1-y2
            dist=math.sqrt(dx*dx+dy*dy)
            return dist

        print "GRAV",grav_xy

        smallest_dist=999.999
        co="none"
        for co_name,corner in zip(["LU","LD","RU","RD"],[lu,ld,ru,rd]):
            tmp_dist=calcDistance(grav_xy,corner)
            if tmp_dist < smallest_dist:
                smallest_dist=tmp_dist
                co=co_name
                print smallest_dist,co_name
        print "Gravity center is near by ",co
        if co == "LU":
            target_corner=rd
        if co == "LD":
            target_corner=ru
        if co == "RU":
            target_corner=ld
        if co == "RD":
            target_corner=lu
        return target_corner

    def findNearestGrid(self,thresh_score,prefix,target_corner,raster_path,kind="n_spots"):
        def calcDistance(code1,code2):
            x1,y1=code1
            x2,y2=code2
            dx=x1-x2
            dy=y1-y2
            dist=math.sqrt(dx*dx+dy*dy)
            return dist

        # Picking grids above thresh_score
        self.min_score=thresh_score
        self.reProcess(prefix,kind)

        print "LENGTH of GOOD SCORES=",len(self.score_good)
        if len(self.score_good)==0:
                        raise MyException.MyException("findNearestGrid: No good grids.")

                # All of grids in this scan will be analyzed
        shortest_dist=9999.9999
        for i in numpy.arange(0,len(self.score_good)):
            x1,y1,score1,imgnum=self.score_good[i]
            curr_xy=x1,y1
            tmp_dist=calcDistance(curr_xy,target_corner)
            print "Checked and distance",x1,y1,tmp_dist
            if tmp_dist < shortest_dist:
                real_x=x1
                real_y=y1
                real_i=imgnum
                shortest_dist=tmp_dist

                x,y,z=self.cen_xyz
                crycode=CrystalSpot.CrystalSpot(x,y,z,self.phi)
        crycode.setDiffscanLog(raster_path)
        fx,fy,fz=crycode.getXYZ(real_i)

        print "findNearestGrid:",fx,fy,fz
        return fx,fy,fz

    def make2Dmap(self):
        # step x
        self.step_x=self.x[0]-self.x[1]
        # step y
        for tmpy in self.y:
            print tmpy
        print self.step_x
        nx=numpy.array(self.x)
        minx=nx.min()
        maxx=nx.max()
        stepx=maxx-minx
        print minx,maxx

        ny=numpy.array(self.y)
        miny=ny.min()
        maxy=ny.max()
        stepy=maxy-miny
        print miny,maxy

        print stepx,stepy

    def calcDist(self,x1,y1,x2,y2):
        dx=numpy.fabs(x1-x2)
        dy=numpy.fabs(y1-y2)
        dist=numpy.sqrt(dx*dx+dy*dy)
        return dist

    def trees(self):
        xy_array=[]
        for data in self.score_good:
            x,y,s,imgnum=data
            xy_array.append((x,y))
            print "data number=",len(self.score_good)
            rlp3d=numpy.array(xy_array)

            # Making the tree for all RLPs
            self.tree=ss.cKDTree(rlp3d)

            tlist=[]
            # Grouping near reflection list
            for rlp in rlp3d: # For all of independent reflections
                proclist=[]
                dist,idx=self.tree.query(
                    rlp,k=300,p=1,distance_upper_bound=0.011)
            # Bunch of processing
            print "RLP=",rlp
            print "DIST=",dist
            print "INDX=",idx
            for (d,i) in zip(dist,idx):
                    if d==float('inf'):
                            break
                    else:
                            proclist.append(i)
            tlist.append(proclist)

        print "##############################"
        for t in tlist:
            for i in t:
                print rlp3d[i]
            print "END"

    def aroundTargetPix(self):
        tmp_list=[]
        for j in self.score_good:
            x1,y1,score1=j
            print x1,y1

    def setThresh(self,threshold):
        self.min_score=threshold

    def setMinMax(self,min_score,max_score):
        self.min_score=min_score
        self.max_score=max_score

    def ana1Dscan(self,prefix):
        heatmap=self.prep(prefix)
        print heatmap.shape

if __name__=="__main__":

    cxyz=(0.7379,   -11.5623,    -0.0629)
    phi=0.0
    prefix="xi-KLaT006-12"
    scan_path=sys.argv[1]

    ahm=AnaHeatmap(scan_path,cxyz,phi)

    min_score=int(sys.argv[2])
    max_score=int(sys.argv[3])

    # Multi crystal 
    #cry_size=float(sys.argv[2])
    #ahm.setMinMax(min_score,max_score)
    #ahm.searchMulti(cry_size)
    # Multi crystal 

    # Helical crystal
    #cry_size=float(sys.argv[2])
    ahm.setMinMax(min_score,max_score)
    crystal_array=ahm.searchPixelBunch(True)
    #for cry in crystal_array:
        #cry.printAll()
        #print cry.getTotalScore(),cry.getRoughEdges(),cry.getCryHsize()

    #ahm.ana1Dscan(prefix)
    #def getBestCrystalCode(self,option="gravity"):
