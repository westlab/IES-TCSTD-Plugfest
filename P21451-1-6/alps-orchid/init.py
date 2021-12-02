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

 
def s16(value):
    return -(value & 0b1000000000000000) | (value & 0b0111111111111111)


class NtfyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here
 
    def handleNotification(self, cHandle, data): 
        # ... perhaps check cHandle
        # ... process 'data'
        return 0


class AlpsSensor(Peripheral):
    def __init__(self,addr):
        Peripheral.__init__(self,addr)
        self.result = 1
 

def main(sensor):
  success_flag = False #初期化が成功したかを表すフラッグ
  print("sensor: {} を初期化中".format(sensor))
  while not success_flag: #初期化が成功するまで繰り返す
      try:
        alps = AlpsSensor(sensor)
        alps.setDelegate( NtfyDelegate(btle.DefaultDelegate) )
 
        alps.writeCharacteristic(0x0013, struct.pack('<bb', 0x01, 0x00), True)# Custom1 Notify Enable 
        alps.writeCharacteristic(0x0016, struct.pack('<bb', 0x01, 0x00), True)# Custom2 Notify Enable

        alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x20, 0x03,0x00), True)#計測停止
     
        alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x2F, 0x03, 0x03), True) # (不揮発)保存内容の初期化
        alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x01, 0x03, 0x7c), True) # 地磁気、加速度,気圧,温度,湿度,UV,照度を有効
        alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x04, 0x03, 0x00), True) # slow Mode
        alps.writeCharacteristic(0x0018, struct.pack('<bbbb', 0x05, 0x04, 0x3C, 0x00), True) # Slow 1sec (気圧,温度,湿度,UV,照度)


        alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x24, 0x03, 0x01), True) #自動status通知

        now = datetime.now()
        year = int(str(now.year)[2:])
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second
        alps.writeCharacteristic(0x0018, struct.pack('<bbbbbbbbbb', 0x30, 0x0A, 0x00, 0x00, second, minute, hour, day, month, year), True)
        alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x2F, 0x03, 0x01), True) # 設定内容保存
        alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x20, 0x03, 0x01), True) # センサ計測開始
        alps.disconnect()
        print("初期化成功\n")
        success_flag = True #初期化成功したのでwhileを抜ける

      except Exception as e: #エラーがあった場合実行される 
        print(e)
        print("初期化失敗、30秒後再トライします")
        time.sleep(30)
        pass #エラーが発生した場合特に何もする必要はない

if __name__ == "__main__":
    main(sensor)
 
