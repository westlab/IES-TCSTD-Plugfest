#!/usr/bin/bash
for i in {1..7}
do
  python3 init.py "$i" &
done

