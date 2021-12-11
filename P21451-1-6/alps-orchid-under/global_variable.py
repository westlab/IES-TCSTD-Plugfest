LINE_URL = "https://notify-api.line.me/api/notify"
#LINE_TOKEN = "G9TriClW5iSJb6qgMETyw9uFogFdgydKHTnyQtdqlWu"
LINE_TOKEN = "L1OArSqiwLgH4B5D6aOxRsHbAhv9Y2Opn5JW9Xg0UkD"
headers = {
  "Authorization": "Bearer " + LINE_TOKEN
}

sensor_list1 = ['36','33','25','35', '29','4E']
sensor_list1 = ["48:F0:7B:78:47:" + x for x in sensor_list1]
#sensor_list2 = ['96','85','95','8A','92','75']
#sensor_list2 = ["48:F0:7B:78:47:" + x for x in sensor_list2]
sensor_list2 = ['78','6F','71','6C','6E','72']
sensor_list2 = ["48:F0:7B:78:4C:" + x for x in sensor_list2]

sensor_list = sensor_list1 + sensor_list2

sensor_dic = {"48:F0:7B:78:4C:78":"sensor1", "48:F0:7B:78:4C:6F":"sensor2", "48:F0:7B:78:4C:71":"sensor3", "48:F0:7B:78:4C:6C":"sensor4", "48:F0:7B:78:4C:6E":"sensor5", "48:F0:7B:78:4C:72":"sensor6", "48:F0:7B:78:47:36":"sensor14", "48:F0:7B:78:47:33":"sensor16", "48:F0:7B:78:47:25":"sensor18", "48:F0:7B:78:47:35":"sensor19", "48:F0:7B:78:47:29":"sensor20", "48:F0:7B:78:47:4E":"sensor21"}
