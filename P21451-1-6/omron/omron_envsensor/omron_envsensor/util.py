from logging import getLogger
logger = getLogger(__name__)

import struct
import sys
import os

def packet_as_hex_string(pkt, flag_with_spacing=False,
                         flag_force_capitalize=False):
    packet = []
    space = ""
    if (flag_with_spacing):
        space = " "

    for b in pkt:
        if sys.version < '3':
            b = struct.unpack("<B", b)[0]

        packet.append('{0:02X}'.format(b))

    packet = space.join(packet)
    if (flag_force_capitalize):
        packet = packet.upper()

    return packet

def packed_bdaddr_to_string(bdaddr_packed):
    return ':'.join('%02x' % i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))

def short_bt_address(btAddr):
    return ''.join(btAddr.split(':'))

# From the spec, 5.4.1, page 427 (Core Spec v4.0 Vol 2):
# "Each command is assigned a 2 byte Opcode used to uniquely identify different
# types of commands. The Opcode parameter is divided into two fields, called
# the OpCode Group Field (OGF) and OpCode Command Field (OCF). The OGF occupies
# the upper 6 bits of the Opcode, while the OCF occupies the remaining 10 bits"
def ogf_and_ocf_from_opcode(opcode):
    ogf = opcode >> 10
    ocf = opcode & 0x03FF
    return (ogf, ocf)

def reset_hci():
    # resetting bluetooth dongle
    cmd = "sudo hciconfig hci0 down"
    subprocess.call(cmd, shell=True)
    cmd = "sudo hciconfig hci0 up"
    subprocess.call(cmd, shell=True)

def get_companyid(pkt):
    if sys.version < '3':
        return (struct.unpack("<B", pkt[1])[0] << 8) | \
            struct.unpack("<B", pkt[0])[0]
    return pkt[1] << 8 | pkt[0]

# classify beacon type sent from the sensor
def classify_beacon_packet(report):
    if report["payload_binary"][29:31] in ['IM', b'IM']:
        return "IM"
    elif report["payload_binary"][29:31] in ['EP', b'EP']:
        return "EP"
    return "UNKNOWN"

def c2B(char):
    # character to Byte conversion
    return struct.unpack("B", char)[0]

def c2b(char):
    # character to signed char conversion
    return struct.unpack("b", char)[0]

def c2b_3(char):
    # character to signed char conversion
    if char & 0x80:
        char ^= 0xff
        char += 1
        char = -char
    return char
    return int.from_bytes(int.to_bytes(char, 1, 'little'), 'little', signed=True)

if sys.version > '3':
    c2b = c2b_3
    c2B = lambda char: char

def bytes2ushort(hi, lo):
    ushort_val = ((hi << 8) | lo)
    return ushort_val

def bytes2short(hi, lo):
    val = (hi << 8) | lo
    if (hi & 0b10000000) == 0b10000000:
        val_inv = val ^ 0b1111111111111111
        val_inv = val_inv + 1
        short_val = val_inv * (-1)
    else:
        short_val = val
    return short_val

def ushort2short(val):
    if ((val & 0x8000) == 0x8000):
        val_inv = val ^ 0b1111111111111111
        val_inv = val_inv + 1
        short_val = val_inv * (-1)
    else:
        short_val = val
    return short_val

def getHostname():
    return os.uname()[1]
