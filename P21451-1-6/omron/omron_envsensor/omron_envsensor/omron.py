from __future__ import absolute_import

from logging import getLogger
logger = getLogger(__name__)

import os
from . import util
from . import sensorbeacon
from .ble import BLE

class OmronEnvSensor(BLE):

    def __init__(self, name=None, *args, **kwargs):
        super(OmronEnvSensor, self).__init__(*args, **kwargs)

        if name is None:
            uname = os.uname()
            name = uname[1]

        self.name = name

    def filter(self, result):

        if 'bluetooth_le_subevent_name' in result and result['bluetooth_le_subevent_name'] == 'EVT_LE_ADVERTISING_REPORT':
            for report in result['advertising_reports']:
                if sensorbeacon.verify_beacon_packet(report):
                    logger.debug(report)
                    return sensorbeacon.SensorBeacon(
                            report["peer_bluetooth_address_s"],
                            util.classify_beacon_packet(report),
                            self.name,
                            report["payload_binary"]
                        )
        return None

    @staticmethod
    def callback(r):
        r.debug_print()
