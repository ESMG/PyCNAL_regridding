from brushcutter import lib_obc_segments as los
from brushcutter import lib_ioncdf as ncdf

# make sure ocean_hgrid has GRIDSPEC compliant units, here :
#cp ocean_hgrid.nc ocean_hgrid_v2.nc
#ncatted -a units,y,m,c,degree_north ocean_hgrid_v2.nc
#ncatted -a units,x,m,c,degree_east ocean_hgrid_v2.nc

# ---------- path to grid and WOA T/S data ---------------------
woadir = '/Users/raphael/STORAGE/WOA13/'
woatemp = 'temp_WOA13-CM2.1_monthly_ccs.nc'
woasalt = 'salt_WOA13-CM2.1_monthly_ccs.nc'
momgrd = '/Users/raphael/STORAGE/MOM6/ocean_hgrid_v2.nc'

# ---------- define segments on MOM grid -----------------------
south = los.obc_segment('segment_001',momgrd,imin=0,imax=360,jmin=0,  jmax=0  )
north = los.obc_segment('segment_002',momgrd,imin=0,imax=360,jmin=960,jmax=960)
west  = los.obc_segment('segment_003',momgrd,imin=0,imax=0,  jmin=0,  jmax=960)

# ---------- define variables on each segment ------------------
temp_south = los.obc_variable(south,'temp',geometry='surface',obctype='radiation')
temp_north = los.obc_variable(north,'temp',geometry='surface',obctype='radiation')
temp_west  = los.obc_variable(west, 'temp',geometry='surface',obctype='radiation')

salt_south = los.obc_variable(south,'salt',geometry='surface',obctype='radiation')
salt_north = los.obc_variable(north,'salt',geometry='surface',obctype='radiation')
salt_west  = los.obc_variable(west, 'salt',geometry='surface',obctype='radiation')

zeta_south = los.obc_variable(south,'zeta',geometry='line',obctype='flather')
zeta_north = los.obc_variable(north,'zeta',geometry='line',obctype='flather')
zeta_west  = los.obc_variable(west ,'zeta',geometry='line',obctype='flather')

# ---------- interpolate T/S from WOA monthly file, frame = 0 (jan) and using locstream (x2 speedup)
temp_south.interpolate_from(woadir + woatemp,'temp',frame=0,depthname='st_ocean',use_locstream=True,from_global=False)
temp_north.interpolate_from(woadir + woatemp,'temp',frame=0,depthname='st_ocean',use_locstream=True,from_global=False)
temp_west.interpolate_from( woadir + woatemp,'temp',frame=0,depthname='st_ocean',use_locstream=True,from_global=False)

salt_south.interpolate_from(woadir + woasalt,'salt',frame=0,depthname='st_ocean',use_locstream=True,from_global=False)
salt_north.interpolate_from(woadir + woasalt,'salt',frame=0,depthname='st_ocean',use_locstream=True,from_global=False)
salt_west.interpolate_from( woadir + woasalt,'salt',frame=0,depthname='st_ocean',use_locstream=True,from_global=False)

# ---------- set constant value for SSH ----------------------
zeta_south.set_constant_value(0.0)
zeta_north.set_constant_value(0.0)
zeta_west.set_constant_value(0.0)

# ---------- list segments and variables to be written -------
list_segments = [north,south,west]

list_variables = [temp_south,temp_north,temp_west, \
                  salt_south,salt_north,salt_west, \
                  zeta_south,zeta_north,zeta_west ]

# ---------- write to file -----------------------------------
ncdf.write_obc_file(list_segments,list_variables,output='obc_woa13_m01_from_regional.nc')
