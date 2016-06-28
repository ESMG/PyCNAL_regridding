from brushcutter import lib_obc_segments as los
from brushcutter import lib_ioncdf as ncdf

woadir = '/Users/raphael/STORAGE/WOA13/'
romsgrd = '/Users/raphael/STORAGE/ROMS/GRIDS/CCS_7k_0-360_fred_grd.nc'

south = los.obc_segment('segment_01',romsgrd,imin=1,imax=100,jmin=1,jmax=1,nvertical=33)
north = los.obc_segment('segment_02',romsgrd,imin=1,imax=100,jmin=400,jmax=400,nvertical=33)


zeta_south = los.obc_variable(south,'zeta',geometry='line',obctype='flather')
temp_south = los.obc_variable(south,'temp',geometry='surface',obctype='radiation')
temp_north = los.obc_variable(north,'temp',geometry='surface',obctype='radiation')

no3_north = los.obc_variable(north,'no3',geometry='surface',obctype='radiation')

# original file with correct _FillValue attributes
temp_south.interpolate_from(woadir + 'temp_WOA13-CM2.1_monthly.nc','temp',frame=0)
temp_north.interpolate_from(woadir + 'temp_WOA13-CM2.1_monthly.nc','temp',frame=0)
zeta_south.set_constant_value(0.1)
no3_north.set_constant_value(0.1)

# modified file to break attributes
#temp_north.interpolate_from(woadir + 'temp_WOA13-CM2.1_monthly_nomiss.nc','temp',frame=0,missing_value=-1.0e+20)

list_segments = [north,south]
list_variables = [temp_south,temp_north,zeta_south,no3_north]

ncdf.write_obc_file(list_segments,list_variables)
