#!/usr/bin/python3
import struct 
import array
import binascii
import sys
import yaml
import argparse
import uuid
import io
import csv
import pprint

def confread:
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
    CNF_MQ_host = confdata['mqtthost'] #'192.168.0.10'
    CNF_MQ_port = int(confdata['mqttport']) #1883
    CNF_MQ_topicdop = confdata['spfx']+confdata['tomdop']+confdata['loc']+'/' # publish
    CNF_MQ_topiccop = confdata['spfx']+confdata['tomcop']+confdata['loc'] # subscribe
    CNF_MQ_topiccopres = confdata['spfx']+confdata['tomcop']+confdata['locclient'] # publish
    CNF_MQ_topicd0op = confdata['spfx']+confdata['tomd0op']+confdata['loc'] # subscribe
    CNF_MQ_topicd0opres = confdata['spfx']+confdata['tomd0op']+confdata['locclient'] # publish
    CNF_NS_NCAPanno_interval = confdata['NS_NCAPanno_interval']
    CNF_NS_TIManno_interval = confdata['NS_TIManno_interval']
    CNF_NS_CHanno_interval['NS_CHanno_interval']
    pprint.pprint([topiccop, topicd0op]) #'_1451.1.6(SPFX)/D0(TOM)/LOC'
