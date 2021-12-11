LINE_URL = "https://notify-api.line.me/api/notify"
#LINE_TOKEN = "G9TriClW5iSJb6qgMETyw9uFogFdgydKHTnyQtdqlWu"
LINE_TOKEN = "L1OArSqiwLgH4B5D6aOxRsHbAhv9Y2Opn5JW9Xg0UkD"
headers = {
  "Authorization": "Bearer " + LINE_TOKEN
}
#sensor_list = ['79','6C','90','94', '9C','89','8F','9A','78','99','76','97', '74','96','93','77']
#prefix1 = "48:F0:7B:78:4C:"
#prefix2 = "48:F0:7B:78:4B:"
#prefix3 = "48:F0:7B:78:47:"
#
#sensor = []
#
#sensor.append(prefix1 + str('78'))
#sensor.append(prefix1 + str('6F'))
#sensor.append(prefix1 + str('71'))
#sensor.append(prefix1 + str('6C'))
#sensor.append(prefix1 + str('6E'))
#sensor.append(prefix1 + str('72'))
#sensor.append(prefix2 + str('8F'))
#sensor.append(prefix2 + str('9A'))
#sensor.append(prefix2 + str('78'))
#sensor.append(prefix2 + str('99'))
#sensor.append(prefix2 + str('76'))
#sensor.append(prefix2 + str('97'))
#sensor.append(prefix2 + str('74'))
#sensor.append(prefix2 + str('96'))
#sensor.append(prefix2 + str('93'))
#sensor.append(prefix2 + str('85'))
#sensor.append(prefix2 + str('77'))
#sensor.append(prefix2 + str('95'))
#sensor.append(prefix2 + str('8A'))
#sensor.append(prefix2 + str('92'))
#sensor.append(prefix2 + str('75'))

#sensor_list = sensor
#sensor_list = ["48:F0:7B:78:4B:" + x for x in sensor_list]
#sensor = "48:F0:7B:78:4B:8A"
sensor_list = ['8F','9A','78','99','76','97','74','93','77']
sensor_list = ["48:F0:7B:78:4B:" + x for x in sensor_list]
sensor_dic = {"48:F0:7B:78:4B:8F":"sensor7","48:F0:7B:78:4B:9A":"sensor8", "48:F0:7B:78:4B:78":"sensor9", "48:F0:7B:78:4B:99":"sensor10", "48:F0:7B:78:4B:76":"sensor11", "48:F0:7B:78:4B:97":"sensor12", "48:F0:7B:78:4B:74":"sensor13", "48:F0:7B:78:4B:93":"sensor15", "48:F0:7B:78:4B:77":"sensor17"} 
