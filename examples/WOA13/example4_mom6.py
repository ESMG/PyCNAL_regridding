from brushcutter import lib_obc_segments as los
from brushcutter import lib_obc_variable as lov
from brushcutter import lib_ioncdf as ncdf

woatemp = '../data/temp_WOA13-CM2.1_monthly_CCS.nc'
woasalt = '../data/salt_WOA13-CM2.1_monthly_CCS.nc'
momgrd = '../data/ocean_hgrid_v2.nc'

# ---------- define segments on MOM grid -----------------------
domain = los.obc_segment('segment_001', momgrd,imin=0,imax=360,jmin=0,  jmax=960)

# ---------- define variables on each segment ------------------
temp_domain = lov.obc_variable(domain,'temp',geometry='surface',obctype='radiation',debug=False)
salt_domain = lov.obc_variable(domain,'salt',geometry='surface',obctype='radiation')

# ---------- interpolate T/S from WOA monthly file, frame = 0 (jan) and using locstream (x2 speedup)
temp_domain.interpolate_from( woatemp,'temp',frame=0,depthname='st_ocean',use_locstream=False,from_global=False,coord_names=['geolon_t','geolat_t'])
salt_domain.interpolate_from( woasalt,'salt',frame=0,depthname='st_ocean',use_locstream=False,from_global=False,coord_names=['geolon_t','geolat_t'])

# ---------- list segments and variables to be written -------
list_segments = [domain]

list_variables = [temp_domain,salt_domain] 

list_vectvariables = []

#----------- time --------------------------------------------
time = temp_domain.timesrc

# ---------- write to file -----------------------------------
ncdf.write_obc_file(list_segments,list_variables,list_vectvariables,time,output='clim_woa13_m01_from_regional.nc')
