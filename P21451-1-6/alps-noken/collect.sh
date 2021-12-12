#!/usr/bin/bash
cd /home/pi/Plugfest2021/P21451-1-6/alps-noken/
for i in {1..7}
do
  /usr/bin/python3 -u /home/pi/Plugfest2021/P21451-1-6/alps-noken/collect_error_detect.py "$i" &
done

#sleep 600

#for i in {4..7}
#do
#  /usr/bin/python3 -u /home/pi/Plugfest2021/P21451-1-6/alps-noken/collect_error_detect.py "$i" &
#done
echo "script end" 
