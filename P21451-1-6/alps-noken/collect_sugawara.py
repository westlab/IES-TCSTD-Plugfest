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
import requests #LINEに通知するために使う
import global_variable as g
 
def s16(value):
    return -(value & 0b1000000000000000) | (value & 0b0111111111111111)


class NtfyDelegate(btle.DefaultDelegate):
    def __init__(self, params, mac_add, sensor_number_passed):
        self.name = mac_add #self.nameにセンサーのMacアドレスを代入
        self.sensor_number = sensor_number_passed
        self.idx = -1
        self.date= None
        self.time = None

        # ... initialise here
 
    def handleNotification(self, cHandle, data): 
        # ... perhaps check cHandle
        # ... process 'data'
        cal = binascii.b2a_hex(data)
        #print(u'handleNotification : {0}-{1}:'.format(cHandle, cal))
        sensor_folder_name = self.sensor_number + '/'
        os.makedirs("./data_save/battery/" + sensor_folder_name, exist_ok=True)
        os.makedirs("./data_save/environment/" + sensor_folder_name, exist_ok=True)

        if int((cal[0:2]), 16) == 0xE0:
            battery = int((cal[16:18] + cal[14:16]), 16)
            print("battery: {}mV".format(battery))
            if battery < 1500:
              params = {
                'message': "バッテリー残量が低下しています\n機体: {}\n現在の容量:{}mV".format(self.name, battery)
              }
              requests.post(g.LINE_URL, headers=g.headers, params=params)

        if int((cal[0:2]), 16) == 0xf2:
            hour = int(cal[36:38],16)
            minute = int(cal[34:36],16)
            second = int(cal[32:34],16)
            idx = int(cal[38:40],16)
            #以下のコードでindexとタイムスタンプを保存しておく
            self.idx = idx
            hour = str(hour).zfill(2)
            minute = str(minute).zfill(2)
            second = str(second).zfill(2)
            self.time = [hour, minute, second]

        if int((cal[0:2]), 16) == 0xf3:
            Pressure = int((cal[6:8] + cal[4:6]), 16) * 860.0/65535 + 250	
            Humidity = 1.0 * (int((cal[10:12] + cal[8:10]), 16) - 896 )/64
            Temperature = 1.0*((int((cal[14:16] + cal[12:14]), 16) -2096)/50)
            UV = int((cal[18:20] + cal[16:18]), 16) / (100*0.388)
            AmbientLight = int((cal[22:24] + cal[20:22]), 16) / (0.05*0.928)
            day = int(cal[32:34],16)
            day = str(day).zfill(2)#zero filled 
            month = int(cal[34:36], 16)
            month = str(month).zfill(2)
            year = int(cal[36:38], 16)
            idx = int(cal[38:40], 16)

            if(self.idx == idx): #data indexがあっているか確認している
              hour, minute, second = self.time

              #for debug
              print("20{}-{}-{}-{}-{}のデータは以下のとおりです".format(year, month, day, hour, minute, second))
              print("Temperature: {} \n Humidity: {} \n Pressure: {} \n AmbientLight: {} \n UV: {} \n".format(Temperature, Humidity, Pressure, AmbientLight, UV))

              #debug end
              date = "20{}-{}-{}".format(year, month, day) #ex.2021-11-30
              file_name = "{}-{}.json".format(date, hour) #ex. 2021-11-30-18.json
              file_path = './data_save/environment/' + "sensor" + sensor_folder_name + "/" + file_name
              if os.path.isfile(file_path): # file exists
                with open(file_path, 'r') as f:
                  data = json.load(f) #既存のデータを読み込み
              else: # file do not exist
                data = {} #dataを初期化して作っておく

                last_hour = (datetime.now() + timedelta(hours = -1)).strftime('%Y-%m-%d-%H')
                trans_file_path = './data_save/environment/' + sensor_folder_name + last_hour + '.json'
                qnap_path = 'SmaAgri/Noken/sonoda/' + sensor_folder_name + last_hour + '.json'
                ssd_path = '/mnt/ssd/sonoda/' + sensor_folder_name + last_hour + '.json'

                ftp = FTP('10.26.0.1','ayu_ftp', passwd = 'WestO831')
                last_hour = (datetime.now() + timedelta(hours = -1)).strftime('%Y-%m-%d-%H')
                if os.path.isfile(trans_file_path):
                    with open(trans_file_path, 'rb') as f:
                        ftp.storlines("STOR /"+ qnap_path, f)
#              
#
                ftp_ssd = FTP('192.168.11.4', 'sonoda', passwd = 'WestO831')
                if os.path.isfile(trans_file_path):
                    with open(trans_file_path, 'rb') as f:
                        ftp_ssd.storlines("STOR " + ssd_path, f)
                

              minute_now = "{}-{}-{}".format(date, hour, minute) #ex. 2021-11-30-18-10
              data[minute_now] = {"Temperature":Temperature,"Humidity":Humidity,"Pressure":Pressure, "UV":UV, "AmbientLight":AmbientLight}
              with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
#



class AlpsSensor(Peripheral):
    def __init__(self,addr):
        Peripheral.__init__(self,addr)
        self.result = 1
 

def main(sensor, sensor_number):
        alps = AlpsSensor(sensor)
        alps.setDelegate( NtfyDelegate(btle.DefaultDelegate, sensor, sensor_number) )
 
        alps.writeCharacteristic(0x0013, struct.pack('<bb', 0x01, 0x00), True)# Custom1 Notify Enable 
        alps.writeCharacteristic(0x0016, struct.pack('<bb', 0x01, 0x00), True)# Custom2 Notify Enable

        alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x2E, 0x03, 0x01), True)#センサーデータリクエスト

        # 以下時刻同期
        now = datetime.now()
        year = int(str(now.year)[2:])
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second
        if minute = 0:
          alps.writeCharacteristic(0x0018, struct.pack('<bbbbbbbbbb', 0x30, 0x0A, 0x00, 0x00, second, minute, hour, day, month, year), True)

# Main loop --------
        count = 0
        while True:
            if alps.waitForNotifications(1.0):
            # handleNotification() was called
                count = 0
                continue
            if count > 4:
              break
            count += 1
            print('waiting...')
        # Perhaps do something else here
        alps.disconnect()

if __name__ == "__main__":
    main(sensor, sensor_number)
