#!/usr/bin/bash
for i in {1..7}
do
  python init.py "$i" &
  
done
