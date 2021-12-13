LINE_URL = "https://notify-api.line.me/api/notify"
LINE_TOKEN = "CDrUpbOhiyuBEP90vYV9A3vJtEYq954JZpV8IFueOGB"
headers = {
  "Authorization": "Bearer " + LINE_TOKEN
}
sensor_list = ['98','81','70','8E','8D','6E', '6F']
sensor_list = ["48:F0:7B:78:4B:" + x for x in sensor_list]

sensor_values = []
for i in range(1,8):
  x = 'sensor' + str(i)
  sensor_values.append(x)

sensor_dic = {key: val for key, val in zip(sensor_list, sensor_values)}


