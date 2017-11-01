from brushcutter import *
import numpy as np
import sys

merrafile=sys.argv[1]
#direxamples='/Volumes/P4/workdir/raphael/work_conserve_remap/'
#merrafile = direxamples + 'MERRA_rain_3hours_1980_2days_conserve.nc'
ncepgrd = '../data/' + 'lsm_CORE2_conserve.nc'

# ---------- define target NCEP/CORE2 grid -----------------------
domain = obc_segment('domain', ncepgrd,target_model='regular',istart=0,iend=191,jstart=0,  jend=93)

# ---------- define variables on each segment ------------------
rain_domain = obc_variable(domain,'rain',geometry='line')

# ---------- list segments and variables to be written -------
list_segments = [domain]
list_variables = [rain_domain] 
list_vectvariables = []

# ---------- conservative interpolation from MERRA file -------------------
interp_t2s_conserve = rain_domain.interpolate_from(merrafile,'rain',timename='rain_time',frame=0,coord_names=['lon','lat'],method='conserve',drown='no',use_gridspec=True)
lib_ioncdf.write_obc_file(list_segments,list_variables,list_vectvariables,rain_domain.timesrc,output='merra_rain_conserve_fr0000.nc')

for kt in np.arange(1,16):
	rain_domain.interpolate_from(merrafile,'rain',timename='rain_time',frame=kt,coord_names=['lon','lat'],method='conserve',drown='no',interpolator=interp_t2s_conserve,use_gridspec=True)
	lib_ioncdf.write_obc_file(list_segments,list_variables,list_vectvariables,rain_domain.timesrc,output='merra_rain_conserve_fr' + str(kt).zfill(4) + '.nc')
