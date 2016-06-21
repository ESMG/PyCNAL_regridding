import numpy as np

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

	def __init__(self,segment_name,**kwargs):
		''' constructor 
		needs segment_name and named arguments as described in class doc 
		create attributes for all given kwargs and add them to the items list
		'''
		self.segment_name = segment_name
		self.items = []
		self.items.append('segment_name')
		# iterate over all kwargs and store them as attributes for the object
		if kwargs is not None:
			self.__dict__.update(kwargs)
        		for key, value in kwargs.iteritems():
				self.items.append(key)
		# compute dimensions
		self.nx = self.imax - self.imin + 1	
		self.ny = self.jmax - self.jmin + 1	
		self.nz = self.nvertical
		
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
        		for key, value in kwargs.iteritems():
				self.items.append(key)

		if self.geometry == 'line':
			self.dimensions_name = ('time','ny_' + self.segment_name,'nx_' + self.segment_name,)
		elif self.geometry == 'surface':
			self.dimensions_name = ('time','nvertical','ny_' + self.segment_name,'nx_' + self.segment_name,)
		return None

	def print_all(self):
		''' print all variable (debug) '''
		for item in self.items:
			exec('print item , self.' + str(item) )
		return None


	def allocate(self):
		self.data = np.empty(self.nz,self.ny,self.nx)

		return None

		
