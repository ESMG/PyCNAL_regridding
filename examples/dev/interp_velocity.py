from brushcutter import lib_obc_segments as los
from brushcutter import lib_obc_vectvariable as losv
from brushcutter import lib_timemanager as ltim
from brushcutter import lib_ioncdf as ncdf
import numpy as np
import matplotlib.pylab as plt

infile = 'uniform_zonal.nc'
momgrd = '/Volumes/P4/workdir/raphael/work_brushcutter/ocean_hgrid_v2.nc'

# ---------- define segments on MOM grid -----------------------
domain = los.obc_segment('domain',momgrd,imin=0,imax=360,jmin=0,  jmax=960)

# ---------- define variables on each segment ------------------
vel_domain    = losv.obc_vectvariable(domain,'u','v',geometry='surface',obctype='radiation',debug=False)
velice_domain = losv.obc_vectvariable(domain,'uice','vice',geometry='line',obctype='radiation',debug=False)

#depths = np.array([0.,100.,200.])
#vel_domain.set_constant_value(1.,0.,depth_vector = depths)
velice_domain.set_constant_value(3.,4.)

vel_domain.interpolate_from('./uniform_zonal.nc','u','v',frame=0,depthname='st_ocean',use_locstream=False,from_global=True)

# ---------- list segments and variables to be written -------
list_segments = [domain]

list_variables = []
list_vectvariables = [vel_domain,velice_domain]

#----------- time --------------------------------------------
time = ltim.timeobject()

# ---------- write to file -----------------------------------
ncdf.write_obc_file(list_segments,list_variables,list_vectvariables,time,output='interpolated_vel.nc')

plt.figure()
plt.quiver(vel_domain.lon[::40,::40],vel_domain.lat[::40,::40],vel_domain.data_u_out[0,::40,::40],vel_domain.data_v_out[0,::40,::40])
plt.title('zonal flow in CCS coordinates')
plt.show()
