#!/bin/bash
for i in {1..7}
do
  python sensor.py "$i" &
done
