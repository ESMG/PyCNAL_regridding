
# coding: utf-8

# # Creating Initial and boundary conditions for MOM6 from WOA13

# In[ ]:

# import the regridding module
from PyCNAL_regridding import *


# In[ ]:

# ---------- path to MOM6 grid and WOA T/S data ---------------------
momgrd = '../data/ocean_hgrid_ccs1.nc'
woatemp = '../data/woa13_5564_t01_01.nc'
woasalt = '../data/woa13_5564_s01_01.nc'


# ## 1. initial Condition

# In[ ]:

# ---------- define a domain target on MOM grid ---------------------
domain = obc_segment('domain', momgrd,istart=0,iend=360,jstart=0,  jend=960)


# In[ ]:

# ---------- define variables on each segment -----------------------
temp_domain = obc_variable(domain,'temp',geometry='surface',obctype='radiation')
salt_domain = obc_variable(domain,'salt',geometry='surface',obctype='radiation')
ssh_domain  = obc_variable(domain,'ssh' ,geometry='line'   ,obctype='flather')
vel_domain  = obc_vectvariable(domain,'u','v',geometry='surface',obctype='radiation')


# In[ ]:

# ---------- interpolate T/S from WOA january file ------------------
# since T and S are on the same grid, we can save the interpolator from T and re-use for S
# to save time
regrid_ts = temp_domain.interpolate_from( woatemp,'t_an',depthname='depth')
regrid_ts = salt_domain.interpolate_from( woasalt,'s_an',depthname='depth',interpolator=regrid_ts)


# In[ ]:

# we use the depth from the temp field to create the depth vector for velocities
depth_woa = temp_domain.depth[:,0,0]

# ---------- we don't have ssh or velocities, setting up to zero -----
ssh_domain.set_constant_value(0.0)
vel_domain.set_constant_value(0.,0.,depth_vector=depth_woa)


# In[ ]:

# ---------- list segments and variables to be written -------
list_segments = [domain]
list_variables = [ssh_domain,temp_domain,salt_domain]
list_vectvariables = [vel_domain]

#----------- time --------------------------------------------
time = timeobject(15.5)
time.units = 'days since 1900-01-01'
time.calendar = 'gregorian'

# ---------- write to file -----------------------------------
write_ic_file(list_segments,list_variables,list_vectvariables,time,output='./output_woa13/initial_condition_WOA13_jan.nc')


# ## 2. Boundary Conditions

# In[ ]:

# ---------- define segments on MOM grid -----------------------
south = obc_segment('segment_001', momgrd,istart=0,iend=360,jstart=0,  jend=0  )
north = obc_segment('segment_002', momgrd,istart=0,iend=360,jstart=960,jend=960)
west  = obc_segment('segment_003', momgrd,istart=0,iend=0,  jstart=0,  jend=960)


# In[ ]:

# ---------- define variables on each segment ------------------
temp_south = obc_variable(south,'temp',geometry='surface',obctype='radiation',use_locstream=True)
temp_north = obc_variable(north,'temp',geometry='surface',obctype='radiation',use_locstream=True)
temp_west  = obc_variable(west, 'temp',geometry='surface',obctype='radiation',use_locstream=True)

salt_south = obc_variable(south,'salt',geometry='surface',obctype='radiation',use_locstream=True)
salt_north = obc_variable(north,'salt',geometry='surface',obctype='radiation',use_locstream=True)
salt_west  = obc_variable(west, 'salt',geometry='surface',obctype='radiation',use_locstream=True)

zeta_south = obc_variable(south,'zeta',geometry='line',obctype='flather')
zeta_north = obc_variable(north,'zeta',geometry='line',obctype='flather')
zeta_west  = obc_variable(west ,'zeta',geometry='line',obctype='flather')

vel_south  = obc_vectvariable(south,'u','v',geometry='surface',obctype='radiation')
vel_north  = obc_vectvariable(north,'u','v',geometry='surface',obctype='radiation')
vel_west   = obc_vectvariable(west ,'u','v',geometry='surface',obctype='radiation')


# In[ ]:

days_in_month = np.array([31,28,31,30,31,30,31,31,30,31,30,31])

# loop over months
for kt in np.arange(12):
    # pick the correct filename
    mm=str(kt+1).zfill(2)
    woatemp = '../data/woa13_5564_t' + mm + '_01.nc'
    woasalt = '../data/woa13_5564_s' + mm + '_01.nc'
 
    # ---------- interpolate T/S from WOA file
    temp_south.interpolate_from( woatemp,'t_an',depthname='depth')
    temp_north.interpolate_from( woatemp,'t_an',depthname='depth')
    temp_west.interpolate_from(  woatemp,'t_an',depthname='depth')
    
    salt_south.interpolate_from( woasalt,'s_an',depthname='depth')
    salt_north.interpolate_from( woasalt,'s_an',depthname='depth')
    salt_west.interpolate_from(  woasalt,'s_an',depthname='depth')
    
    # ---------- set constant value for SSH and velocities -------
    zeta_south.set_constant_value(0.0)
    zeta_north.set_constant_value(0.0)
    zeta_west.set_constant_value(0.0)

    vel_south.set_constant_value(0.,0.,depth_vector=depth_woa)
    vel_north.set_constant_value(0.,0.,depth_vector=depth_woa)
    vel_west.set_constant_value(0.,0.,depth_vector=depth_woa)
    
    # ---------- list segments and variables to be written -------
    list_segments = [north,south,west]

    list_variables = [temp_south,temp_north,temp_west,                       salt_south,salt_north,salt_west,                       zeta_south,zeta_north,zeta_west ]

    list_vectvariables = [vel_south,vel_north,vel_west]

    #----------- time --------------------------------------------
    middle_of_current_month = days_in_month[:kt].sum() + 0.5 * days_in_month[kt]
    time = timeobject(middle_of_current_month)
    time.units = 'days since 1900-01-01'
    time.calendar = 'gregorian'

    # ---------- write to file -----------------------------------
    write_obc_file(list_segments,list_variables,list_vectvariables,time,output='output_woa13/obc_woa13_m' + mm + '.nc')


# In[ ]:



