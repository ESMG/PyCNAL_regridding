from brushcutter import lib_obc_segments as los
from brushcutter import lib_ioncdf as ncdf

# make sure ocean_hgrid has GRIDSPEC compliant units, here :
#cp ocean_hgrid.nc ocean_hgrid_v2.nc
#ncatted -a units,y,m,c,degree_north ocean_hgrid_v2.nc
#ncatted -a units,x,m,c,degree_east ocean_hgrid_v2.nc

# ---------- path to grid and WOA T/S data ---------------------
woadir = '/Users/raphael/STORAGE/WOA13/'
woatemp = 'temp_WOA13-CM2.1_monthly.nc'
woasalt = 'salt_WOA13-CM2.1_monthly.nc'
momgrd = '/Users/raphael/STORAGE/MOM6/ocean_hgrid_v2.nc'

# ---------- define segments on MOM grid -----------------------
domain = los.obc_segment('segment_001',momgrd,imin=0,imax=360,jmin=0,  jmax=960,  nvertical=33)

# ---------- define variables on each segment ------------------
temp_domain = los.obc_variable(domain,'temp',geometry='surface',obctype='radiation',debug=True)

#salt_domain = los.obc_variable(domain,'salt',geometry='surface',obctype='radiation')

#zeta_south = los.obc_variable(south,'zeta',geometry='line',obctype='flather')
#zeta_north = los.obc_variable(north,'zeta',geometry='line',obctype='flather')
#zeta_west  = los.obc_variable(west ,'zeta',geometry='line',obctype='flather')

# ---------- interpolate T/S from WOA monthly file, frame = 0 (jan) and using locstream (x2 speedup)
temp_domain.interpolate_from(woadir + woatemp,'temp',frame=0,use_locstream=False,from_global=True)

#salt_domain.interpolate_from(woadir + woasalt,'salt',frame=0,use_locstream=True)

# ---------- set constant value for SSH ----------------------
#zeta_south.set_constant_value(0.0)
#zeta_north.set_constant_value(0.0)
#zeta_west.set_constant_value(0.0)

# ---------- list segments and variables to be written -------
list_segments = [domain]

list_variables = [temp_domain] 

# ---------- write to file -----------------------------------
ncdf.write_obc_file(list_segments,list_variables,output='clim_woa13_m01_from_global.nc')
