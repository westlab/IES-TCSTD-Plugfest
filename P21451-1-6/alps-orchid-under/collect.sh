#!/bin/bash
WAITTIME=600
cd /home/pi/Plugfest2021/P21451-1-6/alps-orchid-under/

for i in {1..6}
do 
  /usr/bin/python3 -u /home/pi/Plugfest2021/P21451-1-6/alps-orchid-under/collect_error_detect.py "$i" &
done

sleep $WAITTIME

for i in {7..12}
do 
  /usr/bin/python3 -u /home/pi/Plugfest2021/P21451-1-6/alps-orchid-under/collect_error_detect.py "$i" &
done

