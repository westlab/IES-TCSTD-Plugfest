# -*- coding: utf-8 -*- 
from btle import Peripheral
import os
import json
import struct 
import btle
import binascii
from datetime import datetime,date,timedelta
from ftplib import FTP


 
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
         
        if int((cal[0:2]), 16) == 0xE0:
            #Buttery = int((cal[14:16] + cal[16:18]), 16)
            Buttery = int((cal[16:18] + cal[14:16]), 16)
            hour_now=datetime.now().strftime("%Y-%m-%d-%H")
            minute_now=datetime.now().strftime("%Y-%m-%d-%H-%M")
            td=timedelta(hours=1)
            trans_hour=datetime.now()-td
            trans_hour=trans_hour.strftime("%Y-%m-%d-%H")

            file_path='./data_save/buttery/'+hour_now+".json"

            if os.path.isfile(file_path):
                with open(file_path,'r') as f:
                    d_update = json.load(f)
                d_update[minute_now] = {"Buttery":Buttery}
                with open(file_path,'w') as f:
                    json.dump(d_update, f, indent=2)



                ftp = FTP('10.26.0.1','ayu_ftp',passwd='WestO831')
               # hour = datetime.now().strftime('%Y-%m-%d-%H')
                path_buttery = './data_save/buttery/'
                server_path = 'SmaAgri/Noken/sonoda/'
                trans_file = trans_hour+'.json'
                with open(path_buttery + trans_file, 'rb') as f:
                    ftp.storlines("STOR /"+server_path + trans_file, f)








            else:
                with open(file_path,'x') as f:
                    f.write('{}')
                with open(file_path, 'r+') as f:
                    all=json.load(f)
                all[minute_now] = {"Buttery":Buttery}
                with open(file_path,'w') as f:
                    json.dump(all, f, indent=2)

        if int((cal[0:2]), 16) == 0xf2:
            GeoMagnetic_X = s16(int((cal[6:8] + cal[4:6]), 16)) * 0.15
            GeoMagnetic_Y = s16(int((cal[10:12] + cal[8:10]), 16)) * 0.15
            GeoMagnetic_Z = s16(int((cal[14:16] + cal[12:14]), 16)) * 0.15
            print('Geo-Magnetic X:{0:.3f} Y:{1:.3f} Z:{2:.3f}'.format(GeoMagnetic_X, GeoMagnetic_Y, GeoMagnetic_Z))
            Acceleration_X = 1.0 * s16(int((cal[18:20] + cal[16:18]), 16)) / 1024
            Acceleration_Y = 1.0 * s16(int((cal[22:24] + cal[20:22]), 16)) / 1024
            Acceleration_Z = 1.0 * s16(int((cal[26:28] + cal[24:26]), 16)) / 1024
            print('Acceleration X:{0:.3f} Y:{1:.3f} Z:{2:.3f}'.format(Acceleration_X, Acceleration_Y, Acceleration_Z))

        if int((cal[0:2]), 16) == 0xf3:
            Pressure = int((cal[6:8] + cal[4:6]), 16) * 860.0/65535 + 250	
            Humidity = 1.0 * (int((cal[10:12] + cal[8:10]), 16) - 896 )/64
            Temperature = 1.0*((int((cal[14:16] + cal[12:14]), 16) -2096)/50)
            UV = int((cal[18:20] + cal[16:18]), 16) / (100*0.388)
            AmbientLight = int((cal[22:24] + cal[20:22]), 16) / (0.05*0.928)
            print('Pressure:{0:.3f} Humidity:{1:.3f} Temperature:{2:.3f} '.format(Pressure, Humidity , Temperature))
            print('UV:{0:.3f} AmbientLight:{1:.3f} '.format(UV, AmbientLight))


            hour_now=datetime.now().strftime("%Y-%m-%d-%H")
            td=timedelta(hours=1)
            trans_hour=datetime.now()-td
            minute_now=datetime.now().strftime("%Y-%m-%d-%H-%M")

            file_path='./data_save/environment/'+hour_now+".json"

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
                hour = datetime.now().strftime('%Y-%m-%d-%H')
                path_environment = './data_save/environment/'
                server_path = 'SmaAgri/Noken/sonoda/'
                trans_hour = trans_hour.strftime("%Y-%m-%d-%H-%M")
                trans_file = './data_save/enironment/'+trans_hour+'.json'
                with open(trans_file, 'rb') as f:
                    ftp.storlines("STOR"+server_path + trans_file, f)
              


class AlpsSensor(Peripheral):
    def __init__(self,addr):
        Peripheral.__init__(self,addr)
        self.result = 1
 

def main():
    alps = AlpsSensor("48:F0:7B:78:4B:6E")
    alps.setDelegate( NtfyDelegate(btle.DefaultDelegate) )
 
    #Hybrid MAG ACC8G　100ms　/ Other 1s
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

    alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x02, 0x03, 0x02), True) # 加速度±8G
    alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x2F, 0x03, 0x01), True) # 設定内容保存
    alps.writeCharacteristic(0x0018, struct.pack('<bbb', 0x20, 0x03, 0x01), True) # センサ計測開始
     
# Main loop --------
    while True:
        if alps.waitForNotifications(1.0):
            # handleNotification() was called
            continue

        print("Waiting...")
        # Perhaps do something else here
if __name__ == "__main__":
    main()
 
