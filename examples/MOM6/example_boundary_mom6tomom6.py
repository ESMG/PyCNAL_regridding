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

# ---------- define variables on each segment ------------------
temp_south = lov.obc_variable(south,'temp',geometry='surface',obctype='radiation',use_locstream=True)
temp_north = lov.obc_variable(north,'temp',geometry='surface',obctype='radiation',use_locstream=True)
temp_west  = lov.obc_variable(west, 'temp',geometry='surface',obctype='radiation',use_locstream=True)

salt_south = lov.obc_variable(south,'salt',geometry='surface',obctype='radiation',use_locstream=True)
salt_north = lov.obc_variable(north,'salt',geometry='surface',obctype='radiation',use_locstream=True)
salt_west  = lov.obc_variable(west, 'salt',geometry='surface',obctype='radiation',use_locstream=True)

e_south    = lov.obc_variable(south,'e',geometry='surface',obctype='flather',use_locstream=True)
e_north    = lov.obc_variable(north,'e',geometry='surface',obctype='flather',use_locstream=True)
e_west     = lov.obc_variable(west ,'e',geometry='surface',obctype='flather',use_locstream=True)

vel_south  = losv.obc_vectvariable(south,'u','v',geometry='surface',obctype='radiation',use_locstream=True)
vel_north  = losv.obc_vectvariable(north,'u','v',geometry='surface',obctype='radiation',use_locstream=True)
vel_west   = losv.obc_vectvariable(west ,'u','v',geometry='surface',obctype='radiation',use_locstream=True)

# ---------- interpolate T/S from WOA monthly file, frame = 0 (jan) and using locstream (x2 speedup)
temp_south.interpolate_from(momfile,'temp',frame=0,depthname='zl',coord_names=['xh','yh'])
temp_north.interpolate_from(momfile,'temp',frame=0,depthname='zl',coord_names=['xh','yh'])
temp_west.interpolate_from(momfile ,'temp',frame=0,depthname='zl',coord_names=['xh','yh'])

salt_south.interpolate_from(momfile,'salt',frame=0,depthname='zl',coord_names=['xh','yh'])
salt_north.interpolate_from(momfile,'salt',frame=0,depthname='zl',coord_names=['xh','yh'])
salt_west.interpolate_from(momfile ,'salt',frame=0,depthname='zl',coord_names=['xh','yh'])

# ---------- set constant value for SSH ----------------------
e_south.interpolate_from(momfile,'e',frame=0,depthname='zi',coord_names=['xh','yh'])
e_north.interpolate_from(momfile,'e',frame=0,depthname='zi',coord_names=['xh','yh'])
e_west.interpolate_from(momfile,'e',frame=0,depthname='zi',coord_names=['xh','yh'])

vel_south.interpolate_from(momfile,'u','v',frame=0,depthname='zl',coord_names_u=['xq','yh'],coord_names_v=['xh','yq'])
vel_north.interpolate_from(momfile,'u','v',frame=0,depthname='zl',coord_names_u=['xq','yh'],coord_names_v=['xh','yq'])
vel_west.interpolate_from(momfile ,'u','v',frame=0,depthname='zl',coord_names_u=['xq','yh'],coord_names_v=['xh','yq'])

# ---------- list segments and variables to be written -------
list_segments = [south,north,west]

list_variables = [temp_south,temp_north,temp_west, \
                  salt_south,salt_north,salt_west, \
                  e_south,e_north,e_west ]

list_vectvariables = [vel_south,vel_north,vel_west]

#----------- time --------------------------------------------
time = temp_south.timesrc

# ---------- write to file -----------------------------------
ncdf.write_obc_file(list_segments,list_variables,list_vectvariables,time,output='mom6_bdry_CCS.nc')
