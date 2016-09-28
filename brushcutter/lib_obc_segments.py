import numpy as np
import ESMF
from brushcutter import lib_ioncdf as ncdf
from brushcutter import fill_msg_grid as fill
import matplotlib.pylab as plt

class obc_segment():
	''' A class describing an open boundary condtion segment
	'''

	def __init__(self,segment_name,target_grid_file,target_model='MOM6',**kwargs):
		''' constructor of obc_segment - read target grid and create associated 
		ESMF grid and locstream objects.

		*** Args : 

		* segment_name : name of the segment, MOM6 wants segment_001,... 
		                                      ROMS wants north, south,...

		* target_grid_file : full path to target grid file (e.g. ocean_hgrid.nc, roms_grd.nc)

		* target_model (default MOM6) : can be MOM6 or ROMS
	
		*** kwargs (mandatory) : 

		* imin : along x axis, where the segment begins

		* imax : along x axis, where the segment ends

		* jmin : along y axis, where the segment begins

		* jmax : along y axis, where the segment end

		'''

		# read args 
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

		self.ilist = np.empty((self.ny,self.nx))
		self.jlist = np.empty((self.ny,self.nx))

		for kx in np.arange(self.nx):
			self.jlist[:,kx] = np.arange(self.jmin,self.jmax+1) / 2.
		for ky in np.arange(self.ny):
			self.ilist[ky,:] = np.arange(self.imin,self.imax+1) / 2.

		# coordinate names depend on ocean model
		# MOM6 has all T,U,V points in one big grid, ROMS has in 3 separate ones.
		if target_model == 'MOM6':
			coord_names=["x", "y"]
			self.angle_dx = ncdf.read_field(target_grid_file,'angle_dx')
		elif target_model == 'ROMS':
			coord_names=["lon_rho", "lat_rho"]

		# import target grid into ESMF grid object
		self.grid_target = ESMF.Grid(filename=target_grid_file,filetype=ESMF.FileFormat.GRIDSPEC,
		                             coord_names=coord_names) 

		# import same target grid into ESMF locstream object
		self.locstream_target = ESMF.LocStream(self.nx * self.ny, coord_sys=ESMF.CoordSys.SPH_DEG)
		self.locstream_target["ESMF:Lon"] = self.grid_target.coords[0][0][self.imin:self.imax+1, \
		self.jmin:self.jmax+1].flatten()
		self.locstream_target["ESMF:Lat"] = self.grid_target.coords[0][1][self.imin:self.imax+1, \
		self.jmin:self.jmax+1].flatten()
		
		# save lon/lat on this segment
		self.lon = self.grid_target.coords[0][0][self.imin:self.imax+1,self.jmin:self.jmax+1].transpose().squeeze()
		self.lat = self.grid_target.coords[0][1][self.imin:self.imax+1,self.jmin:self.jmax+1].transpose().squeeze()
		# nc dimensions for horizontal coords
		self.hdimensions_name = ('ny_' + self.segment_name,'nx_' + self.segment_name,)

		return None

