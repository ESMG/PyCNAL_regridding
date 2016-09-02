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
domain = los.obc_segment('segment_001',momgrd,imin=0,imax=360,jmin=0,  jmax=960)

# ---------- define variables on each segment ------------------
temp_domain = los.obc_variable(domain,'temp',geometry='surface',obctype='radiation',debug=False)
salt_domain = los.obc_variable(domain,'salt',geometry='surface',obctype='radiation')

# ---------- interpolate T/S from WOA monthly file, frame = 0 (jan) and using locstream (x2 speedup)
temp_domain.interpolate_from(woadir + woatemp,'temp',frame=0,depthname='st_ocean',use_locstream=False,from_global=True)
salt_domain.interpolate_from(woadir + woasalt,'salt',frame=0,depthname='st_ocean',use_locstream=False,from_global=True)

# ---------- list segments and variables to be written -------
list_segments = [domain]

list_variables = [temp_domain,salt_domain] 

#----------- time --------------------------------------------
time = temp_domain.timesrc

# ---------- write to file -----------------------------------
ncdf.write_obc_file(list_segments,list_variables,time,output='clim_woa13_m01_from_global.nc')
