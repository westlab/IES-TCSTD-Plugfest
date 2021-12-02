LINE_URL = "https://notify-api.line.me/api/notify"
#LINE_TOKEN = "G9TriClW5iSJb6qgMETyw9uFogFdgydKHTnyQtdqlWu"
LINE_TOKEN = "L1OArSqiwLgH4B5D6aOxRsHbAhv9Y2Opn5JW9Xg0UkD"
headers = {
  "Authorization": "Bearer " + LINE_TOKEN
}
sensor_list = ['79','6C','90','94', '9C','89','9A','78','99','76','97', '74','96','93','77']
sensor_list = ["48:F0:7B:78:4B:" + x for x in sensor_list]
