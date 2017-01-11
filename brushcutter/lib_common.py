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

	ny,nx = lon_src.shape

	lon_bl_tgt = target_grid.coords[0][0][0,0] ; lat_bl_tgt = target_grid.coords[0][1][0,0] # bottom left
	lon_br_tgt = target_grid.coords[0][0][-1,0] ; lat_br_tgt = target_grid.coords[0][1][-1,0] # bottom right
	lon_ul_tgt = target_grid.coords[0][0][0,-1] ; lat_ul_tgt = target_grid.coords[0][1][0,-1] # upper left
	lon_ur_tgt = target_grid.coords[0][0][-1,-1] ; lat_ur_tgt = target_grid.coords[0][1][-1,-1] # upper right
	
	dist_2_bottom_left_corner = distance_on_unit_sphere(lon_bl_tgt,lat_bl_tgt,lon_src,lat_src)
	j_bl_src, i_bl_src = _np.unravel_index(dist_2_bottom_left_corner.argmin(),dist_2_bottom_left_corner.shape)

	dist_2_bottom_right_corner = distance_on_unit_sphere(lon_br_tgt,lat_br_tgt,lon_src,lat_src)
	j_br_src, i_br_src = _np.unravel_index(dist_2_bottom_right_corner.argmin(),dist_2_bottom_right_corner.shape)

	dist_2_upper_left_corner = distance_on_unit_sphere(lon_ul_tgt,lat_ul_tgt,lon_src,lat_src)
	j_ul_src, i_ul_src = _np.unravel_index(dist_2_upper_left_corner.argmin(),dist_2_upper_left_corner.shape)

	dist_2_upper_right_corner = distance_on_unit_sphere(lon_ur_tgt,lat_ur_tgt,lon_src,lat_src)
	j_ur_src, i_ur_src = _np.unravel_index(dist_2_upper_right_corner.argmin(),dist_2_upper_right_corner.shape)

	imin = min(i_bl_src,i_ul_src) ; imax = max(i_br_src,i_ur_src)
	jmin = min(j_bl_src,j_br_src) ; jmax = max(j_ul_src,j_ur_src)

	# for safety
	imin = max(imin-2,0)
	jmin = max(jmin-2,0)
	imax = min(imax+2,nx)
	jmax = min(jmax+2,ny)

	print('Subset source grid : full dimension is ', nx , ny, ' subset is ', imin, imax, jmin, jmax)

	return imin, imax, jmin, jmax

