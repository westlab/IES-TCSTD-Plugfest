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
import ipaddress


'''
msgType: Reserved 0 Command 1 Reply 2 Announcement 3 Notification 4 Callback 5
addressType: IPv4 1 IPv6 2
UUID field and subfields arrangement:
    Location (48 bits) Byte 15-10 encodes latitude (24 bits) and longitude (24 bits)
    Manufacturer (24 bits) Byte 9-7
    Year (16 bits) Byte 6-5 from the 0 AD base year.
    Time (40 bits) Byte 4-0
'''

ncap_announcement = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 1},
    'msgType'           : {'type': '<B', 'const': 3},
    'msgLength'         : {'type': '<H'},
    'ncapId'            : {'type': '<16B'},
    'ncapName'          : {'type': '<16s'},
    'addressType'       : {'type': '<B', 'cmd':'addrtype'},
    'ncapAddress'       : {'type': '$addrtype$', 'cmd':'addr'},
}

ncap_tim_announcement = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 2},
    'msgType'           : {'type': '<B', 'const': 3},
    'msgLength'         : {'type': '<H'},
    'ncapId'            : {'type': '<16B'},
    'timId'             : {'type': '<16B'},
    'timName'           : {'type': '<16s'},
}

ncap_tim_transducer_announcement = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcID'          : {'type': '<B', 'const': 3},
    'msgType'           : {'type': '<B', 'const': 3},
    'msgLength'         : {'type': '<H'},
    'ncapId'            : {'type': '<16B'},
    'timId'             : {'type': '<16B'},
    'transducerChannelId'   : {'offset': 37, 'type': '<16B'},
    'transducerChannelName' : {'offset': 53, 'type': '<16s'},
}

ncap_discovery_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 4},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H'},
    'appId'             : {'type': '<16B'},
    'timeout'           : {'type': '<8B'},
}

ncap_discovery_rep = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 4},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H'},
    'errorCode'         : {'type': '<H'},
    'appId'             : {'type': '<16B'},
    'ncapId'            : {'type': '<16B'},
    'ncapName'          : {'type': '<16s'},
    'addressType'       : {'type': '<10s', 'cmd':'addrtype'},
    'ncapAddress'       : {'type': '$addrtype$', 'cmd':'addr'},
}

ncap_tim_discovery_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 5},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H'},
    'ncapId'            : {'type': '<16B'},
    'timeout'           : {'type': '<8B'},
}

ncap_tim_discovery_rep = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 5},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H'},
    'errorCode'         : {'type': '<H'},
    'numOfTims'         : {'type': '<2B', 'cmd':'num'},
    'timIds'            : {'type': '<16B', 'cmd':'array'},
    'timNames'          : {'type': '<16s', 'cmd':'array'},
}

ncap_tim_transducer_discovery_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 6},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H'},
    'ncapId'            : {'type': '<16B'},
    'timId'             : {'type': '<16B'},
    'timeout'           : {'type': '<8B'},
}

ncap_tim_transducer_discovery_rep = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 6},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H'},
    'errorCode'         : {'type': '<H'},
    'numOfTransducerChannels'   : {'type': '<2B', 'cmd':'num'},
    'transducerChannelIds'      : {'type': '<16B', 'cmd': 'array'},
    'transducerChannelNames'    : {'type': '<16s', 'cmd': 'array'},

}

Synchronous_read_transducer_sample_data_from_a_channel_of_a_TIM = {
    'netSvcType'        : {'type': '<B', 'const': 2},
    'netSvcId'          : {'type': '<B', 'const': 1},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H'},
    'ncapId'            : {'type': '<16B'},
    'timId'             : {'type': '<16B'},
    'channelId'         : {'type': '<2B'},
    'samplingMode'      : {'type': '<B'},
    'timeout'           : {'type': '<8B'},
}

Read_TEDS_cmd = {
    'netSvcType'        : {'type': '<B'},
    'netSvcId'          : {'type': '<B'},
    'msgType'           : {'type': '<B'},
    'msgLength'         : {'type': '<H'},
    'ncapId'            : {'type': '<16B'},
    'timId'             : {'type': '<16B'},
    'channelId'         : {'type': '<2B'},
    'cmdClassid'        : {'type': '<B', 'const': 1}, # common cmd
    'cmdFunctionId'     : {'type': '<B', 'const': 2}, # Read TEDS
    'tedsAccessCode'    : {'type': '<B'},
    'tedsOffset'        : {'type': '<4B'},
    'timeout'           : {'type': '<8B'},
}

