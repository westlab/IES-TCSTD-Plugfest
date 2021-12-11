#!/bin/bash
for i in {1..6}
do
  python init.py "$i" &
done
