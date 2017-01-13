from brushcutter import *

momfile = '/Volumes/P4/workdir/raphael/work_brushcutter/20140101.nc'
momgrd = '../data/ocean_hgrid_v2.nc'

# ---------- define segments on MOM grid -----------------------
domain = obc_segment('domain', momgrd,istart=0,iend=360,jstart=0,  jend=960)

# ---------- define variables on each segment ------------------
temp_domain = obc_variable(domain,'temp',geometry='surface',obctype='radiation')
salt_domain = obc_variable(domain,'salt',geometry='surface',obctype='radiation')
e_domain    = obc_variable(domain,'e',   geometry='surface',obctype='flather')
vel_domain  = obc_vectvariable(domain,'u','v',geometry='surface',obctype='radiation')

# ---------- interpolate T/S from SODA file -------------------
interp_t2s = temp_domain.interpolate_from(momfile,'temp',frame=0,depthname='zl',coord_names=['xh','yh'],method='bilinear')
salt_domain.interpolate_from(momfile,'salt',frame=0,depthname='zl',coord_names=['xh','yh'],method='bilinear',interpolator=interp_t2s)
e_domain.interpolate_from(momfile ,'e' ,frame=0,depthname='zi',coord_names=['xh','yh'],method='bilinear',interpolator=interp_t2s)
# we can't reuse the previous interpolator because the source grid changes
interp_u2s, interp_v2s = vel_domain.interpolate_from(momfile,'u','v',frame=0,depthname='zl',coord_names_u=['xq','yh'], \
coord_names_v=['xh','yq'],method='bilinear')

# ---------- list segments and variables to be written -------
list_segments = [domain]

list_variables = [temp_domain,salt_domain,e_domain] 

list_vectvariables = [vel_domain]

#----------- time --------------------------------------------
time = temp_domain.timesrc

# ---------- write to file -----------------------------------
lib_ioncdf.write_obc_file(list_segments,list_variables,list_vectvariables,time,output='MOM6_to_domain_CCS.nc')