class tpl2msg:
    def __init__(self, tpl):
        self.tpl = tpl
        self.offset = 0
        self.buffer = ""
        self.rethash = []
        loc = 0

    def decode(self, entcode):
        self.buffer = ""
        self.rethash = []
        loc = 0
        for k, v in self.tpl.items():
            if('type' in v.keys()):
                if('cmd' in v.keys()):
                    if('num' in v['cmd']):
                        numof = int(struct.unpack('<B', entcode, loc))
                        print("numOf:", k, numof)
                        self.rethash[k] = numof
                        loc += struct.calcsize(v['type'])
                    elif('addrtype' in v['cmd']):
                        addrtype = int(struct.unpack('<B', entcode, loc))
                        print("addrType:", k, addrtype)
                        self.rethash[k] = addrtype
                        loc += struct.calcsize(v['type'])
                    elif('addr' in v['cmd']):
                        if 1 == addrtype:
                            ipent = ipaddress.ip_address(struct.unpack('<4B', entcode, loc))
                        elif 2 == addrtype:
                            ipent = ipaddress.ip_address(struct.unpack('<8B', entcode, loc))
                        self.rethash[k] = ipent 
                        loc += struct.calcsize(v['type'])
                    elif('array' == v['cmd']):
                        ent = []
                        for i in range(numof):
                            ent.append(struct.unpack_from(v['type'], entcode, loc))
                            loc += struct.calcsize(v['type'])
                        self.rethash[k] = ent
                    else:
                        print("Error: unknown cmd", v['cmd'])
                else:
                    self.rethash[k] = struct.unpack_from(v['type'], entcode, loc)
                    loc += struct.calcsize(v['type'])
            else:
                print("Error: no type in ", k)
        return self.rethash

    def encode(self, enthash):
        loc = 0
        self.buffer = ""
        for k, v in self.tpl.items():
            if('type' in v.keys()):
                if('cmd' in v.keys()):
                    if('num' in v['cmd']):
                        numof = enthash[k]
                        print("numOf:", k, numof)
                        struct.pack_into(v['type'], self.buffer, loc, numof)
                        loc += struct.calcsize(v['type'])
                    elif('addrtype' in v['cmd']):
                        addrtype = enthash[k]
                        print("addrType:", k, addrtype)
                        struct.pack_into(v['type'], self.buffer, loc, addrtype)
                        loc += struct.calcsize(v['type'])
                    elif('addr' in v['cmd']):
                        if 1 == addrtype:
                            ipent = ipaddress.packed(enthash[k])
                        elif 2 == addrtype:
                            ipent = ipaddress.packed(enthash[k])
                        struct.pack_into(v['type'], self.buffer, loc, ipent)
                        loc += struct.calcsize(v['type'])
                    elif('array' == v['cmd']):
                        ent = []
                        for i in range(numof):
                            struct.pack_into(v['type'], self.buffer, loc, enthash[k,i])
                            loc += struct.calcsize(v['type'])
                    else:
                        print("Error: unknown cmd", v['cmd'])
                else:
                    struct.pack_into(v['type'], self.buffer, loc, enthash[k])
                    loc += struct.calcsize(v['type'])
            else:
                print("Error: no type in ", k)
        return self.buffer

# test
ncap_announcement_func = tpl2msg(ncap_announcement)
ncap_tim_announcement_func = tpl2msg(ncap_tim_announcement)
ncap_tim_transducer_announcement_func = tpl2msg(ncap_tim_transducer_announcement)
ncap_discovery_cmd_func = tpl2msg(ncap_discovery_cmd)
ncap_discovery_rep_func = tpl2msg(ncap_discovery_rep)
ncap_tim_discovery_cmd_func = tpl2msg(ncap_tim_discovery_cmd)
ncap_tim_discovery_rep_func = tpl2msg(ncap_tim_discovery_rep)
ncap_tim_transducer_discovery_cmd_func = tpl2msg(ncap_tim_transducer_discovery_cmd)
ncap_tim_transducer_discovery_rep_func = tpl2msg(ncap_tim_transducer_discovery_rep)
Synchronous_read_transducer_sample_data_from_a_channel_of_a_TIM_func = tpl2msg(Synchronous_read_transducer_sample_data_from_a_channel_of_a_TIM)
Read_TEDS_cmd_func = tpl2msg(Read_TEDS_cmd)
