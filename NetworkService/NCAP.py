#!/usr/bin/python3
# -*- coding: utf-8 -*- 
import asyncio
import os
from btle import Peripheral
import struct 
import btle
import binascii
import gmqtt
import sys
import yaml
import argparse
import uuid
import io
import csv
import pprint
import datetime
import temporenc

parser = argparse.ArgumentParser(
    prog = 'NCAP.py',
    usage = 'Receive BLE sensor data and send to MQTT server',
    description= 'PRISM demo for ALPS Smart IoT BLE Sensor module\nYou have to install and Bluetooth modules',
    epilog = 'Programmer: Hiroaki Nishi west@west.yokohama',
    add_help = True)
parser.add_argument('--version', version='%(prog)s 0.1',
    action = 'version',
    help = 'verbose operation (output sensor data)')
parser.add_argument('-v', '--verbose',
    action = 'store_true',
    help = 'verbose operation (output sensor data)',
    default = False)
parser.add_argument('-q', '--quiet',
    action = 'store_true',
    help = 'quiet (does not output data messages)',
    default = False)
parser.add_argument('-c', '--config',
    action = 'store',
    help = 'specify YAML config file',
    default = './config.yml',
    type = str)

args = parser.parse_args()
vflag = False
if args.verbose:
    vflag = True
qflag = False
if args.quiet:
    qflag = True
sqflag = False

f = open(args.config, "r+")
confdata = yaml.safe_load(f)

host = confdata['mqtthost']
#'192.168.0.10'
port = int(confdata['mqttport'])
#1883
topicdop = confdata['spfx']+confdata['tomdop']+confdata['loc']+'/' # publish
topiccop = confdata['spfx']+confdata['tomcop']+confdata['loc'] # subscribe
topiccopres = confdata['spfx']+confdata['tomcop']+confdata['locclient'] # publish
topicd0op = confdata['spfx']+confdata['tomd0op']+confdata['loc'] # subscribe
topicd0opres = confdata['spfx']+confdata['tomd0op']+confdata['locclient'] # publish
#'_1451.1.6(SPFX)/D0(TOM)/LOC'
pprint.pprint([topiccop, topicd0op])
subscriptor = [
    gmqtt.Subscription(topiccop, qos=2), gmqtt.Subscription(topicd0op, qos=2)
]

vgeomagx = {}
vgeomagy = {}
vgeomagz = {}
vaccelx = {}
vaccely = {}
vaccelz = {}
vpres = {}
vhumid = {}
vtemp = {}
vuv = {}
villumi = {}

binblk_read = {
    'netSvcType'        : {'offset': 0,  'type': '<B'},
    'netSvcID'          : {'offset': 1,  'type': '<B'},
    'msgType'           : {'offset': 2,  'type': '<B'},
    'msgLength'         : {'offset': 3,  'type': '<H'},
    'ncapId'            : {'offset': 5,  'type': '<10s'},
    'timId'             : {'offset': 15, 'type': '<10s'},
    'channelId'         : {'offset': 25, 'type': '<4s'},
    'timeDuration'      : {'offset': 29, 'type': '<8B'},
    'samplingMode'      : {'offset': 37, 'type': '<2B'},
    'sessionId'         : {'offset': 39, 'type': '<4s'},
}

binblk_teds = {
    'netSvcType'        : {'offset': 0,  'type': '<B'},
    'netSvcID'          : {'offset': 1,  'type': '<B'},
    'msgType'           : {'offset': 2,  'type': '<B'},
    'msgLength'         : {'offset': 3,  'type': '<H'},
    'ncapId'            : {'offset': 5,  'type': '<10s'},
    'timId'             : {'offset': 15, 'type': '<10s'},
    'channelId'         : {'offset': 23, 'type': '<H'},
    'cmdClassid'        : {'offset': 25, 'type': '<B'},
    'cmdFunctionId'     : {'offset': 26, 'type': '<B'},
    'tedsAccessCode'    : {'offset': 27, 'type': '<B'},
    'tedsOffset'        : {'offset': 38, 'type': '<I'},
    'sessionId'         : {'offset': 46, 'type': '<4s'},
}

