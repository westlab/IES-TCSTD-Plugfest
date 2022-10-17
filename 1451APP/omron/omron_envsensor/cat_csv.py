#!/usr/bin/env python

from logging import getLogger
logger = getLogger('omron_envsensor')

from omron_envsensor import OmronEnvSensor
from omron_envsensor.sensorbeacon import csv_header
from omron_envsensor.util import getHostname
import sys
import os

BLUETHOOTH_DEVICEID = os.environ.get('BLUETHOOTH_DEVICEID', 0)

def main():
    sys.stdout.write(csv_header())
    sys.stdout.write("\r\n")

    before_seq = None
    o = OmronEnvSensor(getHostname(), BLUETHOOTH_DEVICEID)

    def callback(beacon):
        sys.stdout.write(beacon.csv_format())
        sys.stdout.write("\r\n")

    o.on_message = callback
    o.init()
    o.loop()

if __name__ == '__main__':
    main()
