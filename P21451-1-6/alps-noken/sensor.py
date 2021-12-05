# -*- coding: utf-8 -*- 
from btle import Peripheral
import os
import json
import struct 
import btle
import binascii
from datetime import datetime,date,timedelta
from ftplib import FTP
import time
import sys #引数を受け取るために使う
import requests
import global_variable as g 


def s16(value):
    return -(value & 0b1000000000000000) | (value & 0b0111111111111111)


class NtfyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here
 
    def handleNotification(self, cHandle, data): 
        # ... perhaps check cHandle
        # ... process 'data'
        cal = binascii.b2a_hex(data)
        #print(u'handleNotification : {0}-{1}:'.format(cHandle, cal))
        sensor_folder_name = 'sensor' + sensor_number + '/'
        os.makedirs("./data_save/battery/" + sensor_folder_name, exist_ok=True)
        os.makedirs("./data_save/environment/" + sensor_folder_name, exist_ok=True)
        if int((cal[0:2]), 16) == 0xE0:
            error_status = int(cal[6:8], 16)
            ack = int(cal[20:22], 16)
            #battery = int((cal[14:16] + cal[16:18]), 16)
            battery = int((cal[16:18] + cal[14:16]), 16)
#            if battery < 1500:
#              params = {
#                'message': "バッテリー残量が低下しています\n機体: {}\n現在の
#                容量:{}mV".format(sensor_number, battery)
#              }
#              requests.post(g.LINE_URL, headers = g.headers, params = params)


            hour_now = datetime.now().strftime("%Y-%m-%d-%H")
            minute_now = datetime.now().strftime("%Y-%m-%d-%H-%M")
            trans_hour = (datetime.now() + timedelta(hours = -1)).strftime("%Y-%m-%d-%H") 
            file_path = './data_save/battery/' + sensor_folder_name + hour_now +".json"
            path_battery = './data_save/battery/' + sensor_folder_name

            if os.path.isfile(file_path):
                with open(file_path,'r') as f:
                    d_update = json.load(f)
                d_update[minute_now] = {"Battery":battery}
                with open(file_path,'w') as f:
                    json.dump(d_update, f, indent=2)

            else:
                with open(file_path,'x') as f:
                    f.write('{}')

                with open(file_path, 'r+') as f:
                    all = json.load(f)

                all[minute_now] = {"Battery":battery}

                with open(file_path,'w') as f:
                    json.dump(all, f, indent=2)


        if int((cal[0:2]), 16) == 0xf3:
            Pressure = int((cal[6:8] + cal[4:6]), 16) * 860.0/65535 + 250	
            Humidity = 1.0 * (int((cal[10:12] + cal[8:10]), 16) - 896 )/64
            Temperature = 1.0*((int((cal[14:16] + cal[12:14]), 16) -2096)/50)
            UV = int((cal[18:20] + cal[16:18]), 16) / (100*0.388)
            AmbientLight = int((cal[22:24] + cal[20:22]), 16) / (0.05*0.928)
            print('Pressure:{0:.3f} Humidity:{1:.3f} Temperature:{2:.3f} '.format(Pressure, Humidity , Temperature))
            print('UV:{0:.3f} AmbientLight:{1:.3f} '.format(UV, AmbientLight))


            hour_now = datetime.now().strftime("%Y-%m-%d-%H")
            minute_now = datetime.now().strftime("%Y-%m-%d-%H-%M")

            file_path='./data_save/environment/' + sensor_folder_name + hour_now + ".json"

            if os.path.isfile(file_path):
                with open(file_path,'r') as f:
                    d_update = json.load(f)
                d_update[minute_now] = {"Temperature":Temperature,"Humidity":Humidity,"Pressure":Pressure, "UV":UV, "AmbientLight":AmbientLight}
                with open(file_path,'w') as f:
                    json.dump(d_update, f, indent=2)
            else:
                with open(file_path,'x') as f:
                    f.write('{}')
                with open(file_path,'r+') as f:
                    all=json.load(f)
                all[minute_now] = {"Temperature":Temperature, "Humidity":Humidity, "Pressure":Pressure, "UV":UV, "AmbientLight":AmbientLight}
                with open(file_path,'w') as f:
                    json.dump(all, f, indent=2)

                ftp = FTP('10.26.0.1','ayu_ftp',passwd='WestO831')
                last_hour = (datetime.now() + timedelta(hours = -1)).strftime('%Y-%m-%d-%H')
                trans_file_path = './data_save/environment/' + sensor_folder_name + last_hour + '.json'
                qnap_path = 'SmaAgri/Noken/sonoda/' + sensor_folder_name + last_hour + '.json'

                if os.path.isfile(trans_file_path):
                    with open(trans_file_path, 'rb') as f:
                        ftp.storlines("STOR /"+ qnap_path, f)
             

                ftp_takayama = FTP('192.168.11.4', 'sonoda', passwd='WestO831')
                if os.path.isfile(trans_file_path):
                    with open(trans_file_path, 'rb') as f:
                        ftp_takayama.storlines("STOR /mnt/ssd/sonoda/" + "sensor" + sensor_number + "/" + last_hour + '.json', f)



class AlpsSensor(Peripheral):
    def __init__(self,addr):
        Peripheral.__init__(self,addr)
        self.result = 1
 

def main(sensor_number):
  while True:
    try:

      sensor_list = ['98','81','70','8E','8D','6E','6F']
      sensor_list = ["48:F0:7B:78:4B:" + x for x in sensor_list]

      sensor =sensor_list[int(sensor_number)-1]

      alps = AlpsSensor(sensor)
      alps.setDelegate( NtfyDelegate(btle.DefaultDelegate) )

      alps.writeCharacteristic(0x0013, struct.pack('<bb', 0x01, 0x00), True)# Custom1 Notify Enable 
      alps.writeCharacteristic(0x0016, struct.pack('<bb', 0x01, 0x00), True)# Custom2 Notify Enable


      alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x2F, 0x03, 0x03), True) # (不揮発)保存内容の初期化
      alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x01, 0x03, 0x7c), True) # 地磁気、加速度,気圧,温度,湿度,UV,照度を有効
      alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x04, 0x03, 0x00), True) # slow Mode
#    alps.writeCharacteristic(0x0018, struct.pack('<bbbb', 0x06, 0x04, 0x64, 0x00), True) # Fast 100msec (地磁気,加速度)
#    alps.writeCharacteristic(0x0018, struct.pack('<bbbb', 0x06, 0x04, 0x7A, 0x01), True) # Fast 250msec (地磁気,加速度)
      alps.writeCharacteristic(0x0018, struct.pack('<bbbb', 0x05, 0x04, 0x3C, 0x00), True) # Slow 1sec (気圧,温度,湿度,UV,照度)

#    alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x21, 0x03, 0x01), True)
#   alps.writeCharacteristic(0x0018, struct.pack('<bbbb', 0x10, 0x04, 0x01, 0x00), True)

      alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x24, 0x03, 0x01), True) #自動status通知

#alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x02, 0x03, 0x02), True) # 加速度±8G
      alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x2F, 0x03, 0x01), True) # 設定内容保存
      alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x20, 0x03, 0x01), True) # センサ計測開始

# Main loop --------
      while True:
          if alps.waitForNotifications(1.0):
          # handleNotification() was called
              continue
          print('waiting...')
# Perhaps do something else here
    
    except Exception as e:
      params = {'message' : "Error occured on sensor{}.{}".format(sensor_number, str(e))}
      requests.post(g.LINE_URL, headers = g.headers, oparams = params)


if __name__ == "__main__":
    args = sys.argv
    sensor_number = args[1]
    main(sensor_number)
 
