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

class confpara:
    def __init__(self):
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
        self.args = parser.parse_args()
        self.vflag = False
        if args.verbose:
            vflag = True
        qflag = False
        if args.quiet:
            qflag = True
        sqflag = False

        f = open(args.config, "r+")
        confdata = yaml.safe_load(f)
        self.host = confdata['mqtthost'] #'192.168.0.10'
        self.port = int(confdata['mqttport']) #1883
        self.topicdop = confdata['spfx']+confdata['tomdop']+confdata['loc']+'/' # publish
        self.topiccop = confdata['spfx']+confdata['tomcop']+confdata['loc'] # subscribe
        self.topiccopres = confdata['spfx']+confdata['tomcop']+confdata['locclient'] # publish
        self.topicd0op = confdata['spfx']+confdata['tomd0op']+confdata['loc'] # subscribe
        self.topicd0opres = confdata['spfx']+confdata['tomd0op']+confdata['locclient'] # publish
        pprint.pprint([topiccop, topicd0op]) #'_1451.1.6(SPFX)/D0(TOM)/LOC'
