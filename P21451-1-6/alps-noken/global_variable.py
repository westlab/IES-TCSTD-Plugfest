LINE_URL = "https://notify-api.line.me/api/notify"
LINE_TOKEN = "CDrUpbOhiyuBEP90vYV9A3vJtEYq954JZpV8IFueOGB"
headers = {
  "Authorization": "Bearer " + LINE_TOKEN
}
#sensor_list = ['98', '81', '70','8E', '8D', '6E', '6F']
#sensor_list = ["48:F0:7B:78:4B:" + x for x in sensor_list]
sensor_list1 = ['78','6F','71','6C','6E','72']
sensor_list1 = ['78','6C','6E']
sensor_list1 = ["48:F0:7B:78:4C:" + x for x in sensor_list1]
sensor_list2 = ['35','29','4E','36','33','25']
sensor_list2 = ["48:F0:7B:78:47:" + x for x in sensor_list2]

sensor_list = sensor_list1 + sensor_list2
#sensor_list = sensor_list1