uuid0 = '0x00000000000000000000'
uuid1 = '0x00000000000000000001'
# big endian (MSB first)
buuid0 = bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0])
buuid1 = bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1])
#bncapid = bytearray([0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0])
#btimid = bytearray([0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0])
bnull = bytearray([0x0, 0x0, 0x0, 0x0, 0x0]);
# string left char str, 0x0 end

# a.to_bytes(2, 'big')  # 2 bytes big endian
# b'\x00\x80'
# a.to_bytes(4, 'little')  # 4 bytes little endian
# b'\x80\x00\x00\x00'
# int.from_bytes(b'\x00\x80', 'big')
# 128
# int.from_bytes(b'\x80\x00\x00\x00', 'little')
# 128
# str -> byte .encode()
# byte -> str .decode()

def s16(value):
    return -(value & 0b1000000000000000) | (value & 0b0111111111111111)

def on_connect(client, flags, rc, properties):
    print('[CONNECTED {}]'.format(client._client_id))

def on_disconnect(client, packet, exc=None):
    print('[DISCONNECTED {}]'.format(client._client_id))

def on_subscribe(client, mid, qos, properties):
    print('on subscribe')
    print('[SUBCRIBED {} MID: {} QOS: {} PROPERTIES: {}]'.format(client._client_id, mid, qos, properties))

def on_message(client, topic, payload, qos, properties):
    print('[RECV MSG {}] TOPIC: {} PAYLOAD: {} QOS: {} PROPERTIES: {}'
        .format(client._client_id, topic, payload, qos, properties))
    stopic = topic.split('/')
    msg = str(payload.decode('utf-8'))
