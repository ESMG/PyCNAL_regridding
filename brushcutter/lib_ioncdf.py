import netCDF4 as nc
import numpy as np
from brushcutter import lib_timemanager as tim

def write_obc_file(list_segments,list_variables,time_point,output='out.nc'):
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
	nctime.units = time_point.units

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
	nctime[:] = time_point.data

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

def read_vert_coord(file_name,vc_name,nx,ny):
	''' read the vertical coordinate (vc) and reshape it if needed :
	vertical coordinate can be either a function of z or (x,y,z)
	'''
	vc_in = read_field(file_name,vc_name)
	nz = vc_in.shape[0]
	if len(vc_in.shape) == 1:
		vc = np.empty((nz,ny,nx))
		for kx in np.arange(nx):
			for ky in np.arange(ny):
				vc[:,ky,kx] = vc_in
	else:
		vc = vc_in
	return vc, nz

def read_time(file_name,time_name='time',frame=0):
	''' read time from the input file '''
	otime = tim.timeobject()
	fid = nc.Dataset(file_name,'r')
	otime.data = fid.variables[time_name][frame]
	otime.units = fid.variables[time_name].units
	fid.close()
	return otime


