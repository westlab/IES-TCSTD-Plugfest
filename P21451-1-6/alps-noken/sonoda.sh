#!/usr/bin/bash
cd /home/pi/Plugfest2021/P21451-1-6/alps-noken/
for i in {1..7}
do
  /usr/bin/python3 -u /home/pi/Plugfest2021/P21451-1-6/alps-noken/collect.parent.sonoda.py "$i" &
done
echo "script end" 