#    ts = datetime.today().isoformat()
    ts = datetime.datetime.now()
    bts = temporenc.packb(ts)
    sts = str(ts)
    if stopic[1] == 'D0C':
        f = io.StringIO()
        f.write(msg)
        f.seek(0)
        csv_reader = csv.reader(f)
        rmsg = [row for row in csv_reader]
        f.close()
        pprint.pprint(rmsg)
        for mline in rmsg:
            if mline[0]+mline[1]+mline[2] == '211':
                print('Read Sensor Data COP')
                print('msgLength', mline[3])
                print('ncapId', mline[4])
                print('timId', mline[5])
                print('channelid', mline[6])
                print('timeout', mline[7])
                print('samplingMode', mline[8])
                print('discoverlyId', mline[9])
                chid = int(mline[6])
                if mline[4] == uuid0: # short[5]
                    if mline[5] == '0x0000000000000000':
                        print(topiccopres)
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vtemp[chid])+','+sts+','+mline[9])
                        print("Read TEMP")
                    elif mline[5] == '0x0000000000000001':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vhumid[chid])+','+sts+','+mline[9])
                        print("Read HUMID")
                    elif mline[5] == '0x0000000000000002':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vpres[chid])+','+sts+','+mline[9])
                        print("Read PRESS")
                    elif mline[5] == '0x0000000000000003':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vuv[chid])+','+sts+','+mline[9])
                        print("Read UV")
                    elif mline[5] == '0x0000000000000004':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(villumi[chid])+','+sts+','+mline[9])
                        print("Read ILLUMI")
                    elif mline[5] == '0x0000000000000005':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vgeomagx[chid])+','+sts+','+mline[9])
                        print("Read GEOMAGX")
                    elif mline[5] == '0x0000000000000006':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vgeomagy[chid])+','+sts+','+mline[9])
                        print("Read GEOMAGY")
                    elif mline[5] == '0x0000000000000007':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vgeomagz[chid])+','+sts+','+mline[9])
                        print("Read GEOMAGZ")
                    elif mline[5] == '0x0000000000000008':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vaccelx[chid])+','+sts+','+mline[9])
                        print("Read ACCELX")
                    elif mline[5] == '0x0000000000000009':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vaccely[chid])+','+sts+','+mline[9])
                        print("Read ACCELY")
                    elif mline[5] == '0x000000000000000a':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vaccelz[chid])+','+sts+','+mline[9])
                        print("Read ACCELZ")
                    else:
                        print("timId Error")
                else:
                    print("ncapId Error")
            elif mline[0]+mline[1]+mline[2] == '321':
                print("Read TEDS Data COP")
                print('msgLength', mline[3])
                print('ncapId', mline[4])
                print('timId', mline[5])
                print('channelid', mline[6])
                print('cmdClassId = 1', mline[7])
                print('cmdFunctionId = 2', mline[8])
                print('TedsAccessCode = 4', mline[9])
                print('tedsOffset', mline[10])
                print('timeout', mline[11])
                print('discoverlyId', mline[12])
                if mline[4] == uuid0:
                    chid = int(mline[6])
                    if mline[5] == '0x0000000000000000':
                        client.publish(topiccopres, '3,2,2,0,0,uuid0,uuid0,'+mline[6]+','+mline[10]+','+mline[12]+'TEMP_TEDS')
                        print("Read TEMP TEDS")
                    elif mline[5] == '0x0000000000000001':
                        client.publish(topiccopres, '3,2,2,0,0,uuid0,uuid0,'+mline[6]+','+mline[10]+','+mline[12]+'HUMID_TEDS')
                        print("Read HUMID TEDS")
                    elif mline[5] == '0x0000000000000002':
                        client.publish(topiccopres, '3,2,2,0,0,uuid0,uuid0,'+mline[6]+','+mline[10]+','+mline[12]+'PRES_TEDS')
                        print("Read PRESS TEDS")
                    elif mline[5] == '0x0000000000000003':
                        client.publish(topiccopres, '3,2,2,0,0,uuid0,uuid0,'+mline[6]+','+mline[10]+','+mline[12]+'UV_TEDS')
                        print("Read UV TEDS")
                    elif mline[5] == '0x0000000000000004':
                        client.publish(topiccopres, '3,2,2,0,0,uuid0,uuid0,'+mline[6]+','+mline[10]+','+mline[12]+'ILLUMI_TEDS')
                        print("Read ILLUMI TEDS")
                    elif mline[5] == '0x0000000000000005':
                        client.publish(topiccopres, '3,2,2,0,0,uuid0,uuid0,'+mline[6]+','+mline[10]+','+mline[12]+'GEOMAGX_TEDS')
                        print("Read GEOMAGX TEDS")
                    elif mline[5] == '0x0000000000000006':
                        client.publish(topiccopres, '3,2,2,0,0,uuid0,uuid0,'+mline[6]+','+mline[10]+','+mline[12]+'GEOMAGY_TEDS')
                        print("Read GEOMAGY TEDS")
                    elif mline[5] == '0x0000000000000007':
                        client.publish(topiccopres, '3,2,2,0,0,uuid0,uuid0,'+mline[6]+','+mline[10]+','+mline[12]+'GEOMAGZ_TEDS')
                        print("Read GEOMAGZ TEDS")
                    elif mline[5] == '0x0000000000000008':
                        client.publish(topiccopres, '3,2,2,0,0,uuid0,uuid0,'+mline[6]+','+mline[10]+','+mline[12]+'ACCELX_TEDS')
                        print("Read ACCELX TEDS")
                    elif mline[5] == '0x0000000000000009':
                        client.publish(topiccopres, '3,2,2,0,0,uuid0,uuid0,'+mline[6]+','+mline[10]+','+mline[12]+'ACCELY_TEDS')
                        print("Read ACCELY TEDS")
                    elif mline[5] == '0x000000000000000a':
                        client.publish(topiccopres, '3,2,2,0,0,uuid0,uuid0,'+mline[6]+','+mline[10]+','+mline[12]+'ACCELZ_TEDS')
                        print("Read ACCELZ TEDS")
                    else:
                        print("timId Error")
                else:
                    print("ncapId Error")
    elif stopic[1] == 'D0':
        mline = {}
        if msg[0:3].encode() == b'\x02\x01\x01':
            for k, v in binblk_read.items():
                t_offset = v['offset']
                mline[k] = struct.unpack_from(v['type'], msg.encode(), t_offset)[0]
                print(k+': ',mline[k])
            print('ncapId: ', mline['ncapId'], ' buuid0: ',  buuid0)
            if mline['ncapId'] == buuid0:
                print(mline['timId'])
                sbp = bytearray([0x2, 0x1, 0x2, 0x0, 0x0, 0x0, 0x0])
                chid = int.from_bytes(mline['channelId'], 'big')
                print(mline['channelId'])
                print('chid:',chid)
                if mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]):
                    client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+(vtemp[chid].encode()+bnull)[0:5]+bts+bytearray(mline['sessionId']))
                    print("Read TEMP")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1]):
                    client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+(vhumid[chid].encode()+bnull)[0:5]+bts+bytearray(mline['sessionId']))
                    print("Read HUMID")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x2]):
                    client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+(vpres[chid].encode()+bnull)[0:5]+bts+bytearray(mline['sessionId']))
                    print("Read PRESS")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3]):
                    client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+(vuv[chid].encode()+bnull)[0:5]+bts+bytearray(mline['sessionId']))
                    print("Read UV")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x4]):
                    client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+(villumi[chid].encode()+bnull)[0:5]+bts+bytearray(mline['sessionId']))
                    print("Read ILLUMI")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x5]):
                    client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+(vgeomagx[chid].encode()+bnull)[0:5]+bts+bytearray(mline['sessionId']))
                    print("Read GEOMAGX")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x6]):
                    client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+(vgeomagy[chid].encode()+bnull)[0:5]+bts+bytearray(mline['sessionId']))
                    print("Read GEOMAGY")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7]):
                    client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+(vgeomagz[chid].encode()+bnull)[0:5]+bts+bytearray(mline['sessionId']))
                    print("Read GEOMAGZ")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x8]):
                    client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+(vaccelx[chid].encode()+bnull)[0:5]+bts+bytearray(mline['sessionId']))
                    print("Read ACCELX")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x9]):
                    client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+(vaccely[chid].encode()+bnull)[0:5]+bts+bytearray(mline['sessionId']))
                    print("Read ACCELY")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xa]):
                    client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+(vaccelz[chid].encode()+bnull)[0:5]+bts+bytearray(mline['sessionId']))
                    print("Read ACCELZ")
                else:
                    print("timId Error")
            else:
                print("ncapId Error")
        elif msg[0:3].encode() == b'\x03\x02\x01':
            for k, v in binblk_teds.items():
                t_offset = v['offset']
                mline[k] = struct.unpack_from(v['type'], msg.encode(), t_offset)
            if mline['ncapId'] == uuid0:
                sbp = bytearray([0x3, 0x2, 0x2, 0x0, 0x0])
                if mline['timId'] == 0:
                  client.publish(topicd0opres, sbp+buuid0+buuid0+mline['channelId']+mline[10]+mline['sessionId']+'TEMP_TEDS')
                  print("Read TEMP TEDS")
                elif mline['timId'] == 1:
                  client.publish(topicd0opres, sbp+buuid0+buuid0+mline['channelId']+mline[10]+mline['sessionId']+'HUMID_TEDS')
                  print("Read HUMID TEDS")
                elif mline['timId'] == 2:
                  client.publish(topicd0opres, sbp+buuid0+buuid0+mline['channelId']+mline[10]+mline['sessionId']+'PRES_TEDS')
                  print("Read PRESS TEDS")
                elif mline['timId'] == 3:
                  client.publish(topicd0opres, sbp+buuid0+buuid0+mline['channelId']+mline[10]+mline['sessionId']+'UV_TEDS')
                  print("Read UV TEDS")
                elif mline['timId'] == 4:
                  client.publish(topicd0opres, sbp+buuid0+buuid0+mline['channelId']+mline[10]+mline['sessionId']+'ILLUMI_TEDS')
                  print("Read ILLUMI TEDS")
                elif mline['timId'] == 5:
                  client.publish(topicd0opres, sbp+buuid0+buuid0+mline['channelId']+mline[10]+mline['sessionId']+'GEOMAGX_TEDS')
                  print("Read GEOMAGX TEDS")
                elif mline['timId'] == 6:
                  client.publish(topicd0opres, sbp+buuid0+buuid0+mline['channelId']+mline[10]+mline['sessionId']+'GEOMAGY_TEDS')
                  print("Read GEOMAGY TEDS")
                elif mline['timId'] == 7:
                  client.publish(topicd0opres, sbp+buuid0+buuid0+mline['channelId']+mline[10]+mline['sessionId']+'GEOMAGZ_TEDS')
                  print("Read GEOMAGZ TEDS")
                elif mline['timId'] == 8:
                  client.publish(topicd0opres, sbp+buuid0+buuid0+mline['channelId']+mline[10]+mline['sessionId']+'ACCELX_TEDS')
                  print("Read ACCELX TEDS")
                elif mline['timId'] == 9:
                  client.publish(topicd0opres, sbp+buuid0+buuid0+mline['channelId']+mline[10]+mline['sessionId']+'ACCELY_TEDS')
                  print("Read ACCELY TEDS")
                elif mline['timId'] == 10:
                  client.publish(topicd0opres, sbp+buuid0+buuid0+mline['channelId']+mline[10]+mline['sessionId']+'ACCELZ_TEDS')
                  print("Read ACCELZ TEDS")
                else:
                    print("timId Error")
            else:
                print("ncapId Error")
    else:
        print("Type of Message Error")

