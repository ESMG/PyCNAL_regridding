# this example aims at showing ability of ESMF to regrid on ROMS grid

import os
import ESMF
from brushcutter import fill_msg_grid as fill
import matplotlib.pylab as plt
import numpy as np

# This call enables debug logging
ESMF.Manager(debug=True)

# Use example provided with ESMPy
srcdir = '/Users/raphael/tmp_install/esmf/src/addon/ESMPy/examples/data/'
srcgrid = srcdir + 'so_Omon_GISS-E2.nc'

# CCS grid is available here :
# http://oceanus.esm.rutgers.edu:8080/thredds/catalog/ROMS/CCS/Run01/Inputs/catalog.html

romsdir  = '/Users/raphael/STORAGE/ROMS/GRIDS/'
romsgrid = romsdir + 'CCS_7k_0-360_fred_grd.nc'

# Create source grid
grid1 = ESMF.Grid(filename=srcgrid,
                  filetype=ESMF.FileFormat.GRIDSPEC)

# Create the roms grid
grid2 = ESMF.Grid(filename=romsgrid,
                  filetype=ESMF.FileFormat.GRIDSPEC,
                  coord_names=["lon_rho", "lat_rho"])

# Create a field on the centers of the grid
field1 = ESMF.Field(grid1, staggerloc=ESMF.StaggerLoc.CENTER)

# Read a field from the file
field1.read(filename=srcgrid, variable="so")

# example field is not right (somebody does not know that greenwich is not in the middle 
# of the pacific...)
dataorig = field1.data.copy()
data_correct = dataorig.copy()
data_correct[0:180,:] = dataorig[180:,:]
data_correct[180:,:] = dataorig[0:180,:]

# perform manually land extrapolation using our land extrapolation
xmsg = field1.data.max()
guess = 1
gtype = 1
nscan = 1500             # usually much less than this
epsx  = 1.e-2            # variable dependent
relc  = 0.6              # relaxation coefficient
output = fill.mod_poisson.poisxy1(data_correct, xmsg, guess, gtype, nscan, epsx, relc)

# replace value in ESMF field object
field1.data[:] = output

# alternative : use original (not land extrapolated)
#field1.data[:] = data_correct

# Create a field on the centers of the grid
field2 = ESMF.Field(grid2, staggerloc=ESMF.StaggerLoc.CENTER)

# Set up a regridding object between source and destination
regridme = ESMF.Regrid(field1, field2, 
                        regrid_method=ESMF.RegridMethod.BILINEAR)

field2 = regridme(field1, field2)

# plot the original and interpolated fields
lonin  = field1.grid.coords[0][0]
latin  = field1.grid.coords[0][1]

dataout = field2.data.copy()
lonout  = field2.grid.coords[0][0]
latout  = field2.grid.coords[0][1]

plt.figure() 
plt.contourf(lonin,latin,data_correct,np.arange(30,40,0.05)) 
plt.colorbar() 
plt.title('Original field (SSS) at right location')

plt.figure() 
plt.contourf(lonin,latin,data_correct,np.arange(30,37,0.05)) 
plt.axis([220,250,20,50]) 
plt.colorbar() 
plt.title('Original field (SSS) at right location (zoom CCS)')

plt.figure()
plt.contourf(lonout,latout,dataout,np.arange(30,37,0.05))
plt.colorbar()
plt.title('Interpolated field onto CCS domain')

plt.show()
