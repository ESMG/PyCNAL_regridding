from brushcutter import lib_obc_segments as los
from brushcutter import lib_obc_variable as lov
from brushcutter import lib_obc_vectvariable as losv
from brushcutter import lib_ioncdf as ncdf

momfile = '/Volumes/P4/workdir/raphael/work_brushcutter/20140101.nc'
momgrd = '../data/ocean_hgrid_v2.nc'

# ---------- define segments on MOM grid -----------------------
south = los.obc_segment('segment_001',momgrd,istart=0,iend=360,jstart=0,  jend=0  )
north = los.obc_segment('segment_002',momgrd,istart=0,iend=360,jstart=960,jend=960)
west  = los.obc_segment('segment_003',momgrd,istart=0,iend=0,  jstart=0,  jend=960)
domain= los.obc_segment('domain',momgrd,istart=0,iend=360,  jstart=0,  jend=960)

# ---------- define variables on each segment ------------------
temp_south = lov.obc_variable(south,'temp',geometry='surface',obctype='radiation',use_locstream=False)
temp_north = lov.obc_variable(north,'temp',geometry='surface',obctype='radiation',use_locstream=False)
temp_west  = lov.obc_variable(west, 'temp',geometry='surface',obctype='radiation',use_locstream=False)
temp_domain= lov.obc_variable(domain,'temp',geometry='surface',obctype='radiation')

salt_south = lov.obc_variable(south,'salt',geometry='surface',obctype='radiation',use_locstream=False)
salt_north = lov.obc_variable(north,'salt',geometry='surface',obctype='radiation',use_locstream=False)
salt_west  = lov.obc_variable(west, 'salt',geometry='surface',obctype='radiation',use_locstream=False)
salt_domain= lov.obc_variable(domain,'salt',geometry='surface',obctype='radiation')

e_south = lov.obc_variable(south,'e',geometry='surface',obctype='flather',use_locstream=False)
e_north = lov.obc_variable(north,'e',geometry='surface',obctype='flather',use_locstream=False)
e_west  = lov.obc_variable(west ,'e',geometry='surface',obctype='flather',use_locstream=False)
e_domain= lov.obc_variable(domain,'e',geometry='surface',obctype='flather')

vel_south  = losv.obc_vectvariable(south,'u','v',geometry='surface',obctype='radiation',use_locstream=False)
vel_north  = losv.obc_vectvariable(north,'u','v',geometry='surface',obctype='radiation',use_locstream=False)
vel_west   = losv.obc_vectvariable(west ,'u','v',geometry='surface',obctype='radiation',use_locstream=False)
vel_domain = losv.obc_vectvariable(domain ,'u','v',geometry='surface',obctype='radiation')

# ---------- interpolate T/S/U/V from SODA to MOM6 supergrid
interp_t2s = temp_domain.interpolate_from(momfile,'temp',frame=0,depthname='zl',coord_names=['xh','yh'])
temp_domain.extract_subset_into(temp_south)
temp_domain.extract_subset_into(temp_north)
temp_domain.extract_subset_into(temp_west)

salt_domain.interpolate_from(momfile,'salt',frame=0,depthname='zl',coord_names=['xh','yh'],interpolator=interp_t2s)

salt_domain.extract_subset_into(salt_south)
salt_domain.extract_subset_into(salt_north)
salt_domain.extract_subset_into(salt_west)

e_domain.interpolate_from(momfile,'e',frame=0,depthname='zi',coord_names=['xh','yh'],interpolator=interp_t2s)

e_domain.extract_subset_into(e_south)
e_domain.extract_subset_into(e_north)
e_domain.extract_subset_into(e_west)

interp_u2s,interp_v2s = vel_domain.interpolate_from(momfile,'u','v',frame=0,depthname='zl',coord_names_u=['xq','yh'],\
coord_names_v=['xh','yq'])

vel_domain.extract_subset_into(vel_south)
vel_domain.extract_subset_into(vel_north)
vel_domain.extract_subset_into(vel_west)

# ---------- list segments and variables to be written -------
list_segments = [south,north,west]

list_variables = [temp_south,temp_north,temp_west, \
                  salt_south,salt_north,salt_west, \
                  e_south,e_north,e_west ]

list_vectvariables = [vel_south,vel_north,vel_west]

#----------- time --------------------------------------------
time = temp_south.timesrc

# ---------- write to file -----------------------------------
ncdf.write_obc_file(list_segments,list_variables,list_vectvariables,time,output='mom6_bdry_CCS_alt.nc')
