from brushcutter import lib_obc_segments as los
from brushcutter import lib_obc_variable as lov
from brushcutter import lib_ioncdf as ncdf
from brushcutter import lib_timemanager as ltim
import numpy as np
import sys
import ConfigParser

# this example demonstrate how to make analytical obc

# ---------- path to grid and WOA T/S data ---------------------
# read information in files.path file for user given in arg

this_user = sys.argv[-1]
config = ConfigParser.ConfigParser()
config.read('files.path')
try:
	for item in config.options(this_user):
		exec(item + ' = config.get(this_user,item)')
except:
	exit('Please provide the id from files.path you want to use')

momgrd = 'ocean_hgrid_v2.nc'

# ---------- define segments on MOM grid -----------------------
south = los.obc_segment('segment_001',momdir + momgrd,imin=0,imax=360,jmin=0,  jmax=0  )
north = los.obc_segment('segment_002',momdir + momgrd,imin=0,imax=360,jmin=960,jmax=960)
west  = los.obc_segment('segment_003',momdir + momgrd,imin=0,imax=0,  jmin=0,  jmax=960)

# ---------- define variables on each segment ------------------
temp_south = lov.obc_variable(south,'temp',geometry='surface',obctype='radiation')
temp_north = lov.obc_variable(north,'temp',geometry='surface',obctype='radiation')
temp_west  = lov.obc_variable(west, 'temp',geometry='surface',obctype='radiation')

salt_south = lov.obc_variable(south,'salt',geometry='surface',obctype='radiation')
salt_north = lov.obc_variable(north,'salt',geometry='surface',obctype='radiation')
salt_west  = lov.obc_variable(west, 'salt',geometry='surface',obctype='radiation')

u_south = lov.obc_variable(south,'u',geometry='surface',obctype='radiation')
u_north = lov.obc_variable(north,'u',geometry='surface',obctype='radiation')
u_west  = lov.obc_variable(west, 'u',geometry='surface',obctype='radiation')

v_south = lov.obc_variable(south,'v',geometry='surface',obctype='radiation')
v_north = lov.obc_variable(north,'v',geometry='surface',obctype='radiation')
v_west  = lov.obc_variable(west, 'v',geometry='surface',obctype='radiation')

zeta_south = lov.obc_variable(south,'zeta',geometry='line',obctype='flather')
zeta_north = lov.obc_variable(north,'zeta',geometry='line',obctype='flather')
zeta_west  = lov.obc_variable(west ,'zeta',geometry='line',obctype='flather')

# ---------- define vertical axis (here from WOA, but could be anything)
depth_woa = np.array([5, 15, 25, 35, 45, 55, 65, 75, 85, 95, 105, 115, 125, 135, 145, 
                      155, 165, 175, 185, 195, 205, 215, 225, 236.122817993164, 
                      250.599975585938, 270.620819091797, 298.304931640625, 335.675628662109, 
                      384.63427734375, 446.936645507812, 524.170593261719, 617.736328125, 
                      728.828491210938, 858.421508789062, 1007.25708007812, 1175.83483886719, 
                      1364.40625, 1572.97131347656, 1801.27868652344, 2048.82861328125, 
                      2314.87915039062, 2598.45629882812, 2898.365234375, 3213.20581054688, 
                      3541.38989257812, 3881.162109375, 4230.62060546875, 4587.74267578125, 
                      4950.40869140625, 5316.4287109375]) 

# ---------- set linear stratification for T, constant value for S
temp_south.set_vertical_profile(30.,2.,shape='linear',depth_vector=depth_woa)
temp_north.set_vertical_profile(30.,2.,shape='linear',depth_vector=depth_woa)
temp_west.set_vertical_profile(30.,2.,shape='linear',depth_vector=depth_woa)

salt_south.set_constant_value(35., depth_vector=depth_woa)
salt_north.set_constant_value(35., depth_vector=depth_woa)
salt_west.set_constant_value(35., depth_vector=depth_woa)

# ---------- set constant value for SSH ----------------------
zeta_south.set_constant_value(0.0)
zeta_north.set_constant_value(0.0)
zeta_west.set_constant_value(0.0)

# --------- set velocity profile ---------------

u_south.set_constant_value(0.0, depth_vector=depth_woa)
u_north.set_constant_value(0.0, depth_vector=depth_woa)
u_west.set_horizontal_shear(-1.0,0.0,shape='linear', direction='y',depth_vector=depth_woa)

v_south.set_horizontal_shear(-1.0,1.0,shape='linear', direction='x', depth_vector=depth_woa)
v_north.set_horizontal_shear(0.0,1.0, shape='linear', direction='x', depth_vector=depth_woa)
v_west.set_constant_value(0.0, depth_vector=depth_woa)

# ---------- list segments and variables to be written -------
list_segments = [north,south,west]

list_variables = [temp_south ,temp_north,temp_west, \
                  salt_south,salt_north,salt_west, \
                  zeta_south,zeta_north,zeta_west, \
                  u_south,u_north,u_west, \
                  v_south,v_north,v_west ]

#----------- time --------------------------------------------
time = ltim.timeobject()

# ---------- write to file -----------------------------------
ncdf.write_obc_file(list_segments,list_variables,time,output='obc_analytical.nc')
