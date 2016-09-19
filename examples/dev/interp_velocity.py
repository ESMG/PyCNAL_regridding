from brushcutter import lib_obc_segments as los
from brushcutter import lib_obc_vectvariable as losv
from brushcutter import lib_ioncdf as ncdf

infile = 'uniform_zonal.nc'
momgrd = '/home/raphael/WORK/work_brushcutter/ocean_hgrid_v2.nc'

# ---------- define segments on MOM grid -----------------------
domain = los.obc_segment('domain',momgrd,imin=0,imax=360,jmin=0,  jmax=960)

# ---------- define variables on each segment ------------------
vel_domain = losv.obc_vectvariable(domain,'u','v',geometry='surface',obctype='radiation',debug=True)

vel_domain = losv.set_contant_value(domain,1.,0.)

# ---------- interpolate T/S from WOA monthly file, frame = 0 (jan) and using locstream (x2 speedup)
#u_domain.interpolate_from(infile,'u',frame=0,depthname='st_ocean',use_locstream=False,from_global=True,vector='U')
#v_domain.interpolate_from(infile,'v',frame=0,depthname='st_ocean',use_locstream=False,from_global=True,vector='V')

#u_real, v_real = 

# ---------- list segments and variables to be written -------
#list_segments = [domain]

#list_variables = [u_domain,v_domain]

#----------- time --------------------------------------------
#time = u_domain.timesrc

# ---------- write to file -----------------------------------
#ncdf.write_obc_file(list_segments,list_variables,time,output='interpolated_vel.nc')
