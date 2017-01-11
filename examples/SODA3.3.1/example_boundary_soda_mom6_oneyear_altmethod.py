from brushcutter import lib_obc_segments as los
from brushcutter import lib_obc_variable as lov
from brushcutter import lib_obc_vectvariable as losv
from brushcutter import lib_ioncdf as ncdf

import subprocess as sp
import time as ptime

dir_soda = '/Volumes/P1/Data/SODA/SODA_3.3.1/1980/'
cmd = 'ls ' + dir_soda + ' | grep nc '
list_soda_files = sp.check_output(cmd,shell=True).replace('\n',' ').split()

momgrd = '../data/ocean_hgrid_v2.nc'

diroutput = '/Volumes/P4/workdir/raphael/CCS1_MOM_bdry/'

# ---------- define segments on MOM grid -----------------------
Nx=360
Ny=960
north = los.obc_segment('segment_001',momgrd,istart=Nx,iend=0, jstart=Ny,jend=Ny)
west  = los.obc_segment('segment_002',momgrd,istart=0, iend=0, jstart=Ny,jend=0 )
south = los.obc_segment('segment_003',momgrd,istart=0, iend=Nx,jstart=0, jend=0 )
domain= los.obc_segment('domain',     momgrd,istart=0, iend=Nx,jstart=0, jend=Ny)

# ---------- define variables on each segment ------------------
temp_south = lov.obc_variable(south,'temp',geometry='surface',obctype='radiation')
temp_north = lov.obc_variable(north,'temp',geometry='surface',obctype='radiation')
temp_west  = lov.obc_variable(west, 'temp',geometry='surface',obctype='radiation')

salt_south = lov.obc_variable(south,'salt',geometry='surface',obctype='radiation')
salt_north = lov.obc_variable(north,'salt',geometry='surface',obctype='radiation')
salt_west  = lov.obc_variable(west, 'salt',geometry='surface',obctype='radiation')

zeta_south = lov.obc_variable(south,'zeta',geometry='line',obctype='flather')
zeta_north = lov.obc_variable(north,'zeta',geometry='line',obctype='flather')
zeta_west  = lov.obc_variable(west ,'zeta',geometry='line',obctype='flather')

vel_south  = losv.obc_vectvariable(south,'u','v',geometry='surface',obctype='radiation')
vel_north  = losv.obc_vectvariable(north,'u','v',geometry='surface',obctype='radiation')
vel_west   = losv.obc_vectvariable(west ,'u','v',geometry='surface',obctype='radiation')

temp_domain= lov.obc_variable(domain,'temp',geometry='surface',obctype='radiation')
salt_domain= lov.obc_variable(domain,'salt',geometry='surface',obctype='radiation')
zeta_domain= lov.obc_variable(domain,'zeta',geometry='line',obctype='flather')
vel_domain = losv.obc_vectvariable(domain ,'u','v',geometry='surface',obctype='radiation')

first_call=True

for filein in list_soda_files:
	start = ptime.time()
	sodafile = dir_soda + filein
	print('working on ' + sodafile)
	fileout= diroutput + filein.replace('.nc','_CCS1.nc')

	if first_call:
		interp_t2s = temp_domain.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',\
		coord_names=['xt_ocean','yt_ocean'])
	else:
		temp_domain.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',\
		coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s)
		
	temp_domain.extract_subset_into(temp_south)
	temp_domain.extract_subset_into(temp_north)
	temp_domain.extract_subset_into(temp_west)

	salt_domain.interpolate_from(sodafile,'salt',frame=0,depthname='st_ocean',\
	coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s)

	salt_domain.extract_subset_into(salt_south)
	salt_domain.extract_subset_into(salt_north)
	salt_domain.extract_subset_into(salt_west)

	zeta_domain.interpolate_from(sodafile,'ssh',frame=0,depthname='st_ocean',\
	coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s)

	zeta_domain.extract_subset_into(zeta_south)
	zeta_domain.extract_subset_into(zeta_north)
	zeta_domain.extract_subset_into(zeta_west)

	if first_call:
		interp_u2s,interp_v2s = vel_domain.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',\
		coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'])
	else:
		vel_domain.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',\
		coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'],\
		interpolator_u=interp_u2s,interpolator_v=interp_v2s)

	vel_domain.extract_subset_into(vel_south)
	vel_domain.extract_subset_into(vel_north)
	vel_domain.extract_subset_into(vel_west)

	# ---------- list segments and variables to be written -------
	list_segments = [south,north,west]

	list_variables = [temp_south,temp_north,temp_west, \
	                  salt_south,salt_north,salt_west, \
	                  zeta_south,zeta_north,zeta_west ]

	list_vectvariables = [vel_south,vel_north,vel_west]

	#----------- time --------------------------------------------
	time = temp_south.timesrc

	# ---------- write to file -----------------------------------
	ncdf.write_obc_file(list_segments,list_variables,list_vectvariables,time,output=fileout)

	first_call=False
	end = ptime.time()
	print('done in ', end-start)
