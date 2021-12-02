from init import main as init
from time import sleep
import sys
import global_variable as g

for sensor in g.sensor_list:
  init(sensor)
#init(g.sensor_list[-3])
#init("48:F0:7B:78:4B:96")