class NtfyDelegate(btle.DefaultDelegate):
    def __init__(self, params, alpsid, client):
        btle.DefaultDelegate.__init__(self)
        self.alpsid = alpsid
        self.client = client
        # ... initialise here
    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        cal = binascii.b2a_hex(data)
        #print(u'handleNotification : {0}-{1}:'.format(cHandle, cal))
        if int((cal[0:2]), 16) == 0xf2:
            GeoMagnetic_X = '{0:.3f}'.format(s16(int((cal[6:8] + cal[4:6]), 16)) * 0.15)
            GeoMagnetic_Y = '{0:.3f}'.format(s16(int((cal[10:12] + cal[8:10]), 16)) * 0.15)
            GeoMagnetic_Z = '{0:.3f}'.format(s16(int((cal[14:16] + cal[12:14]), 16)) * 0.15)
            vgeomagx[self.alpsid] = GeoMagnetic_X
            vgeomagy[self.alpsid] = GeoMagnetic_Y
            vgeomagz[self.alpsid] = GeoMagnetic_Z
            print(self.alpsid, ':Geo-Magnetic X:', GeoMagnetic_X, ' Y:', GeoMagnetic_Y, ' Z:', GeoMagnetic_Z)
            self.client.publish(topicdop+str(self.alpsid)+'/GEOMAGX', GeoMagnetic_X)
            self.client.publish(topicdop+str(self.alpsid)+'/GEOMAGY', GeoMagnetic_Y)
            self.client.publish(topicdop+str(self.alpsid)+'/GEOMAGZ', GeoMagnetic_Z)
            Acceleration_X = '{0:.3f}'.format(1.0 * s16(int((cal[18:20] + cal[16:18]), 16)) / 1024)
            Acceleration_Y = '{0:.3f}'.format(1.0 * s16(int((cal[22:24] + cal[20:22]), 16)) / 1024)
            Acceleration_Z = '{0:.3f}'.format(1.0 * s16(int((cal[26:28] + cal[24:26]), 16)) / 1024)
            vaccelx[self.alpsid] = Acceleration_X
            vaccely[self.alpsid] = Acceleration_Y
            vaccelz[self.alpsid] = Acceleration_Z
            print(self.alpsid, ':Acceleration X:', Acceleration_X, ' Y:', Acceleration_Y, ' Z:', Acceleration_Z)
            self.client.publish(topicdop+str(self.alpsid)+'/ACCELX', Acceleration_X)
            self.client.publish(topicdop+str(self.alpsid)+'/ACCELY', Acceleration_Y)
            self.client.publish(topicdop+str(self.alpsid)+'/ACCELZ', Acceleration_Z)
        if int((cal[0:2]), 16) == 0xf3:
            Pressure = '{0:.3f}'.format(int((cal[6:8] + cal[4:6]), 16) * 860.0/65535 + 250)
            Humidity = '{0:.3f}'.format(1.0 * (int((cal[10:12] + cal[8:10]), 16) - 896 )/64)
            Temperature = '{0:.3f}'.format(1.0*((int((cal[14:16] + cal[12:14]), 16) -2096)/50))
            UV = '{0:.3f}'.format(int((cal[18:20] + cal[16:18]), 16) / (100*0.388))
            AmbientLight = '{0:.3f}'.format(int((cal[22:24] + cal[20:22]), 16) / (0.05*0.928))
            print(self.alpsid, ':Pressure:', Pressure, ' Humidity:', Humidity, ' Temperature:', Temperature)
            self.client.publish(topicdop+str(self.alpsid)+'/PRES', Pressure)
            self.client.publish(topicdop+str(self.alpsid)+'/HUMID', Humidity)
            self.client.publish(topicdop+str(self.alpsid)+'/TEMP', Temperature)
            print(self.alpsid, ':UV:', UV, ' AmbientLight:', AmbientLight)
            self.client.publish(topicdop+str(self.alpsid)+'/UV', UV)
            self.client.publish(topicdop+str(self.alpsid)+'/ILLUMI', AmbientLight)
            vpres[self.alpsid] =  Pressure
            vhumid[self.alpsid] = Humidity
            vtemp[self.alpsid] = Temperature
            vuv[self.alpsid] = UV
            villumi[self.alpsid] = AmbientLight
 
