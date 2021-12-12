#!/bin/bash
for i in {1..12}
do
  python3 init.py "$i" &
done
