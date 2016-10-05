import numpy as np
import ESMF
from brushcutter import lib_ioncdf as ncdf
from brushcutter import fill_msg_grid as fill
from brushcutter import mod_utils as modu
import matplotlib.pylab as plt

class obc_vectvariable():
	''' A class describing an open boundary condition vector variable
	on an obc_segment '''

	def __init__(self,segment,variable_name_u,variable_name_v,**kwargs):
		''' constructor of obc_variable : import from segment and adds attributes
		specific to this variable

		*** args :

		* segment : existing obc_segment object

		* variable_name_u : name of the zonal component in output file

		* variable_name_v : name of the meridional component in output file
		
		*** kwargs (mandatory) :

		* geometry : shape of the output field (line, surface)

		* obctype : radiation, flather,...

		'''

		self.vector = True
		# read args 
		self.variable_name_u = variable_name_u
		self.variable_name_v = variable_name_v
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
			self.dimensions_name_u = ('time','ny_' + self.segment_name,'nx_' + self.segment_name,)
			self.dimensions_name_v = ('time','ny_' + self.segment_name,'nx_' + self.segment_name,)
		elif self.geometry == 'surface':
			self.dimensions_name_u = ('time','nz_' + self.segment_name + '_' + self.variable_name_u, \
			'ny_' + self.segment_name,'nx_' + self.segment_name,)
			self.dimensions_name_v = ('time','nz_' + self.segment_name + '_' + self.variable_name_v, \
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
			data = np.empty((self.nz,self.ny,self.nx))
		elif self.geometry == 'line':
			data = np.empty((self.ny,self.nx))
		return data

	def set_constant_value(self,value_u,value_v,depth_vector=None):
		''' Set constant value to field '''
		if depth_vector is not None:
			self.depth_dz_from_vector(depth_vector)
		self.data_u_out = self.allocate()
		self.data_v_out = self.allocate()
		self.data_u_out[:] = value_u
		self.data_v_out[:] = value_v
		return None
		
	def interpolate_from(self,filename,variable_u,variable_v,frame=None,drown=True,maskfile=None,maskvar=None, \
	                     missing_value=None,use_locstream=False,from_global=True,depthname='z', \
	                     timename='time'):
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
		datasrc_u = ncdf.read_field(filename,variable_u,frame=frame)
		datasrc_v = ncdf.read_field(filename,variable_v,frame=frame)
		try:
			self.timesrc = ncdf.read_time(filename,timename,frame=frame)
		except:
			print('input data time variable not read')
		if self.geometry == 'surface':
			self.depth, self.nz, self.dz = ncdf.read_vert_coord(filename,depthname,self.nx,self.ny)

		# TODO !! make rotation to east,north from source grid.

		# 2. perform extrapolation over land
		if drown is True:
			dataextrap_u = self.perform_extrapolation(datasrc_u,maskfile,maskvar,missing_value)
			dataextrap_v = self.perform_extrapolation(datasrc_v,maskfile,maskvar,missing_value)
		else:
			dataextrap_u = datasrc_u.copy()
			dataextrap_v = datasrc_v.copy()
		# 3. ESMF interpolation
		# Create source grid
		gridsrc = ESMF.Grid(filename=filename,filetype=ESMF.FileFormat.GRIDSPEC,is_sphere=from_global)
		self.gridsrc = gridsrc
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

		self.data_u = self.perform_interpolation(dataextrap_u,regridme,field_src,field_target,use_locstream)
		self.data_v = self.perform_interpolation(dataextrap_v,regridme,field_src,field_target,use_locstream)

		# vector rotation to output grid
		self.data_u_out = np.empty((self.nz,self.ny,self.nx))
		self.data_v_out = np.empty((self.nz,self.ny,self.nx))
		axis= [1,1,0]
                self.data_u_out, self.data_v_out = modu.mod_utils.vector_rotation(axis,self.angle_dx,self.data_u,self.data_v)

#               python prototype euler-rodrigues
#		for kz in np.arange(self.nz):
#			for ky in np.arange(self.ny):
#				for kx in np.arange(self.nx):
#					self.data_u_out[kz,ky,kx], self.data_v_out[kz,ky,kx], dummy = np.dot(self.rotation_matrix(axis,self.angle_dx[ky,kx]), [self.data_u[kz,ky,kx],self.data_v[kz,ky,kx],0])
		#print(np.dot(rotation_matrix(axis,theta), v))

                # what everybody else does and is wrong !
		if self.buggedvelocities:
			self.data_u_out = self.data_u * np.cos(self.angle_dx) - \
			                  self.data_v * np.sin(self.angle_dx)
			self.data_v_out = self.data_v * np.cos(self.angle_dx) + \
			                  self.data_u * np.sin(self.angle_dx) 
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
			plt.figure() ; plt.contourf(mask[0,:,:],[0.99,1.01]) ; plt.colorbar() ; plt.title('land sea mask')
		return mask

	def perform_extrapolation(self,datasrc,maskfile,maskvar,missing_value):
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
			datasrc_plt = np.ma.masked_values(datasrc,self.xmsg)
			plt.figure() ; plt.contourf(datasrc_plt[0,:,:],40) ; plt.title('original') ; plt.colorbar() 
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
			for kz in np.arange(self.nz):
				tmpin = data[kz,:,:].transpose()
				if self.debug and kz == 0:
					tmpin_plt = np.ma.masked_values(tmpin,self.xmsg)
					plt.figure() ; plt.contourf(tmpin_plt.transpose(),40) ; plt.colorbar() ; 
					plt.title('normalized before drown')
				tmpout = fill.mod_poisson.poisxy1(tmpin,self.xmsg, self.guess, self.gtype, \
				self.nscan, self.epsx, self.relc)
				data[kz,:,:] = tmpout.transpose()
				if self.debug and kz == 0:
					plt.figure() ; plt.contourf(tmpout.transpose(),40) ; plt.colorbar() ; 
					plt.title('normalized after drown') 
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

	def perform_interpolation(self,dataextrap,regridme,field_src,field_target,use_locstream):
		data = self.allocate()
		if self.geometry == 'surface':
			for kz in np.arange(self.nz):
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
						data_target_plt = np.ma.masked_values(data[kz,:,:],self.xmsg)
						#data_target_plt = np.ma.masked_values(field_target.data,self.xmsg)
						plt.figure() ; plt.contourf(data_target_plt[:,:],40) ; plt.colorbar() ; 
						plt.title('regridded') ; plt.show()
		elif self.geometry == 'line':
			field_src.data[:] = dataextrap[:,:].transpose()
			field_target = regridme(field_src, field_target)
			if use_locstream:
				# TODO check
				data[:,:] = field_target.data.transpose()
			else:
				data[:,:] = field_target.data.transpose()[self.jmin:self.jmax+1,self.imin:self.imax+1]
		return data

	def depth_dz_from_vector(self,depth_vector):
		self.nz = depth_vector.shape[0]
		self.depth = np.empty((self.nz,self.ny,self.nx))
		for ky in np.arange(self.ny):
			for kx in np.arange(self.nx):
				self.depth[:,ky,kx] = depth_vector
		# compute layer thickness
		self.dz = np.empty((self.nz,self.ny,self.nx))
		self.dz[:-1,:,:] = self.depth[1:,:,:] - self.depth[:-1,:,:]
		# test if bounds exist first (to do), else
		self.dz[-1,:,:] = self.dz[-2,:,:]
		return None

	def rotation_matrix(self,axis, theta):
		"""
		Return the rotation matrix associated with counterclockwise rotation about
		the given axis by theta radians.
		"""
		axis = np.asarray(axis)
		axis = axis/np.sqrt(np.dot(axis, axis))
		a = np.cos(theta/2.0)
		b, c, d = -axis*np.sin(theta/2.0)
		aa, bb, cc, dd = a*a, b*b, c*c, d*d
		bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
		out = np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
		[2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
		[2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])
		return out