class AlpsSensor(Peripheral):
    def __init__(self, addr):
        Peripheral.__init__(self, addr)
        self.result = 1

async def alpsmain(client):
    print("ALPS", client)
    print(' - alps connect', host, port)
    await client.connect(host, port, keepalive=60)
    print('ALPS setup')
    alpsarray = []
    n = 1
    while True:
        keyname = 'alpsmodule'+str(n)
        if keyname in confdata:
            if confdata[keyname] is not None:
                alpsarray.append(AlpsSensor(confdata[keyname]))
                print(" - No.%d : %s added" % (n, confdata[keyname]))
            n += 1
        else:
            break
    if n == 1:
        print('Cannot find alpsmodule1 in your configuration file.')
        sys.exit()
    print('ALPS module ready')
    for i,a in enumerate(alpsarray):
        a.setDelegate( NtfyDelegate(btle.DefaultDelegate, i+1, client) )
        print("Node:",i+1)

        #Hybrid MAG ACC8G　100ms　/ Other 1s
        # code - meaning
        a.writeCharacteristic(0x0013, struct.pack('<bb', 0x01, 0x00), True)
        # Custom1 Notify Enable 
        a.writeCharacteristic(0x0016, struct.pack('<bb', 0x01, 0x00), True)
        # Custom2 Notify Enable
        a.writeCharacteristic(0x0018, struct.pack('<bbb', 0x2F, 0x03, 0x03), True)
        # (不揮発)保存内容の初期化
        a.writeCharacteristic(0x0018, struct.pack('<bbb', 0x01, 0x03, 0x7F), True)
        # 地磁気、加速度,気圧,温度,湿度,UV,照度を有効
        a.writeCharacteristic(0x0018, struct.pack('<bbb', 0x04, 0x03, 0x04), True)
        # Hybrid Mode
        # a.writeCharacteristic(0x0018, struct.pack('<bbbb', 0x06, 0x04, 0x64, 0x00), True) # Fast 100msec (地磁気,加速度)
        fastsample = confdata.get('fastsample')
        if fastsample is not None:
            faststime = abs(int(fastsample))
            if(faststime > 999):
                faststime = 999
            fstimel = faststime % 128
            fstimeh = int(faststime/128)
            fstimelstr = format(fstimel, '08x')
            fstimehstr = format(fstimeh, '08x')
            fsstrl = int(fstimelstr[-2:], 16)
            fsstrh = int(fstimehstr[-2:], 16)
            a.writeCharacteristic(0x0018, struct.pack('<bbbb', 0x06, 0x04, fsstrl, fsstrh), True) 
        else:
            a.writeCharacteristic(0x0018, struct.pack('<bbbb', 0x06, 0x04, 0x7A, 0x01), True) 
        # Fast 250msec (地磁気,加速度)
        slowsample = confdata.get('slowsample')
        if slowsample is not None:
            slowstime = abs(int(slowsample))
            if slowstime > 255:
                slowstime = 255
            a.writeCharacteristic(0x0018, struct.pack('<bbbb', 0x05, 0x04, slowstime, 0x00), True)
        else:
            a.writeCharacteristic(0x0018, struct.pack('<bbbb', 0x05, 0x04, 0x01, 0x00), True)
        # Slow 1sec (気圧,温度,湿度,UV,照度)     
        a.writeCharacteristic(0x0018, struct.pack('<bbb', 0x02, 0x03, 0x01), True)
        # 加速度±4G
        a.writeCharacteristic(0x0018, struct.pack('<bbb', 0x2F, 0x03, 0x01), True)
        # 設定内容保存
        a.writeCharacteristic(0x0018, struct.pack('<bbb', 0x20, 0x03, 0x01), True)
        # センサ計測開始
    # Main loop --------
    print('Notification wait')
    while True:
        for i,a in enumerate(alpsarray):
            if a.waitForNotifications(1.0):
                # handleNotification() was called
                continue
            # Perhaps do something else here
