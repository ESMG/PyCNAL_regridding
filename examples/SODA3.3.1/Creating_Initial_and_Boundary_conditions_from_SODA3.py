
# coding: utf-8

# # Creating Initial and boundary conditions for MOM6 from SODA3

# In[ ]:

# import the regridding module
from PyCNAL_regridding import *


# In[ ]:

# ---------- path to MOM6 grid and SODA3 data ---------------------
momgrd = '../data/ocean_hgrid_ccs1.nc'

# change this to wherever you've got SODA3
sodadir = '/Users/raphael/STORAGE/SODA3.3.1/'

# output directory
outputdir = './output_soda3/'


# # 1. initial Condition

# In[ ]:

# pick date for initial condition
year=1981 ; month=1 ; day=2

cyear= str(year) ; cmonth=str(month).zfill(2) ; cday = str(day).zfill(2)
sodaic = sodadir + cyear + '/' + 'soda3.3.1_5dy_ocean_reg_' + cyear + '_' + cmonth + '_' + cday + '.nc'


# In[ ]:

# ---------- define a domain target on MOM grid ---------------------
Nx=360
Ny=960
domain = obc_segment('domain', momgrd,istart=0,iend=Nx,jstart=0,  jend=Ny)


# In[ ]:

# ---------- define variables on each segment ------------------
temp_domain = obc_variable(domain,'temp',geometry='surface',obctype='radiation')
salt_domain = obc_variable(domain,'salt',geometry='surface',obctype='radiation')
ssh_domain  = obc_variable(domain,'ssh' ,geometry='line'   ,obctype='flather')
vel_domain  = obc_vectvariable(domain,'u','v',geometry='surface',obctype='radiation')


# In[ ]:

# ---------- interpolate T/S/U/V/SSH from SODA file -------------------
# note that since temp/salt/ssh are on all defined on T-point, we can re-use
# the same interpolator (time-saving)

