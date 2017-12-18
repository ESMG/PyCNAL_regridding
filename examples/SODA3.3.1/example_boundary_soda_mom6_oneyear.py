from PyCNAL_regridding import lib_obc_segments as los
from PyCNAL_regridding import lib_obc_variable as lov
from PyCNAL_regridding import lib_obc_vectvariable as losv
from PyCNAL_regridding import lib_ioncdf as ncdf

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

# ---------- define variables on each segment ------------------
temp_south = lov.obc_variable(south,'temp',geometry='surface',obctype='radiation',use_locstream=True)
temp_north = lov.obc_variable(north,'temp',geometry='surface',obctype='radiation',use_locstream=True)
temp_west  = lov.obc_variable(west, 'temp',geometry='surface',obctype='radiation',use_locstream=True)

salt_south = lov.obc_variable(south,'salt',geometry='surface',obctype='radiation',use_locstream=True)
salt_north = lov.obc_variable(north,'salt',geometry='surface',obctype='radiation',use_locstream=True)
salt_west  = lov.obc_variable(west, 'salt',geometry='surface',obctype='radiation',use_locstream=True)

zeta_south = lov.obc_variable(south,'zeta',geometry='line',obctype='flather',use_locstream=True)
zeta_north = lov.obc_variable(north,'zeta',geometry='line',obctype='flather',use_locstream=True)
zeta_west  = lov.obc_variable(west ,'zeta',geometry='line',obctype='flather',use_locstream=True)

vel_south  = losv.obc_vectvariable(south,'u','v',geometry='surface',obctype='radiation',use_locstream=True)
vel_north  = losv.obc_vectvariable(north,'u','v',geometry='surface',obctype='radiation',use_locstream=True)
vel_west   = losv.obc_vectvariable(west ,'u','v',geometry='surface',obctype='radiation',use_locstream=True)

first_call=True

for filein in list_soda_files:
	start = ptime.time()
	sodafile = dir_soda + filein
	print('working on ' + sodafile)
	fileout= diroutput + filein.replace('.nc','_CCS1.nc')

	if first_call:
		interp_t2s_south = temp_south.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'])
		interp_t2s_north = temp_north.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'])
		interp_t2s_west  = temp_west.interpolate_from(sodafile ,'temp',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'])
	else:
		temp_south.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_south)
		temp_north.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_north)
		temp_west.interpolate_from(sodafile ,'temp',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_west)

	salt_south.interpolate_from(sodafile,'salt',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_south)
	salt_north.interpolate_from(sodafile,'salt',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_north)
	salt_west.interpolate_from(sodafile ,'salt',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_west)

	zeta_south.interpolate_from(sodafile,'ssh',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_south)
	zeta_north.interpolate_from(sodafile,'ssh',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_north)
	zeta_west.interpolate_from(sodafile ,'ssh',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_west)

	if first_call:
		interp_u2s_south, interp_v2s_south = vel_south.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',\
		coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'])

		interp_u2s_north, interp_v2s_north = vel_north.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',\
		coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'])

		interp_u2s_west, interp_v2s_west = vel_west.interpolate_from(sodafile ,'u','v',frame=0,depthname='st_ocean',\
		coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'])
	else:
		vel_south.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',\
		coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'],\
		interpolator_u=interp_u2s_south,interpolator_v=interp_v2s_south)

		vel_north.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',\
		coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'],\
		interpolator_u=interp_u2s_north,interpolator_v=interp_v2s_north)

		vel_west.interpolate_from(sodafile ,'u','v',frame=0,depthname='st_ocean',\
		coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'],\
		interpolator_u=interp_u2s_west,interpolator_v=interp_v2s_west)


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
