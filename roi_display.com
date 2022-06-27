#!/bin/csh

while(1)
	echo $BLCONFIG
	display roi.png &
	sleep 1
	killall display
end
