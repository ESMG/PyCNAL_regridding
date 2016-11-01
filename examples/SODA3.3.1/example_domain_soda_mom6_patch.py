from brushcutter import *

sodafile = '../data/soda3.3.1_5dy_ocean_reg_1980_09_29.nc'
momgrd = '../data/ocean_hgrid_v2.nc'

# ---------- define segments on MOM grid -----------------------
domain = obc_segment('domain', momgrd,imin=0,imax=360,jmin=0,  jmax=960)

# ---------- define variables on each segment ------------------
temp_domain = obc_variable(domain,'temp',geometry='surface',obctype='radiation')
salt_domain = obc_variable(domain,'salt',geometry='surface',obctype='radiation')
ssh_domain  = obc_variable(domain,'ssh' ,geometry='line'   ,obctype='flather')
vel_domain  = obc_vectvariable(domain,'u','v',geometry='surface',obctype='radiation')

# ---------- interpolate T/S from WOA monthly file, frame = 0 (jan) and using locstream (x2 speedup)
temp_domain.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',use_locstream=False,coord_names=['xt_ocean','yt_ocean'],method='patch')
salt_domain.interpolate_from(sodafile,'salt',frame=0,depthname='st_ocean',use_locstream=False,coord_names=['xt_ocean','yt_ocean'],method='patch')
ssh_domain.interpolate_from(sodafile ,'ssh' ,frame=0,depthname='st_ocean',use_locstream=False,coord_names=['xt_ocean','yt_ocean'],method='patch')
vel_domain.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',use_locstream=False,coord_names=['xu_ocean','yu_ocean'],method='patch')

# ---------- list segments and variables to be written -------
list_segments = [domain]

list_variables = [temp_domain,salt_domain,ssh_domain] 

list_vectvariables = [vel_domain]

#----------- time --------------------------------------------
time = temp_domain.timesrc

# ---------- write to file -----------------------------------
lib_ioncdf.write_obc_file(list_segments,list_variables,list_vectvariables,time,output='soda3.3.1_5dy_ocean_reg_1980_09_29_domain_CCS_patch.nc')
