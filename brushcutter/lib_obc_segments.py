import numpy as np
import ESMF
from brushcutter import lib_ioncdf as ncdf
from brushcutter import fill_msg_grid as fill
import matplotlib.pylab as plt

class obc_segment():
	''' A class describing a MOM open boundary condtion segment
	takes as argument : 
	* segment_name = name of the given segment
	* kwargs (named arguments) : 
	imin = along x axis, where the segment begins
	imax = along x axis, where the segment ends
	jmin = along y axis, where the segment begins
	jmax = along y axis, where the segment end
	OPTIONAL :
	nvertical = number of vertical levels
	'''

	def __init__(self,segment_name,target_grid_file,target_model='MOM6',**kwargs):
		''' constructor 
		needs segment_name and named arguments as described in class doc 
		create attributes for all given kwargs and add them to the items list
		'''
		self.segment_name = segment_name
		self.target_grid_file = target_grid_file
		self.items = []
		self.items.append('segment_name')
		self.items.append('target_grid')
		self.debug = False
		# iterate over all kwargs and store them as attributes for the object
		if kwargs is not None:
			self.__dict__.update(kwargs)
        		for key, value in kwargs.items():
				self.items.append(key)
		# compute dimensions
		self.nx = self.imax - self.imin + 1	
		self.ny = self.jmax - self.jmin + 1	
		self.nz = self.nvertical

		if target_model == 'MOM6':
			coord_names=["x", "y"]
		elif target_model == 'ROMS':
			coord_names=["lon_rho", "lat_rho"]

		self.grid_target = ESMF.Grid(filename=target_grid_file,filetype=ESMF.FileFormat.GRIDSPEC,
		                             coord_names=coord_names) 

		self.locstream_target = ESMF.LocStream(self.nx * self.ny, coord_sys=ESMF.CoordSys.SPH_DEG)
		self.locstream_target["ESMF:Lon"] = self.grid_target.coords[0][0][self.imin:self.imax+1,self.jmin:self.jmax+1].squeeze()
		self.locstream_target["ESMF:Lat"] = self.grid_target.coords[0][1][self.imin:self.imax+1,self.jmin:self.jmax+1].squeeze()
		
		return None

class obc_variable():
	''' A class describing a MOM open boundary condition variable
	takes as argument : 
	* a segment object of class obc_segment
	* variable_name = name of the given variable
	* kwargs (named arguments) :
	'''

	def __init__(self,segment,variable_name,**kwargs):
		''' constructor
		create attributes for all given kwargs and attributes of input segment
		'''
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
			self.dimensions_name = ('time','nvertical','ny_' + self.segment_name,'nx_' + self.segment_name,)

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
			self.data = np.empty((self.nz,self.ny,self.nx))
		elif self.geometry == 'line':
			self.data = np.empty((self.ny,self.nx))
		return None

	def set_constant_value(self,value):
		''' Set constant value to field '''
		self.allocate()
		self.data[:] = value
		return None
		
	def interpolate_from(self,filename,variable,frame=None,drown=True,maskfile=None,maskvar=None,missing_value=None,use_locstream=False):
		''' interpolate_from performs a serie of operation :
		* read input data
		* perform extrapolation over land if desired
			* read or create mask if extrapolation
		* call ESMF for regridding
		'''
		# 1. read the original field
		datasrc = ncdf.read_field(filename,variable,frame=frame)
		# 2. perform extrapolation over land
		if drown is True:
			# 2.1 read mask or compute it
			if maskfile is not None:
				mask = ncdf.read_field(maskfile,maskvar)
			else:
				mask = self.compute_mask_from_missing_value(datasrc,missing_value=missing_value)
			# 2.2 mask the source data
			datasrc[np.where(mask == 0)] = self.xmsg
			datamin = datasrc[np.where(mask == 1)].min()
			datamax = datasrc[np.where(mask == 1)].max()
			if self.debug:
				plt.figure() ; plt.contourf(datasrc[0,:,:]) ; plt.colorbar()
			# 2.3 perform land extrapolation on reduced variable
			datanorm = self.normalize(datasrc,datamin,datamax,mask)
			if self.debug:
				print(datanorm.min() , datanorm.max(), datamin, datamax)
			datanormextrap = self.drown_field(datanorm)
			dataextrap = self.unnormalize(datanormextrap,datamin,datamax)
		else:
			dataextrap = datasrc.copy()
		# 3. ESMF interpolation
		# Create source grid
		gridsrc = ESMF.Grid(filename=filename,filetype=ESMF.FileFormat.GRIDSPEC)
		# Create a field on the centers of the grid
		field_src = ESMF.Field(gridsrc, staggerloc=ESMF.StaggerLoc.CENTER)
		# Create a field on the centers of the grid
		if use_locstream:
			field_target = ESMF.Field(self.locstream_target)
		else:
			field_target = ESMF.Field(self.grid_target, staggerloc=ESMF.StaggerLoc.CENTER)
		# Set up a regridding object between source and destination
		regridme = ESMF.Regrid(field_src, field_target,
	                        regrid_method=ESMF.RegridMethod.BILINEAR)

		self.allocate()
		if self.geometry == 'surface':
			for kz in np.arange(self.nz):
				field_src.data[:] = dataextrap[kz,:,:].transpose()
				field_target = regridme(field_src, field_target)
				if use_locstream:
					if self.nx == 1:
						self.data[kz,:,0] = field_target.data.copy()
					elif self.ny == 1:
						self.data[kz,0,:] = field_target.data.copy()
				else:
					self.data[kz,:,:] = field_target.data.transpose()[self.jmin:self.jmax+1,self.imin:self.imax+1]
				if self.debug and kz == 0:
					plt.figure() ; plt.contourf(field_target.data) ; plt.colorbar() ; plt.show()
		elif self.geometry == 'line':
			field_src.data[:] = dataextrap[:,:].transpose()
			field_target = regridme(field_src, field_target)
			if use_locstream:
				# TODO check
				self.data[:,:] = field_target.data.transpose()
			else:
				self.data[:,:] = field_target.data.transpose()[self.jmin:self.jmax+1,self.imin:self.imax+1]
		
		return None

	def compute_mask_from_missing_value(self,data,missing_value=None):
		''' compute mask from missing value :
		* first try to get the mask assuming our data is a np.ma.array.
		Well-written netcdf files with missing_value of _FillValue attributes
		are translated into a np.ma.array
		* else use provided missing value to create mask '''
		try:
			logicalmask = data.mask
			mask = np.ones(logicalmask.shape)
			mask[np.where(logicalmask == True)] = 0
		except:
			if missing_value is not None:
				mask = np.ones(data.shape)
				mask[np.where(data == missing_value)] = 0
			else:
				exit('Cannot create mask, please provide a missing_value, or maskfile')
		if self.debug:
			plt.figure() ; plt.contourf(mask[0,:,:]) ; plt.colorbar()
		return mask

	def drown_field(self,data):
		''' drown_field is a wrapper around the fortran code fill_msg_grid.
		depending on the output geometry, applies land extrapolation on 1 or N levels'''
		if self.geometry == 'surface':
			for kz in np.arange(self.nz):
				tmpin = data[kz,:,:].transpose()
				if self.debug and kz == 0:
					plt.figure() ; plt.contourf(tmpin) ; plt.colorbar()
				tmpout = fill.mod_poisson.poisxy1(tmpin,self.xmsg, self.guess, self.gtype, \
				self.nscan, self.epsx, self.relc)
				data[kz,:,:] = tmpout.transpose()
				if self.debug and kz == 0:
					plt.figure() ; plt.contourf(tmpout) ; plt.colorbar() ; plt.show()
		elif self.geometry == 'line':
			tmpin = data[:,:].transpose()
			tmpout = fill.mod_poisson.poisxy1(tmpin,self.xmsg, self.guess, self.gtype, \
			self.nscan, self.epsx, self.relc)
			data[:,:] = tmpout.transpose()
		return data

	def normalize(self,data,datamin,datamax,mask):
		''' create a reduced variable to perform better drown '''
		datanorm = ( data -datamin) / (datamax - datamin)
		datanorm[np.where( mask == 0 )] = self.xmsg
		return datanorm

	def unnormalize(self,datanorm,datamin,datamax):
		''' return back to original range of values '''
		data = datamin + datanorm * (datamax - datamin)
		return data
