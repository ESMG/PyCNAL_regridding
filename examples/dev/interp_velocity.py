from brushcutter import lib_obc_segments as los
from brushcutter import lib_obc_vectvariable as losv
from brushcutter import lib_timemanager as ltim
from brushcutter import lib_ioncdf as ncdf
import numpy as np

infile = 'uniform_zonal.nc'
momgrd = '/Volumes/P4/workdir/raphael/work_brushcutter/ocean_hgrid_v2.nc'

# ---------- define segments on MOM grid -----------------------
domain = los.obc_segment('domain',momgrd,imin=0,imax=360,jmin=0,  jmax=960)

# ---------- define variables on each segment ------------------
vel_domain    = losv.obc_vectvariable(domain,'u','v',geometry='surface',obctype='radiation',debug=True)
velice_domain = losv.obc_vectvariable(domain,'uice','vice',geometry='line',obctype='radiation',debug=True)

depths = np.array([0.,100.,200.])
vel_domain.set_constant_value(1.,0.,depth_vector = depths)
velice_domain.set_constant_value(3.,4.)

# ---------- list segments and variables to be written -------
list_segments = [domain]

list_variables = []
list_vectvariables = [vel_domain,velice_domain]

#----------- time --------------------------------------------
time = ltim.timeobject()

# ---------- write to file -----------------------------------
ncdf.write_obc_file(list_segments,list_variables,list_vectvariables,time,output='interpolated_vel.nc')
