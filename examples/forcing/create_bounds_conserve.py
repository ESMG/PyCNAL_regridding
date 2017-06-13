import netCDF4 as nc
import sys
import numpy as np

filein = sys.argv[1]
fileout = filein.replace('.nc','_conserve.nc')

# read from original mask
fidin = nc.Dataset(lsmin, 'r')
lon = fidin.variables['lon'][:]
lat = fidin.variables['lat'][:]
fidin.close()

# compute the bounds
nx = lon.shape[0] ; ny = lat.shape[0]
lon_bnds = 9999 * np.ones((nx,2))
lat_bnds = 9999 * np.ones((ny,2))

lon_extended = np.zeros((nx+2))
lon_extended[1:-1] = lon.copy()
lon_extended[0] = lon[-1] - 360.  # periodic
lon_extended[-1] = 360 + lon[0]   # periodic

lat_extended = np.zeros((ny+2))
lat_extended[1:-1] = lat.copy()
lat_extended[0] = max(-90. , lat[0] - (lat[1]-lat[0]))
lat_extended[-1] = min(90. , lat[-1] + (lat[-1]-lat[-2]))

lon_bnds[:,0] = 0.5*lon_extended[0:-2]+0.5*lon_extended[1:-1] # lower bound
lon_bnds[:,1] = 0.5*lon_extended[1:-1]+0.5*lon_extended[2:]   # upper bound

lat_bnds[:,0] = 0.5*lat_extended[0:-2]+0.5*lat_extended[1:-1] # lower bound
lat_bnds[:,1] = 0.5*lat_extended[1:-1]+0.5*lat_extended[2:]   # upper bound

# create mask for conservative remapping
fid = nc.Dataset(fileout, 'w', format='NETCDF3_CLASSIC')
fid.description = 'lsm conservative remap'
# dimensions
fid.createDimension('lat', ny)
fid.createDimension('lon', nx)
fid.createDimension('bounds', 2)
# variables
latitudes  = fid.createVariable('lat', 'f8', ('lat',))
longitudes = fid.createVariable('lon', 'f8', ('lon',))
latitudes_bounds  = fid.createVariable('lat_bnds', 'f8', ('lat','bounds'))
longitudes_bounds = fid.createVariable('lon_bnds', 'f8', ('lon','bounds'))
# attributes
latitudes.units = 'degrees_north'
latitudes.long_name = 'latitude'
latitudes.bounds = 'lat_bnds'
longitudes.units = 'degrees_east'
longitudes.long_name = 'longitude'
longitudes.bounds = 'lon_bnds'
# data
latitudes[:]    = lat
longitudes[:]   = lon
latitudes_bounds[:,:] = lat_bnds
longitudes_bounds[:,:] = lon_bnds
# close
fid.close()
