from brushcutter import lib_obc_segments as los
from brushcutter import lib_obc_variable as lov
from brushcutter import lib_obc_vectvariable as losv
from brushcutter import lib_ioncdf as ncdf

sodafile = '../data/soda3.3.1_5dy_ocean_reg_1980_09_29.nc'
momgrd = '../data/ocean_hgrid_v2.nc'

# ---------- define segments on MOM grid -----------------------
south = los.obc_segment('segment_001',momgrd,imin=0,imax=360,jmin=0,  jmax=0  )
north = los.obc_segment('segment_002',momgrd,imin=0,imax=360,jmin=960,jmax=960)
west  = los.obc_segment('segment_003',momgrd,imin=0,imax=0,  jmin=0,  jmax=960)

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

# ---------- interpolate T/S from WOA monthly file, frame = 0 (jan) and using locstream (x2 speedup)
temp_south.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'])
temp_north.interpolate_from(sodafile,'temp',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'])
temp_west.interpolate_from(sodafile ,'temp',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'])

salt_south.interpolate_from(sodafile,'salt',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'])
salt_north.interpolate_from(sodafile,'salt',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'])
salt_west.interpolate_from(sodafile ,'salt',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'])

# ---------- set constant value for SSH ----------------------
zeta_south.interpolate_from(sodafile,'ssh',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'])
zeta_north.interpolate_from(sodafile,'ssh',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'])
zeta_west.interpolate_from(sodafile,'ssh',frame=0,depthname='st_ocean',coord_names=['xt_ocean','yt_ocean'])

vel_south.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',coord_names=['xu_ocean','yu_ocean'])
vel_north.interpolate_from(sodafile,'u','v',frame=0,depthname='st_ocean',coord_names=['xu_ocean','yu_ocean'])
vel_west.interpolate_from(sodafile ,'u','v',frame=0,depthname='st_ocean',coord_names=['xu_ocean','yu_ocean'])

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
