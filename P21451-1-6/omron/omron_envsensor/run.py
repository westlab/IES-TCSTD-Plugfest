#!/usr/bin/env python

from logging import getLogger
logger = getLogger('omron_envsensor')

from omron_envsensor import OmronEnvSensor
from omron_envsensor.util import getHostname
import sys
import os

BLUETHOOTH_DEVICEID = os.environ.get('BLUETHOOTH_DEVICEID', 0)

def main():
    import logging
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    before_seq = None
    o = OmronEnvSensor(getHostname(), BLUETHOOTH_DEVICEID)

    def callback(beacon):
        beacon.debug_print(logger)
        # logger.info(beacon.bt_address)

    o.on_message = callback
    o.init()
    o.loop()

if __name__ == '__main__':
    main()
