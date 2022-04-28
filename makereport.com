#!/bin/bash

dbfile=$1
title=$2

echo $dbfile

# At the data collection directory
yamtbx.python ~/ZOO45XU/Libs/ZOOhtmlMaker.py $dbfile $2

# For _kamoproc
cd _kamoproc/
yamtbx.python /isilon/users/target/target/PPPP/18.Report/XDSReporter.py . report_$2.html
cd ../

# Time stamp
timestr=`date "+%y%m%d%H%M"`
arcfile=${timestr}_${2}_report.tgz

echo "making $arcfile"

# archive a file
tar cvfz $arcfile ./*html _kamoproc/*html _kamoproc/contents/

# Copy this file to /isilon/BL45XU/TMP/
#cp $arcfile /isilon/BL45XU/TMP/

echo "Running directory: $PWD" > message.txt
#xxxxcat message.txt | mailx -a $arcfile -s "ZOO report .tgz is attached [$arcfile]" kunio.hirata@riken.jp << message.tx
cat message.txt | mailx -a $arcfile -s "ZOO report .tgz is attached [$arcfile]" y-nakamu@spring8.or.jp
