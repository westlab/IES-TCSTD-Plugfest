#!/bin/bash
for i in {1..8}
do
  python3 sensor.py "$i" &
done
