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


	# define time and coordinates
	nctime = fid.createVariable('time','f8',('time',))

	ncsegments_lon = []
	ncsegments_lat = []
	for segment in list_segments:
		ncseg_lon = fid.createVariable('lon_' + segment.segment_name, 'f8', segment.hdimensions_name)
		ncseg_lat = fid.createVariable('lat_' + segment.segment_name, 'f8', segment.hdimensions_name)
		ncsegments_lon.append(ncseg_lon)
		ncsegments_lat.append(ncseg_lat)

	# define variables
	ncvariables = []
	ncvariables_vc = []
	for variable in list_variables:
		ncvar = fid.createVariable(variable.variable_name + '_' + variable.segment_name, 'f8', variable.dimensions_name)
		ncvariables.append(ncvar)
		if variable.geometry == 'surface':
			ncvar_vc = fid.createVariable('vc_' + variable.variable_name + '_' + variable.segment_name, 'f8', \
			variable.dimensions_name)
			ncvariables_vc.append(ncvar_vc)


	# fill time and coordinates
	nctime[:] = 0. # to fix

	for nseg in np.arange(len(list_segments)):
		ncsegments_lon[nseg][0,:] = list_segments[nseg].lon
		ncsegments_lat[nseg][0,:] = list_segments[nseg].lat

	# fill variables
	for nvar in np.arange(len(list_variables)):
		ncvariables[nvar][0,:] = list_variables[nvar].data
		if list_variables[nvar].geometry == 'surface':
			ncvariables_vc[nvar][0,:] = list_variables[nvar].depth # rename to vc

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
		
