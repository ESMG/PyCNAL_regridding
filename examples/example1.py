from brushcutter import lib_obc_segments as los
from brushcutter import lib_ioncdf as ncdf

woadir = '/Users/raphael/STORAGE/WOA13/'

south = los.obc_segment('segment_01',imin=1,imax=100,jmin=1,jmax=1,nvertical=33)
north = los.obc_segment('segment_02',imin=1,imax=100,jmin=100,jmax=100,nvertical=33)


zeta_south = los.obc_variable(south,'zeta',geometry='line',obctype='flather')
temp_south = los.obc_variable(south,'temp',geometry='surface',obctype='radiation')
temp_north = los.obc_variable(north,'temp',geometry='surface',obctype='radiation',debug=True)

# original file with correct _FillValue attributes
temp_north.interpolate_from(woadir + 'temp_WOA13-CM2.1_monthly.nc','temp',frame=0)
# modified file to break attributes
temp_north.interpolate_from(woadir + 'temp_WOA13-CM2.1_monthly_nomiss.nc','temp',frame=0,missing_value=-1.0e+20)

list_segments = [north,south]
list_variables = [zeta_south,temp_south,temp_north]

ncdf.write_obc_file(list_segments,list_variables)
