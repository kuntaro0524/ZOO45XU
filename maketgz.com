#!/bin/csh
pwd > pwd.log
tar cvfz $1.tgz XSCALE.INP XSCALE.LP *.log pwd.log ccp4/
