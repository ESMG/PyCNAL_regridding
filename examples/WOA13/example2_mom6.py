from brushcutter import lib_obc_segments as los
from brushcutter import lib_obc_variable as lov
from brushcutter import lib_ioncdf as ncdf

woatemp = '../data/temp_WOA13-CM2.1_monthly_ccs.nc'
woasalt = '../data/salt_WOA13-CM2.1_monthly_ccs.nc'
momgrd = '../data/ocean_hgrid_v2.nc'

# ---------- define segments on MOM grid -----------------------
south = los.obc_segment('segment_001', momgrd,istart=0,iend=360,jstart=0,  jend=0  )
north = los.obc_segment('segment_002', momgrd,istart=0,iend=360,jstart=960,jend=960)
west  = los.obc_segment('segment_003', momgrd,istart=0,iend=0,  jstart=0,  jend=960)

# ---------- define variables on each segment ------------------
temp_south = lov.obc_variable(south,'temp',geometry='surface',obctype='radiation',use_locstream=True)
temp_north = lov.obc_variable(north,'temp',geometry='surface',obctype='radiation',use_locstream=True)
temp_west  = lov.obc_variable(west, 'temp',geometry='surface',obctype='radiation',use_locstream=True)

salt_south = lov.obc_variable(south,'salt',geometry='surface',obctype='radiation',use_locstream=True)
salt_north = lov.obc_variable(north,'salt',geometry='surface',obctype='radiation',use_locstream=True)
salt_west  = lov.obc_variable(west, 'salt',geometry='surface',obctype='radiation',use_locstream=True)

zeta_south = lov.obc_variable(south,'zeta',geometry='line',obctype='flather')
zeta_north = lov.obc_variable(north,'zeta',geometry='line',obctype='flather')
zeta_west  = lov.obc_variable(west ,'zeta',geometry='line',obctype='flather')

# ---------- interpolate T/S from WOA monthly file, frame = 0 (jan) and using locstream (x2 speedup)
temp_south.interpolate_from( woatemp,'temp',frame=0,depthname='st_ocean',from_global=False,coord_names=['geolon_t','geolat_t'])
temp_north.interpolate_from( woatemp,'temp',frame=0,depthname='st_ocean',from_global=False,coord_names=['geolon_t','geolat_t'])
temp_west.interpolate_from(  woatemp,'temp',frame=0,depthname='st_ocean',from_global=False,coord_names=['geolon_t','geolat_t'])

salt_south.interpolate_from( woasalt,'salt',frame=0,depthname='st_ocean',from_global=False,coord_names=['geolon_t','geolat_t'])
salt_north.interpolate_from( woasalt,'salt',frame=0,depthname='st_ocean',from_global=False,coord_names=['geolon_t','geolat_t'])
salt_west.interpolate_from(  woasalt,'salt',frame=0,depthname='st_ocean',from_global=False,coord_names=['geolon_t','geolat_t'])

# ---------- set constant value for SSH ----------------------
zeta_south.set_constant_value(0.0)
zeta_north.set_constant_value(0.0)
zeta_west.set_constant_value(0.0)

# ---------- list segments and variables to be written -------
list_segments = [north,south,west]

list_variables = [temp_south,temp_north,temp_west, \
                  salt_south,salt_north,salt_west, \
                  zeta_south,zeta_north,zeta_west ]

list_vectvariables = []

#----------- time --------------------------------------------
time = temp_south.timesrc

# ---------- write to file -----------------------------------
ncdf.write_obc_file(list_segments,list_variables,list_vectvariables,time,output='obc_woa13_m01_from_regional.nc')