interp_t2s = temp_domain.interpolate_from(sodaic,'temp',frame=0,depthname='st_ocean',                                           coord_names=['xt_ocean','yt_ocean'],method='bilinear')
salt_domain.interpolate_from(sodaic,'salt',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'],                             method='bilinear',interpolator=interp_t2s)
ssh_domain.interpolate_from(sodaic ,'ssh' ,frame=0,coord_names=['xt_ocean','yt_ocean'],                            method='bilinear',interpolator=interp_t2s)

# but we can't reuse the previous interpolator because u,v are defined at U,V point, not T point
interp_u2s, interp_v2s = vel_domain.interpolate_from(sodaic,'u','v',frame=0,depthname='st_ocean',                                                     coord_names_u=['xu_ocean','yu_ocean'],                                                      coord_names_v=['xu_ocean','yu_ocean'],method='bilinear')


# In[ ]:

# ---------- list segments and variables to be written -------
list_segments = [domain]
list_variables = [ssh_domain,temp_domain,salt_domain]
list_vectvariables = [vel_domain]

#----------- time --------------------------------------------
time = temp_domain.timesrc

# ---------- write to file -----------------------------------
write_ic_file(list_segments,list_variables,list_vectvariables,time,output=outputdir + 'initial_condition_SODA3.nc')


# # 2. Boundary Conditions

# In[ ]:

import subprocess as sp
import numpy as np


# In[ ]:

# pick which years to regrid
firstyear=1981 ; lastyear=1981


# In[ ]:

# create the list of the SODA files we want to regrid

list_soda_files = []
for year in np.arange(firstyear,lastyear+1):
    cmd = 'ls ' + sodadir + '/' + str(year) + ' | grep nc '
    list_this_year = sp.check_output(cmd,shell=True).replace('\n',' ').split()
    for sodafile in list_this_year:
        list_soda_files.append(sodadir + '/' + str(year) + '/' + sodafile)


# In[ ]:

# ---------- define segments on MOM grid -----------------------
Nx=360
Ny=960
north = obc_segment('segment_001',momgrd,istart=Nx,iend=0, jstart=Ny,jend=Ny)
west  = obc_segment('segment_002',momgrd,istart=0, iend=0, jstart=Ny,jend=0 )
south = obc_segment('segment_003',momgrd,istart=0, iend=Nx,jstart=0, jend=0 )


# In[ ]:

# ---------- define variables on each segment ------------------
temp_south = obc_variable(south,'temp',geometry='surface',obctype='radiation',use_locstream=True)
temp_north = obc_variable(north,'temp',geometry='surface',obctype='radiation',use_locstream=True)
temp_west  = obc_variable(west, 'temp',geometry='surface',obctype='radiation',use_locstream=True)

salt_south = obc_variable(south,'salt',geometry='surface',obctype='radiation',use_locstream=True)
salt_north = obc_variable(north,'salt',geometry='surface',obctype='radiation',use_locstream=True)
salt_west  = obc_variable(west, 'salt',geometry='surface',obctype='radiation',use_locstream=True)

zeta_south = obc_variable(south,'zeta',geometry='line',obctype='flather',use_locstream=True)
zeta_north = obc_variable(north,'zeta',geometry='line',obctype='flather',use_locstream=True)
zeta_west  = obc_variable(west ,'zeta',geometry='line',obctype='flather',use_locstream=True)

vel_south  = obc_vectvariable(south,'u','v',geometry='surface',obctype='radiation',use_locstream=True)
vel_north  = obc_vectvariable(north,'u','v',geometry='surface',obctype='radiation',use_locstream=True)
vel_west   = obc_vectvariable(west ,'u','v',geometry='surface',obctype='radiation',use_locstream=True)


# In[ ]:

# ---------- run the regridding on the list of files ------------------
# for the first call to the regridding, we save all the interpolators
# (for each segment, and each type of variable), so we don't need to
# recompute the regridding weights for the N-1 following files

first_call=True

for sodafile in list_soda_files:
    print('working on ' + sodafile)
    filein=sodafile.replace('/',' ').split()[-1]
    fileout= outputdir + filein.replace('.nc','_obc.nc')

    if first_call:
        interp_t2s_south = temp_south.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',                                                       coord_names=['xt_ocean','yt_ocean'])
        interp_t2s_north = temp_north.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',                                                       coord_names=['xt_ocean','yt_ocean'])
        interp_t2s_west  = temp_west.interpolate_from(sodafile ,'temp',frame=0,depthname='st_ocean',                                                      coord_names=['xt_ocean','yt_ocean'])
    else:
        temp_south.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',                                    coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_south)
        temp_north.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',                                    coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_north)
        temp_west.interpolate_from(sodafile ,'temp',frame=0,depthname='st_ocean',                                   coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_west)

    salt_south.interpolate_from(sodafile,'salt',frame=0,depthname='st_ocean',                                coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_south)
    salt_north.interpolate_from(sodafile,'salt',frame=0,depthname='st_ocean',                                coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_north)
    salt_west.interpolate_from(sodafile ,'salt',frame=0,depthname='st_ocean',                               coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_west)

    zeta_south.interpolate_from(sodafile,'ssh',frame=0,depthname='st_ocean',                                coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_south)
    zeta_north.interpolate_from(sodafile,'ssh',frame=0,depthname='st_ocean',                                coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_north)
    zeta_west.interpolate_from(sodafile ,'ssh',frame=0,depthname='st_ocean',                               coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s_west)

    if first_call:
        interp_u2s_south, interp_v2s_south = vel_south.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',        coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'])

        interp_u2s_north, interp_v2s_north = vel_north.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',        coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'])

        interp_u2s_west, interp_v2s_west = vel_west.interpolate_from(sodafile ,'u','v',frame=0,depthname='st_ocean',        coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'])
    else:
        vel_south.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',        coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'],        interpolator_u=interp_u2s_south,interpolator_v=interp_v2s_south)

        vel_north.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',        coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'],        interpolator_u=interp_u2s_north,interpolator_v=interp_v2s_north)

        vel_west.interpolate_from(sodafile ,'u','v',frame=0,depthname='st_ocean',        coord_names_u=['xu_ocean','yu_ocean'],coord_names_v=['xu_ocean','yu_ocean'],        interpolator_u=interp_u2s_west,interpolator_v=interp_v2s_west)
        
    # ---------- list segments and variables to be written -------
    list_segments = [south,north,west]

    list_variables = [temp_south,temp_north,temp_west,                       salt_south,salt_north,salt_west,                       zeta_south,zeta_north,zeta_west ]

    list_vectvariables = [vel_south,vel_north,vel_west]

    #----------- time --------------------------------------------
    time = temp_south.timesrc

    # ---------- write to file -----------------------------------
    write_obc_file(list_segments,list_variables,list_vectvariables,time,output=fileout)

    first_call=False


# In[ ]:



