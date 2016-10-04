import netCDF4 as nc
import numpy as np 

# we create some velocity on the same grid as CM2.1
indir = '/Volumes/P4/workdir/raphael/work_brushcutter/'
fcm = 'temp_WOA13-CM2.1_monthly.nc'

# read stuff from input WOA
fidin = nc.Dataset(indir+fcm,'r')
lon = fidin.variables['geolon_t'][:]
lat = fidin.variables['geolat_t'][:]
temp = fidin.variables['temp'][:][0,:,:,:]
st_ocean = fidin.variables['st_ocean'][:]
fidin.close()

u = np.empty((50,200,360))
v = np.empty((50,200,360))
for kz in np.arange(len(st_ocean)):
	u[kz,:,:] = 1.0
	v[kz,:,:] = 0.0

u[np.where(temp.mask == True)] = 1.0e+15
v[np.where(temp.mask == True)] = 1.0e+15

fidout = nc.Dataset('uniform_zonal.nc','w',format='NETCDF3_CLASSIC')
fidout.createDimension('time', None)
fidout.createDimension('x',360)
fidout.createDimension('y',200)
fidout.createDimension('st_ocean',50)

olon   = fidout.createVariable('geolon_t','f8',('y','x',))
olat   = fidout.createVariable('geolat_t','f8',('y','x',))
ost    = fidout.createVariable('st_ocean','f8',('st_ocean',))
otime  = fidout.createVariable('time','f8',('time',))
ou     = fidout.createVariable('u','f4',('time','st_ocean','y','x',),fill_value=1.0e+15)
ov     = fidout.createVariable('v','f4',('time','st_ocean','y','x',),fill_value=1.0e+15)

otime.units = 'days since 1900-01-01 0:00:00'
olon.units = 'degrees_east'
olat.units = 'degrees_north'

olon[:] = lon
olat[:] = lat
ost[:]  = st_ocean
otime[:] = 0.
ou[0,:] = u
ov[0,:] = v

fidout.close()


