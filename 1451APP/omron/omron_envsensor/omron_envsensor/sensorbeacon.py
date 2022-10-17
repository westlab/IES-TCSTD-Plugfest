from __future__ import absolute_import

from logging import getLogger
logger = getLogger(__name__)

import math
import sys
import datetime
import struct
import json

from . import util
from .ble import ADV_TYPE_MANUFACTURER_SPECIFIC_DATA, ADV_TYPE_SHORT_LOCAL_NAME


# constructs
# OMRON company ID (Bluetooth SIG.)
COMPANY_ID = 0x2D5

# BEACON Measured power (RSSI at 1m distance)
BEACON_MEASURED_POWER = -59


def verify_beacon_packet(report):
    # verify received beacon packet format

    # check payload length (31byte)
    if (report["report_metadata_length"] != 31):
        return False
    # check Company ID (OMRON = 0x02D5)
    if (struct.unpack("<B", report["payload_binary"][4])[0] !=
            ADV_TYPE_MANUFACTURER_SPECIFIC_DATA):
        return False
    if (util.get_companyid(report["payload_binary"][5:7]) != COMPANY_ID):
        return False
    # check shortened local name ("IM")
    if (struct.unpack("<B", report["payload_binary"][28])[0] !=
            ADV_TYPE_SHORT_LOCAL_NAME):
        return False
    if ((report["payload_binary"][29:31] != "IM") and
            (report["payload_binary"][29:31] != "EP")):
        return False

    return True


def verify_beacon_packet_3(report):
    # verify received beacon packet format

    # check payload length (31byte)
    if report["report_metadata_length"] != 31:
        return False
    # check Company ID (OMRON = 0x02D5)
    if report["payload_binary"][4] != ADV_TYPE_MANUFACTURER_SPECIFIC_DATA:
        return False
    if util.get_companyid(report["payload_binary"][5:7]) != COMPANY_ID:
        return False
    # check shortened local name ("IM")
    if report["payload_binary"][28] != ADV_TYPE_SHORT_LOCAL_NAME:
        return False
    if report["payload_binary"][29:31] != b'IM' and report["payload_binary"][29:31] != b'EP':
        logger.debug(report['payload_binary'][29:31])
        return False

    return True


if sys.version > '3':
    verify_beacon_packet = verify_beacon_packet_3


