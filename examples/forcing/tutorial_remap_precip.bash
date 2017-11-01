#!/bin/bash

dirdata_merra=/Volumes/P4/workdir/raphael/work_conserve_remap
merra_file=MERRA_rain_3hours_1980_2days.nc

# first add lon and lat bounds on the target grid, here CORE2
# the python scripts writes a file containing only those bounds
# hence we need to append the original file to it
./create_bounds_conserve.py ../data/lsm_CORE2.nc
ncks -A ../data/lsm_CORE2.nc ../data/lsm_CORE2_conserve.nc

# same thing for precip date, here on MERRA grid
./create_bounds_conserve.py $dirdata_merra/$merra_file
merra_file_conserve=$( echo $merra_file | sed -e "s/.nc/_conserve.nc/")
ncks -A $dirdata_merra/$merra_file $dirdata_merra/$merra_file_conserve

# run the conservative reampping from ESMF
python example_conservative_remapping_precip.py $dirdata_merra/$merra_file_conserve

# concatenate the N individual files into one big file and clean-up
ncrcat merra_rain_conserve_fr????.nc -o merra_rain_conserve.nc
rm merra_rain_conserve_fr????.nc
