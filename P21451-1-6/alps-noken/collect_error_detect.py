from collect_sugawara import main as collect
from time import sleep
import sys
import requests
import global_variable as g

#for sensor in g.sensor_list:
sensor_number = sys.argv[1]
sensor = g.sensor_list[int(sensor_number)-1]
count = 0
error = None
while True:
  try:
    print("start collecting data from {}".format(sensor))
    collect(sensor, sensor_number)
    print("end\n")
    break
  except Exception as e:
    error = e
    count += 1
    print(e)
    print("failed to collect data from {}. this program is going to try it again in 30sec.".format(sensor))
    sleep(30)
  if count > 2:
    print("we could not collect data from {}. please check it.\n".format(sensor))
    params = {
      'message': 'Error occured when collectiong data from {}.\n{}'.format(sensor,str(error))
    }
    requests.post(g.LINE_URL, headers=g.headers, params=params)
    break
