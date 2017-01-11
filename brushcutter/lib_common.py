import numpy as _np

def distance_on_unit_sphere(lat1, long1, lat2, long2):

	# Convert latitude and longitude to 
	# spherical coordinates in radians.
	degrees_to_radians = _np.pi/180.0
        
	# phi = 90 - latitude
	phi1 = (90.0 - lat1)*degrees_to_radians
	phi2 = (90.0 - lat2)*degrees_to_radians
        
	# theta = longitude
	theta1 = long1*degrees_to_radians
	theta2 = long2*degrees_to_radians
        
	# Compute spherical distance from spherical coordinates.
       
	# For two locations in spherical coordinates 
	# (1, theta, phi) and (1, theta, phi)
	# cosine( arc length ) = 
	#    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
	# distance = rho * arc length
    
	cos = (_np.sin(phi1)*_np.sin(phi2)*_np.cos(theta1 - theta2) + \
	_np.cos(phi1)*_np.cos(phi2))
	dist = _np.arccos( cos )

	return dist

def find_subset(target_grid,lon_src,lat_src):
	lon_min_tgt = target_grid.coords[0][0].min()
	lon_max_tgt = target_grid.coords[0][0].max()
	lat_min_tgt = target_grid.coords[0][1].min()
	lat_max_tgt = target_grid.coords[0][1].max()

	ny,nx = lon_src.shape

	dist_2_bottom_left_corner = distance_on_unit_sphere(lon_min_tgt,lat_min_tgt,lon_src,lat_src)
	jmin, imin = _np.unravel_index(dist_2_bottom_left_corner.argmin(),dist_2_bottom_left_corner.shape)
	
	dist_2_upper_right_corner = distance_on_unit_sphere(lon_max_tgt,lat_max_tgt,lon_src,lat_src)
	jmax, imax = _np.unravel_index(dist_2_upper_right_corner.argmin(), dist_2_upper_right_corner.shape)

	# for safety
	imin = max(imin-5,0)
	jmin = max(jmin-5,0)
	imax = min(imax+5,nx)
	jmax = min(jmax+5,ny)

	print('Subset source grid : full dimension is ', nx , ny, ' subset is ', imin, imax, jmin, jmax)

	return imin, imax, jmin, jmax

