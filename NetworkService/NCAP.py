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

from NCAPLIB import Tpl2Msg
from NCAPOP import confread
from NCAPSM import NCAPstatemachine

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
    'channelId'         : {'offset': 25, 'type': '<2s'},
    'timeDuration'      : {'offset': 27, 'type': '<8B'},
    'samplingMode'      : {'offset': 35, 'type': '<2B'},
    'sessionId'         : {'offset': 37, 'type': '<4s'},
}

binblk_teds = {
    'netSvcType'        : {'offset': 0,  'type': '<B'},
    'netSvcID'          : {'offset': 1,  'type': '<B'},
    'msgType'           : {'offset': 2,  'type': '<B'},
    'msgLength'         : {'offset': 3,  'type': '<H'},
    'ncapId'            : {'offset': 5,  'type': '<10s'},
    'timId'             : {'offset': 15, 'type': '<10s'},
    'channelId'         : {'offset': 25, 'type': '<2s'},
    'cmdClassid'        : {'offset': 27, 'type': '<B'},
    'cmdFunctionId'     : {'offset': 28, 'type': '<B'},
    'tedsAccessCode'    : {'offset': 29, 'type': '<B'},
    'tedsOffset'        : {'offset': 30, 'type': '<4s'},
    'timeout'           : {'offset': 34, 'type': '8s'},
    'sessionId'         : {'offset': 42, 'type': '<4s'},
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
                    if mline[5] == '0x00000000000000000000':
                        print(topiccopres)
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vtemp[chid])+','+sts+','+mline[9])
                        print("Read TEMP")
                    elif mline[5] == '0x00000000000000000001':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vhumid[chid])+','+sts+','+mline[9])
                        print("Read HUMID")
                    elif mline[5] == '0x00000000000000000002':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vpres[chid])+','+sts+','+mline[9])
                        print("Read PRES")
                    elif mline[5] == '0x00000000000000000003':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vuv[chid])+','+sts+','+mline[9])
                        print("Read UV")
                    elif mline[5] == '0x00000000000000000004':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(villumi[chid])+','+sts+','+mline[9])
                        print("Read ILLUMI")
                    elif mline[5] == '0x00000000000000000005':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vgeomagx[chid])+','+sts+','+mline[9])
                        print("Read GEOMAGX")
                    elif mline[5] == '0x00000000000000000006':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vgeomagy[chid])+','+sts+','+mline[9])
                        print("Read GEOMAGY")
                    elif mline[5] == '0x00000000000000000007':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vgeomagz[chid])+','+sts+','+mline[9])
                        print("Read GEOMAGZ")
                    elif mline[5] == '0x00000000000000000008':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vaccelx[chid])+','+sts+','+mline[9])
                        print("Read ACCELX")
                    elif mline[5] == '0x00000000000000000009':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vaccely[chid])+','+sts+','+mline[9])
                        print("Read ACCELY")
                    elif mline[5] == '0x0000000000000000000a':
                        client.publish(topiccopres, '2,1,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+str(vaccelz[chid])+','+sts+','+mline[9])
                        print("Read ACCELZ")
                    else:
                        print("timId Error")
                        print(mline[5])
                else:
                    print("ncapId Error")
                    print(mline[4])
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
                    if mline[5] == '0x00000000000000000000':
                        client.publish(topiccopres, '3,2,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+mline[10]+','+mline[12]+',TEMP_TEDS')
                        print("Read TEMP TEDS")
                    elif mline[5] == '0x00000000000000000001':
                        client.publish(topiccopres, '3,2,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+mline[10]+','+mline[12]+',HUMID_TEDS')
                        print("Read HUMID TEDS")
                    elif mline[5] == '0x00000000000000000002':
                        client.publish(topiccopres, '3,2,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+mline[10]+','+mline[12]+',PRES_TEDS')
                        print("Read PRES TEDS")
                    elif mline[5] == '0x00000000000000000003':
                        client.publish(topiccopres, '3,2,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+mline[10]+','+mline[12]+',UV_TEDS')
                        print("Read UV TEDS")
                    elif mline[5] == '0x00000000000000000004':
                        client.publish(topiccopres, '3,2,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+mline[10]+','+mline[12]+',ILLUMI_TEDS')
                        print("Read ILLUMI TEDS")
                    elif mline[5] == '0x00000000000000000005':
                        client.publish(topiccopres, '3,2,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+mline[10]+','+mline[12]+',GEOMAGX_TEDS')
                        print("Read GEOMAGX TEDS")
                    elif mline[5] == '0x00000000000000000006':
                        client.publish(topiccopres, '3,2,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+mline[10]+','+mline[12]+',GEOMAGY_TEDS')
                        print("Read GEOMAGY TEDS")
                    elif mline[5] == '0x00000000000000000007':
                        client.publish(topiccopres, '3,2,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+mline[10]+','+mline[12]+',GEOMAGZ_TEDS')
                        print("Read GEOMAGZ TEDS")
                    elif mline[5] == '0x00000000000000000008':
                        client.publish(topiccopres, '3,2,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+mline[10]+','+mline[12]+',ACCELX_TEDS')
                        print("Read ACCELX TEDS")
                    elif mline[5] == '0x00000000000000000009':
                        client.publish(topiccopres, '3,2,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+mline[10]+','+mline[12]+',ACCELY_TEDS')
                        print("Read ACCELY TEDS")
                    elif mline[5] == '0x0000000000000000000a':
                        client.publish(topiccopres, '3,2,2,0,0,'+uuid0+','+mline[5]+','+mline[6]+','+mline[10]+','+mline[12]+',ACCELZ_TEDS')
                        print("Read ACCELZ TEDS")
                    else:
                        print("timId Error")
                        print(mline[5])
                else:
                    print("ncapId Error")
                    print(mline[4])
    elif stopic[1] == 'D0':
        mline = {}
        if msg[0:3].encode() == b'\x02\x01\x01':
            for k, v in binblk_read.items():
                t_offset = v['offset']
                mline[k] = struct.unpack_from(v['type'], msg.encode(), t_offset)[0]
            pprint.pprint(mline)
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
                    print("Read PRES")
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
                    print(mline['timId'])
            else:
                print("ncapId Error")
        elif msg[0:3].encode() == b'\x03\x02\x01':
            for k, v in binblk_teds.items():
                t_offset = v['offset']
                mline[k] = struct.unpack_from(v['type'], msg.encode(), t_offset)[0]
            pprint.pprint(mline)
            if mline['ncapId'] == buuid0:
                sbp = bytearray([0x3, 0x2, 0x2, 0x0, 0x0, 0x0, 0x0])
                if mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]):
                  client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+bytearray(mline['tedsOffset'])+bytearray([0x11, 0x22, 0x33, 0x44])+bytearray(mline['sessionId'])+bytearray('TEMP_BIN_TEDS'.encode()))
                  print("Read TEMP TEDS")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1]):
                  client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+bytearray(mline['tedsOffset'])+bytearray(mline['sessionId'])+bytearray('HUMID_BIN_TEDS'.encode()))
                  print("Read HUMID TEDS")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x2]):
                  client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+bytearray(mline['tedsOffset'])+bytearray(mline['sessionId'])+bytearray('PRES_BIN_TEDS'.encode()))
                  print("Read PRES TEDS")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3]):
                  client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+bytearray(mline['tedsOffset'])+bytearray(mline['sessionId'])+bytearray('UV_BIN_TEDS'.encode()))
                  print("Read UV TEDS")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x4]):
                  client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+bytearray(mline['tedsOffset'])+bytearray(mline['sessionId'])+bytearray('ILLUMI_BIN_TEDS'.encode()))
                  print("Read ILLUMI TEDS")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x5]):
                  client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+bytearray(mline['tedsOffset'])+bytearray(mline['sessionId'])+bytearray('GEOMAGX_BIN_TEDS'.encode()))
                  print("Read GEOMAGX TEDS")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x6]):
                  client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+bytearray(mline['tedsOffset'])+bytearray(mline['sessionId'])+bytearray('GEOMAGY_BIN_TEDS'.encode()))
                  print("Read GEOMAGY TEDS")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7]):
                  client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+bytearray(mline['tedsOffset'])+bytearray(mline['sessionId'])+bytearray('GEOMAGZ_BIN_TEDS'.encode()))
                  print("Read GEOMAGZ TEDS")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x8]):
                  client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+bytearray(mline['tedsOffset'])+bytearray(mline['sessionId'])+bytearray('ACCELX BIN TEDS'.encode()))
                  print("Read ACCELX TEDS")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x9]):
                  client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+bytearray(mline['tedsOffset'])+bytearray(mline['sessionId'])+bytearray('ACCELY BIN TEDS'.encode()))
                  print("Read ACCELY TEDS")
                elif mline['timId'] == bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xa]):
                  client.publish(topicd0opres, sbp+buuid0+mline['timId']+bytearray(mline['channelId'])+bytearray(mline['tedsOffset'])+bytearray(mline['sessionId'])+bytearray('ACCELZ BIN TEDS'.encode()))
                  print("Read ACCELZ TEDS")
                else:
                    print("timId Error")
                    print(mline['timId'])
            else:
                print("ncapId Error")
                print(mline['ncapId'])
    else:
        print("Type of Message Error")

