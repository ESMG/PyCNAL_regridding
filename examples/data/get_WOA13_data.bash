#!/bin/bash
# download 1 degree resolution WOA13 Temperature and Salinity

for mm in $( seq -f %02g 1 12 ) ; do

    echo downloading month $mm
    wget https://data.nodc.noaa.gov/woa/WOA13/DATA/temperature/netcdf/5564/1.00/woa13_5564_t${mm}_01.nc
    wget https://data.nodc.noaa.gov/woa/WOA13/DATA/salinity/netcdf/5564/1.00/woa13_5564_s${mm}_01.nc

done
