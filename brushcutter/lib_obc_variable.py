import numpy as _np
import ESMF as _ESMF
from brushcutter import lib_ioncdf as _ncdf
from brushcutter import fill_msg_grid as _fill
import matplotlib.pylab as _plt

class obc_variable():
	''' A class describing an open boundary condition variable
	on an obc_segment '''

	def __init__(self,segment,variable_name,**kwargs):
		''' constructor of obc_variable : import from segment and adds attributes
		specific to this variable

		*** args :

		* segment : existing obc_segment object

		* variable_name : name of the variable in output file
		
		*** kwargs (mandatory) :

		* geometry : shape of the output field (line, surface)

		* obctype : radiation, flather,...

		'''

		self.vector = False
		# read args 
		self.variable_name = variable_name
		self.items = []
		self.items.append('variable_name')
		# iterate over all attributes of segment and copy them 
		self.__dict__.update(segment.__dict__)
		# iterate over all kwargs and store them as attributes for the object
		if kwargs is not None:
			self.__dict__.update(kwargs)
			for key, value in kwargs.items():
				self.items.append(key)

		# boundary geometry
		if self.geometry == 'line':
			self.dimensions_name = ('time','ny_' + self.segment_name,'nx_' + self.segment_name,)
		elif self.geometry == 'surface':
			self.dimensions_name = ('time','nz_' + self.segment_name + '_' + self.variable_name, \
			'ny_' + self.segment_name,'nx_' + self.segment_name,)


		# default parameters for land extrapolation
		# can be modified by changing the attribute of object
		self.xmsg = -99
		self.guess = 1                # guess = 1 zonal mean
		self.gtype = 1                # cyclic or not
		self.nscan = 1500             # usually much less than this
		self.epsx  = 1.e-4            # variable dependent / not with reduced var
		self.relc  = 0.6              # relaxation coefficient
		return None

	def allocate(self):
		''' Allocate the output array '''
		if self.geometry == 'surface':
			data = _np.empty((self.nz,self.ny,self.nx))
		elif self.geometry == 'line':
			data = _np.empty((self.ny,self.nx))
		return data

	def depth_dz_from_vector(self,depth_vector):
		self.nz = depth_vector.shape[0]
		self.depth = _np.empty((self.nz,self.ny,self.nx))
		for ky in _np.arange(self.ny):
			for kx in _np.arange(self.nx):
				self.depth[:,ky,kx] = depth_vector
		# compute layer thickness
		self.dz = _np.empty((self.nz,self.ny,self.nx))
		self.dz[:-1,:,:] = self.depth[1:,:,:] - self.depth[:-1,:,:]
		# test if bounds exist first (to do), else
		self.dz[-1,:,:] = self.dz[-2,:,:]
		return None

	def set_constant_value(self,value,depth_vector=None):
		''' Set constant value to field '''
		if depth_vector is not None:
			self.depth_dz_from_vector(depth_vector)
		self.data = self.allocate()
		self.data[:] = value

		return None

	def set_vertical_profile(self,top_value,bottom_value,shape='linear',depth_vector=None):
		''' create a vertical profile '''
		if depth_vector is not None:
			self.depth_dz_from_vector(depth_vector)
		self.data = self.allocate()
		if shape == 'linear':
			slope = ( top_value - bottom_value) / (depth_vector[0] - depth_vector[-1])
			for kz in _np.arange(self.nz):
				self.data[kz,:,:] = bottom_value + slope * (depth_vector[kz] - depth_vector[-1])

		return None

	def set_horizontal_shear(self,value_1,value_n,shape='linear',direction='x',depth_vector=None):
		if depth_vector is not None:
			self.depth_dz_from_vector(depth_vector)
		self.data = self.allocate()
		if shape == 'linear':
			if direction == 'x':
				dx = (value_n - value_1) / self.nx
				if depth_vector is not None:
					for kz in _np.arange(self.nz):
						for ky in _np.arange(self.ny):
							self.data[kz,ky,:] = _np.arange(value_1,value_n,dx)
				else:
					for ky in _np.arange(self.ny):
						self.data[ky,:] = _np.arange(value_1,value_n,dx)
			if direction == 'y':
				dy = (value_n - value_1) / self.ny
				if depth_vector is not None:
					for kz in _np.arange(self.nz):
						for kx in _np.arange(self.nx):
							self.data[kz,:,kx] = _np.arange(value_1,value_n,dy)
				else:
					for kx in _np.arange(self.nx):
						self.data[:,kx] = _np.arange(value_1,value_n,dy)

		return None

	def interpolate_from(self,filename,variable,frame=None,drown=True,maskfile=None,maskvar=None, \
	                     missing_value=None,use_locstream=False,from_global=True,depthname='z', \
	                     timename='time',coord_names=['lon','lat'],method='bilinear'):
		''' interpolate_from performs a serie of operation :
		* read input data
		* perform extrapolation over land if desired
			* read or create mask if extrapolation
		* call ESMF for regridding
		
		Optional arguments (=default) :

		* frame=None : time record from input data (e.g. 1,2,..,12) when input file contains more than one record.
		* drown=True : perform extrapolation of ocean values onto land
		* maskfile=None : to read mask from a file (else uses missing value of variable)
		* maskvar=None : if maskfile is defined, we need to provide name of mask array in maskfile
		* missing_value=None : when missing value attribute not defined in input file, this allows to pass it
		* use_locstream=False : interpolate from ESMF grid to ESMF locstream instead of ESMF grid, a bit faster.
		                        use only to interpolate to boundary.
		* from_global=True : if input file is global leave to true. If input is regional, set to False.
		                     interpolating from a regional extraction can significantly speed up processing.
		'''
		# 1. read the original field
		datasrc = _ncdf.read_field(filename,variable,frame=frame)
		try:
			self.timesrc = _ncdf.read_time(filename,timename,frame=frame)
		except:
			print('input data time variable not read')
		if self.geometry == 'surface':
			self.depth, self.nz, self.dz = _ncdf.read_vert_coord(filename,depthname,self.nx,self.ny)
		# 2. perform extrapolation over land
		if drown is True:
			dataextrap = self.perform_extrapolation(datasrc,maskfile,maskvar,missing_value)
		else:
			dataextrap = datasrc.copy()
		# 3. ESMF interpolation
		# Create source grid
		gridsrc = _ESMF.Grid(filename=filename,filetype=_ESMF.FileFormat.GRIDSPEC,is_sphere=from_global,coord_names=coord_names)
		self.gridsrc = gridsrc
		# Create a field on the centers of the grid
		field_src = _ESMF.Field(gridsrc, staggerloc=_ESMF.StaggerLoc.CENTER)
		# Create a field on the centers of the grid
		if use_locstream:
			field_target = _ESMF.Field(self.locstream_target)
		else:
			field_target = _ESMF.Field(self.grid_target, staggerloc=_ESMF.StaggerLoc.CENTER)
		# Set up a regridding object between source and destination
		if method == 'bilinear':
			regridme = _ESMF.Regrid(field_src, field_target,
			                        regrid_method=_ESMF.RegridMethod.BILINEAR)
		elif method == 'patch':
			regridme = _ESMF.Regrid(field_src, field_target,
			                        regrid_method=_ESMF.RegridMethod.PATCH)

		self.data = self.perform_interpolation(dataextrap,regridme,field_src,field_target,use_locstream)
		return None
		
	def compute_mask_from_missing_value(self,data,missing_value=None):
		''' compute mask from missing value :
		* first try to get the mask assuming our data is a np.ma.array.
		Well-written netcdf files with missing_value of _FillValue attributes
		are translated into a np.ma.array
		* else use provided missing value to create mask '''
		try:
			logicalmask = data.mask
			mask = _np.ones(logicalmask.shape)
			mask[_np.where(logicalmask == True)] = 0
		except:
			if missing_value is not None:
				mask = _np.ones(data.shape)
				mask[_np.where(data == missing_value)] = 0
			else:
				exit('Cannot create mask, please provide a missing_value, or maskfile')
		if self.debug:
			_plt.figure() ; _plt.contourf(mask[0,:,:],[0.99,1.01]) ; _plt.colorbar() ; _plt.title('land sea mask')
		return mask

	def perform_extrapolation(self,datasrc,maskfile,maskvar,missing_value):
		# 2.1 read mask or compute it
		if maskfile is not None:
			mask = _ncdf.read_field(maskfile,maskvar)
		else:
			mask = self.compute_mask_from_missing_value(datasrc,missing_value=missing_value)
		# 2.2 mask the source data
		datasrc[_np.where(mask == 0)] = self.xmsg
		datamin = datasrc[_np.where(mask == 1)].min()
		datamax = datasrc[_np.where(mask == 1)].max()
		if self.debug:
			datasrc_plt = _np.ma.masked_values(datasrc,self.xmsg)
			_plt.figure() ; _plt.contourf(datasrc_plt[0,:,:],40) ; _plt.title('original') ; _plt.colorbar() 
		# 2.3 perform land extrapolation on reduced variable
		datanorm = self.normalize(datasrc,datamin,datamax,mask)
		if self.debug:
			print(datanorm.min() , datanorm.max(), datamin, datamax)
		datanormextrap = self.drown_field(datanorm)
		dataextrap = self.unnormalize(datanormextrap,datamin,datamax)
		return dataextrap


	def drown_field(self,data):
		''' drown_field is a wrapper around the fortran code fill_msg_grid.
		depending on the output geometry, applies land extrapolation on 1 or N levels'''
		if self.geometry == 'surface':
			for kz in _np.arange(self.nz):
				tmpin = data[kz,:,:].transpose()
				if self.debug and kz == 0:
					tmpin_plt = _np.ma.masked_values(tmpin,self.xmsg)
					_plt.figure() ; _plt.contourf(tmpin_plt.transpose(),40) ; _plt.colorbar() ; 
					_plt.title('normalized before drown')
				tmpout = _fill.mod_poisson.poisxy1(tmpin,self.xmsg, self.guess, self.gtype, \
				self.nscan, self.epsx, self.relc)
				data[kz,:,:] = tmpout.transpose()
				if self.debug and kz == 0:
					_plt.figure() ; _plt.contourf(tmpout.transpose(),40) ; _plt.colorbar() ; 
					_plt.title('normalized after drown') 
		elif self.geometry == 'line':
			tmpin = data[:,:].transpose()
			tmpout = _fill.mod_poisson.poisxy1(tmpin,self.xmsg, self.guess, self.gtype, \
			self.nscan, self.epsx, self.relc)
			data[:,:] = tmpout.transpose()
		return data

	def normalize(self,data,datamin,datamax,mask):
		''' create a reduced variable to perform better drown '''
		datanorm = ( data -datamin) / (datamax - datamin)
		datanorm[_np.where( mask == 0 )] = self.xmsg
		return datanorm

	def unnormalize(self,datanorm,datamin,datamax):
		''' return back to original range of values '''
		data = datamin + datanorm * (datamax - datamin)
		return data

	def perform_interpolation(self,dataextrap,regridme,field_src,field_target,use_locstream):
		data = self.allocate()
		if self.geometry == 'surface':
			for kz in _np.arange(self.nz):
				field_src.data[:] = dataextrap[kz,:,:].transpose()
				field_target = regridme(field_src, field_target)
				if use_locstream:
					if self.nx == 1:
						data[kz,:,0] = field_target.data.copy()
					elif self.ny == 1:
						data[kz,0,:] = field_target.data.copy()
				else:
					data[kz,:,:] = field_target.data.transpose()[self.jmin:self.jmax+1, \
					                                             self.imin:self.imax+1]
					if self.debug and kz == 0:
						data_target_plt = _np.ma.masked_values(self.data[0,:,:],self.xmsg)
						#data_target_plt = _np.ma.masked_values(field_target.data,self.xmsg)
						_plt.figure() ; _plt.contourf(data_target_plt[:,:],40) ; _plt.colorbar() ; 
						_plt.title('regridded') ; plt.show()
		elif self.geometry == 'line':
			field_src.data[:] = dataextrap[:,:].transpose()
			field_target = regridme(field_src, field_target)
			if use_locstream:
				data[:,:] = _np.reshape(field_target.data.transpose(),(self.ny,self.nx))
			else:
				data[:,:] = field_target.data.transpose()[self.jmin:self.jmax+1,self.imin:self.imax+1]
		return data

