from PyCNAL_regridding import lib_obc_segments as los
from PyCNAL_regridding import lib_obc_variable as lov
from PyCNAL_regridding import lib_obc_vectvariable as losv
from PyCNAL_regridding import lib_ioncdf as ncdf

sodafile = '../data/soda3.3.1_5dy_ocean_reg_1980_09_29.nc'
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

zeta_south = lov.obc_variable(south,'zeta',geometry='line',obctype='flather',use_locstream=False)
zeta_north = lov.obc_variable(north,'zeta',geometry='line',obctype='flather',use_locstream=False)
zeta_west  = lov.obc_variable(west ,'zeta',geometry='line',obctype='flather',use_locstream=False)
zeta_domain= lov.obc_variable(domain,'zeta',geometry='line',obctype='flather')

vel_south  = losv.obc_vectvariable(south,'u','v',geometry='surface',obctype='radiation',use_locstream=False)
vel_north  = losv.obc_vectvariable(north,'u','v',geometry='surface',obctype='radiation',use_locstream=False)
vel_west   = losv.obc_vectvariable(west ,'u','v',geometry='surface',obctype='radiation',use_locstream=False)
vel_domain = losv.obc_vectvariable(domain ,'u','v',geometry='surface',obctype='radiation')

# ---------- interpolate T/S/U/V from SODA to MOM6 supergrid
interp_t2s = temp_domain.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'])
temp_domain.extract_subset_into(temp_south)
temp_domain.extract_subset_into(temp_north)
temp_domain.extract_subset_into(temp_west)

salt_domain.interpolate_from(sodafile,'salt',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s)

salt_domain.extract_subset_into(salt_south)
salt_domain.extract_subset_into(salt_north)
salt_domain.extract_subset_into(salt_west)

zeta_domain.interpolate_from(sodafile,'ssh',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'],interpolator=interp_t2s)

zeta_domain.extract_subset_into(zeta_south)
zeta_domain.extract_subset_into(zeta_north)
zeta_domain.extract_subset_into(zeta_west)

interp_u2s,interp_v2s = vel_domain.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',coord_names_u=['xu_ocean','yu_ocean'],\
coord_names_v=['xu_ocean','yu_ocean'])

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
ncdf.write_obc_file(list_segments,list_variables,list_vectvariables,time,output='soda3.3.1_5dy_ocean_reg_1980_09_29_bdry_CCS.nc')
