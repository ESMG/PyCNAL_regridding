import netCDF4 as nc
import numpy as np

def write_obc_file(list_segments,list_variables,output='out.nc'):
	''' write an open boundary condition file from a list
	of segments and associated variables '''

	# open file in write mode
	fid = nc.Dataset(output, 'w', format='NETCDF3_CLASSIC')
	fid.description = ''

	# define the list of dimensions we need to write
	fid.createDimension('time', None)
	
        # dimensions
	for segment in list_segments:
		fid.createDimension('nx_' + segment.segment_name, segment.nx)
		fid.createDimension('ny_' + segment.segment_name, segment.ny)
	for variable in list_variables:
		if (variable.geometry == 'surface'):
			fid.createDimension('nz_' + variable.segment_name + '_' + variable.variable_name, variable.nz)

	ncvariables = []
	lon_ncvariables = []
	lat_ncvariables = []

	# grid/time variables
	nctime = fid.createVariable('time','f8',('time',))

	# variables
	for variable in list_variables:
		ncvar = fid.createVariable(variable.variable_name + '_' + variable.segment_name, 'f8', variable.dimensions_name)
		lon_ncvar = fid.createVariable('lon_' + variable.variable_name + '_' + variable.segment_name, 'f8', variable.hdimensions_name)
		lat_ncvar = fid.createVariable('lat_' + variable.variable_name + '_' + variable.segment_name, 'f8', variable.hdimensions_name)
		ncvariables.append(ncvar)
		lon_ncvariables.append(lon_ncvar)
		lat_ncvariables.append(lat_ncvar)


	nctime[:] = 0.

	for nvar in np.arange(len(list_variables)):
		ncvariables[nvar][0,:] = list_variables[nvar].data
		lon_ncvariables[nvar][0,:] = list_variables[nvar].lon
		lat_ncvariables[nvar][0,:] = list_variables[nvar].lat

	# close file
	fid.close()

def read_field(file_name,variable_name,frame=None):
	fid = nc.Dataset(file_name,'r')
	if frame is not None:
		out = fid.variables[variable_name][frame,:].squeeze()
	else:
		out = fid.variables[variable_name][:].squeeze()
	fid.close()
	return out
		
