#!/bin/bash

profile=$1
listexamples="example1_mom6.py example2_mom6.py example3_mom6.py example4_mom6.py"

for ex in $listexamples ; do

    echo running example $ex with profile $profile
    time python $ex $profile

done
