#!/bin/bash
WAITTIME=300
cd /home/pi0/Plugfest2021/P21451-1-6/alps-orchid/

for i in {1..3}
do
 /usr/bin/python3 -u /home/sonoda/Plugfest2021/P21451-1-6/alps-orchid/collect_error_detect.py "$i" &
done

echo "script end"
#/usr/bin/python3 /home/pi0/Plugfest2021/P21451-1-6/alps/test.py