#        await asyncio.Event().wait()
        try:
            await asyncio.wait_for(asyncio.Event().wait(), timeout=0.1)
            print('end')
            break
        except asyncio.TimeoutError:
            pass

async def mqttmain(clientm):
    print('mqttmain')
    print(' - mqtt connect', host, port)
    await clientm.connect(host, port, keepalive=60)
    print(' - subscribe')
    clientm.subscribe(subscriptor, subscription_identifier=len(subscriptor))
    await asyncio.Event().wait()

if __name__ == '__main__':
    print('start')
    if sys.version_info[0] != 3:
        print("Version 3 is required")
    print('MQTT setup')
    node = uuid.getnode()
    mac = uuid.UUID(int=node)
    addr = mac.hex[-12:]
    addrm = addr+'mqtt'
    print(' - Client ID='+addr)
    client = gmqtt.Client(addr)
    clientm = gmqtt.Client(addrm)
    print(' - set callbacks')
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    clientm.on_connect = on_connect
    clientm.on_disconnect = on_disconnect
#    clientm.on_subscribe = on_subscribe
    clientm.on_message = on_message
    loop = asyncio.get_event_loop()
    gather = asyncio.gather(
        alpsmain(client), mqttmain(clientm)
    )
    loop.run_until_complete(gather)