# Env Senor (OMRON 2JCIE-BL01 Broadcaster) ####################################
class SensorBeacon:

    # local fields from raw data
    bt_address = ""
    seq_num = 0
    val_temp = 0.0
    val_humi = 0.0
    val_light = 0.0
    val_uv = 0.0
    val_pressure = 0.0
    val_noise = 0.0
    val_di = 0.0
    val_heat = 0.0
    val_ax = 0.0
    val_ay = 0.0
    val_az = 0.0
    val_battery = 0.0

    rssi = -127
    distance = 0
    tick_last_update = 0
    tick_register = 0

    flag_active = False

    sensor_type = "UNKNOWN"
    gateway = "UNKNOWN"


    def __init__(self, bt_address_s, sensor_type_s, gateway_s, pkt):
        self.bt_address = bt_address_s
        self.seq_num = util.c2B(pkt[7])

        self.val_temp = util.bytes2short(
            util.c2B(pkt[9]), util.c2B(pkt[8])) / 100.0
        self.val_humi = util.bytes2ushort(
            util.c2B(pkt[11]), util.c2B(pkt[10])) / 100.0
        self.val_light = util.bytes2ushort(
            util.c2B(pkt[13]), util.c2B(pkt[12]))
        self.val_uv = util.bytes2ushort(
            util.c2B(pkt[15]), util.c2B(pkt[14])) / 100.0
        self.val_pressure = util.bytes2ushort(
            util.c2B(pkt[17]), util.c2B(pkt[16])) / 10.0
        self.val_noise = util.bytes2ushort(
            util.c2B(pkt[19]), util.c2B(pkt[18])) / 100.0
        self.val_battery = (util.c2B(pkt[26]) + 100) * 10.0

        if sensor_type_s == "IM":
            self.val_ax = util.bytes2short(
                util.c2B(pkt[21]), util.c2B(pkt[20])) / 10.0
            self.val_ay = util.bytes2short(
                util.c2B(pkt[23]), util.c2B(pkt[22])) / 10.0
            self.val_az = util.bytes2short(
                util.c2B(pkt[25]), util.c2B(pkt[24])) / 10.0
            self.val_di = 0.0
            self.val_heat = 0.0
            self.calc_factor()
        elif sensor_type_s == "EP":
            self.val_ax = 0.0
            self.val_ay = 0.0
            self.val_az = 0.0
            self.val_di = util.bytes2short(
                util.c2B(pkt[21]), util.c2B(pkt[20])) / 100.0
            self.val_heat = util.bytes2short(
                util.c2B(pkt[23]), util.c2B(pkt[22])) / 100.0
        else:
            self.val_ax = 0.0
            self.val_ay = 0.0
            self.val_az = 0.0
            self.val_di = 0.0
            self.val_heat = 0.0
            self.calc_factor()

        self.rssi = util.c2b(pkt[-1])
        self.distance = self.return_accuracy(
            self.rssi, BEACON_MEASURED_POWER)

        self.tick_register = datetime.datetime.now()
        self.tick_last_update = self.tick_register
        self.flag_active = True

        self.sensor_type = sensor_type_s
        self.gateway = gateway_s


    def return_accuracy(self, rssi, power):  # rough distance in meter
        RSSI = abs(rssi)
        if RSSI == 0:
            return -1
        if power == 0:
            return -1

        ratio = RSSI * 1.0 / abs(power)
        if ratio < 1.0:
            return pow(ratio, 8.0)
        accuracy = 0.69976 * pow(ratio, 7.7095) + 0.111
        # accuracy = 0.89976 * pow(ratio, 7.7095) + 0.111
        return accuracy


    def check_diff_seq_num(self, sensor_beacon):
        result = False
        if (self.seq_num != sensor_beacon.seq_num):
            result = True
        else:
            result = False
        return result


    def update(self, sensor_beacon):
        sensor_beacon.sensor_type = self.sensor_type
        sensor_beacon.gateway = self.gateway
        sensor_beacon.seq_num = self.seq_num
        sensor_beacon.val_temp = self.val_temp
        sensor_beacon.val_humi = self.val_humi
        sensor_beacon.val_light = self.val_light
        sensor_beacon.val_uv = self.val_uv
        sensor_beacon.val_pressure = self.val_pressure
        sensor_beacon.val_noise = self.val_noise
        sensor_beacon.val_di = self.val_di
        sensor_beacon.val_heat = self.val_heat
        sensor_beacon.val_ax = self.val_ax
        sensor_beacon.val_ay = self.val_ay
        sensor_beacon.val_az = self.val_az
        sensor_beacon.val_battery = self.val_battery
        sensor_beacon.rssi = self.rssi
        sensor_beacon.distance = self.distance
        sensor_beacon.tick_last_update = self.tick_last_update
        sensor_beacon.flag_active = True


    def calc_factor(self):
        self.val_di = self.__discomfort_index_approximation(
            self.val_temp, self.val_humi)
        self.val_heat = self.__wbgt_approximation(
            self.val_temp, self.val_humi, flag_outside=False)


    # Index Calc ###
    def __discomfort_index_approximation(self, temp, humi):
        return (0.81 * temp) + 0.01 * humi * ((0.99 * temp) - 14.3) + 46.3


    def __wbgt_approximation(self, temp, humi, flag_outside=False):
        wbgt = 0
        if (temp < 0):
            temp = 0
        if (humi < 0):
            humi = 0
        if (humi > 100):
            humi = 100
        wbgt = (0.567 * temp) + 0.393 * (
            humi / 100 * 6.105 * math.exp(
                17.27 * temp / (237.7 + temp))) + 3.94
        if not flag_outside:
            wbgt = (wbgt + (1.1 * (1 - (humi / 62) * 1.6)) * (temp - 30) *
                    0.17 - abs(temp - 30) * 0.09) / 1.135
        return wbgt


    def debug_print(self, logger=logger):
        logger.info("gateway = %s", self.gateway)
        logger.info("type = %s", self.sensor_type)
        logger.info("bt_address = %s", self.bt_address)
        logger.info("seq_num = %s", self.seq_num)
        logger.info("val_temp = %s", self.val_temp)
        logger.info("val_humi = %s", self.val_humi)
        logger.info("val_light = %s", self.val_light)
        logger.info("val_uv = %s", self.val_uv)
        logger.info("val_pressure = %s", self.val_pressure)
        logger.info("val_noise = %s", self.val_noise)
        logger.info("val_di = %s", self.val_di)
        logger.info("val_heat = %s", self.val_heat)
        logger.info("val_ax = %s", self.val_ax)
        logger.info("val_ay = %s", self.val_ay)
        logger.info("val_az = %s", self.val_az)
        logger.info("val_battery = %s", self.val_battery)
        logger.info("rssi = %s", self.rssi)
        logger.info("distance = %s", self.distance)
        logger.info("tick_register = %s", self.tick_register)
        logger.info("tick_last_update = %s", self.tick_last_update)
        logger.info("flag_active = %s", self.flag_active)


    def csv_format(self):
        str_data = str(self.tick_last_update) + "," + \
                   str(self.gateway) + "," + \
                   str(self.bt_address) + "," + \
                   str(self.sensor_type) + "," + \
                   str(self.rssi) + "," + \
                   str(self.distance) + "," + \
                   str(self.seq_num) + "," + \
                   str(self.val_battery) + "," + \
                   str(self.val_temp) + "," + \
                   str(self.val_humi) + "," + \
                   str(self.val_light) + "," + \
                   str(self.val_uv) + "," + \
                   str(self.val_pressure) + "," + \
                   str(self.val_noise) + "," + \
                   str(self.val_di) + "," + \
                   str(self.val_heat) + "," + \
                   str(self.val_ax) + "," + \
                   str(self.val_ay) + "," + \
                   str(self.val_az)
        return str_data


    def json_format(self):
        return json.dumps({
            'tick_last_update': self.tick_last_update.isoformat(),
            'gateway': self.gateway,
            'address': self.bt_address,
            'sensor_type': self.sensor_type,
            'rssi': self.rssi,
            'distance': self.distance,
            'seq_num': self.seq_num,
            'battery': self.val_battery,
            'temp': self.val_temp,
            'humi': self.val_humi,
            'light': self.val_light,
            'uv': self.val_uv,
            'pressure': self.val_pressure,
            'noise': self.val_noise,
            'di': self.val_di,
            'heat': self.val_heat,
            'ax': self.val_ax,
            'ay': self.val_ay,
            'az': self.val_az
        })


def csv_header():
    str_head = "Time" + "," + \
               "Gateway" + "," + \
               "Address" + "," + \
               "Type" + "," + \
               "RSSI (dBm)" + "," + \
               "Distance (m)" + "," + \
               "Sequence No." + "," + \
               "Battery (mV)" + "," + \
               "Temperature (degC)" + "," + \
               "Humidity (%%RH)" + "," + \
               "Light (lx)" + "," + \
               "UV Index" + "," + \
               "Pressure (hPa)" + "," + \
               "Noise (dB)" + "," + \
               "Discomfort Index" + "," + \
               "Heat Stroke Risk" + "," + \
               "Accel.X (mg)" + "," + \
               "Accel.Y (mg)" + "," + \
               "Accel.X (mg)"
    return str_head
