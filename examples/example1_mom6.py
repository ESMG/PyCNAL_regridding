from brushcutter import lib_obc_segments as los
from brushcutter import lib_ioncdf as ncdf

#cp ocean_hgrid.nc ocean_hgrid_v2.nc
#ncatted -a units,y,m,c,degree_north ocean_hgrid_v2.nc
#ncatted -a units,x,m,c,degree_east ocean_hgrid_v2.nc

woadir = '/Users/raphael/STORAGE/WOA13/'
momgrd = '/Users/raphael/STORAGE/MOM6/ocean_hgrid_v2.nc'

south = los.obc_segment('segment_01',momgrd,imin=1,imax=100,jmin=1,jmax=1,nvertical=33)
north = los.obc_segment('segment_02',momgrd,imin=1,imax=100,jmin=400,jmax=400,nvertical=33)


zeta_south = los.obc_variable(south,'zeta',geometry='line',obctype='flather')
temp_south = los.obc_variable(south,'temp',geometry='surface',obctype='radiation')
temp_north = los.obc_variable(north,'temp',geometry='surface',obctype='radiation',debug=True)

no3_north = los.obc_variable(north,'no3',geometry='surface',obctype='radiation')

# original file with correct _FillValue attributes
temp_south.interpolate_from(woadir + 'temp_WOA13-CM2.1_monthly.nc','temp',frame=0)
temp_north.interpolate_from(woadir + 'temp_WOA13-CM2.1_monthly.nc','temp',frame=0)
zeta_south.set_constant_value(0.1)
no3_north.set_constant_value(0.1)

list_segments = [north,south]
list_variables = [temp_south,temp_north,zeta_south,no3_north]

ncdf.write_obc_file(list_segments,list_variables)