class NCAP:
    def __init__(self):
        print("NCAP setup")

        addr = uuid.UUID(int=uuid.getnode()).hex[-12:] + "mqtt"
        print('MQTT client setup. Client ID:', addr)
        self.client = gmqtt.Client(addr)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message

        print("statemachine setup")
        self.stateMachine = NCAPstatemachine()
    
    def on_connect(self, client, flags, rc, properties):
        print('[CONNECTED {}]'.format(self.client._client_id))

    def on_disconnect(self, client, packet, exc=None):
        print('[DISCONNECTED {}]'.format(client._client_id))

    def on_subscribe(self, client, mid, qos, properties):
        print('on subscribe')
        print('[SUBCRIBED {} MID: {} QOS: {} PROPERTIES: {}]'.format(client._client_id, mid, qos, properties))

    def on_message(self, client, topic, payload, qos, properties):
        """
        送られてきたリクエストを NCAPLIB を使用してパースし，NCAPSM を使用してレスポンスを生成し，返す
        """
        ### TODO implement
        print('[RECV MSG {}] TOPIC: {} PAYLOAD: {} QOS: {} PROPERTIES: {}'
            .format(client._client_id, topic, payload, qos, properties))
        print("TODO: implement on_message")
    
    async def start(self, host, port, subscriptor):
        await self.client.connect(host, port, keepalive=60)
        self.client.subscribe(subscriptor, subscription_identifier=len(subscriptor))
        await asyncio.Event().wait()

if __name__ == '__main__':
    print('demonstration start')
    if sys.version_info[0] != 3:
        print("Version 3 is required")
    
    ncap = NCAP()

    loop = asyncio.get_event_loop()
    gather = asyncio.gather(
        ncap.start("localhost", "1883", subscriptor)
    )
    loop.run_until_complete(gather)
