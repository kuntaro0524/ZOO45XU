#!/bin/csh
# BL45XU PILATUS cbf file: scan skip

# Usage : 
# 1. move to HDD-directory
# 2. run tanuki.com 
# EX) tanuki.com FROM_DIRNAME

set INDIR = $1
echo "Copying from ",$INDIR 

while (1)
#echo "DIRE=",$INDIR
find $INDIR -name '*cbf' -printf "%P\n" |grep scan > exclude.list
rsync -auv --exclude-from=./exclude.list $INDIR ./
sleep 60
end
