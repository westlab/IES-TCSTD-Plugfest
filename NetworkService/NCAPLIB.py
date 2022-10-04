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
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'ncapName'          : {'type': '<16s'},
    'addressType'       : {'type': '<B', 'cmd': 'addrtype'},
    'ncapAddress'       : {'type': '$addrtype$', 'cmd': 'addr'},
}

ncap_tim_announcement = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 2},
    'msgType'           : {'type': '<B', 'const': 3},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'timName'           : {'type': '<16s'},
}

ncap_tim_transducer_announcement = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcID'          : {'type': '<B', 'const': 3},
    'msgType'           : {'type': '<B', 'const': 3},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'transducerChannelId'   : {'type': '<16s'},
    'transducerChannelName' : {'type': '<16s'},
}

ncap_discovery_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 4},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'appId'             : {'type': '<16s'},
    'timeout'           : {'type': '<8B'},
}

ncap_discovery_rep = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 4},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'errorCode'         : {'type': '<H'},
    'appId'             : {'type': '<16s'},
    'ncapId'            : {'type': '<16s'},
    'ncapName'          : {'type': '<16s'},
    'addressType'       : {'type': '<10s', 'cmd': 'addrtype'},
    'ncapAddress'       : {'type': '$addrtype$', 'cmd': 'addr'},
}

ncap_tim_discovery_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 5},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'timeout'           : {'type': '<8B'},
}

ncap_tim_discovery_rep = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 5},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'errorCode'         : {'type': '<H'},
    'numOfTims'         : {'type': '<2B', 'cmd': 'num'},
    'timIds'            : {'type': '<16s', 'cmd': 'array'},
    'timNames'          : {'type': '<16s', 'cmd': 'array'},
}

ncap_tim_transducer_discovery_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 6},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'timeout'           : {'type': '<8B'},
}

ncap_tim_transducer_discovery_rep = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 6},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'errorCode'         : {'type': '<H'},
    'numOfTransducerChannels'   : {'type': '<2B', 'cmd': 'num'},
    'transducerChannelIds'      : {'type': '<16s', 'cmd':  'array'},
    'transducerChannelNames'    : {'type': '<16s', 'cmd':  'array'},

}

Synchronous_read_transducer_sample_data_from_a_channel_of_a_TIM = {
    'netSvcType'        : {'type': '<B', 'const': 2},
    'netSvcId'          : {'type': '<B', 'const': 1},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelId'         : {'type': '<2B'},
    'samplingMode'      : {'type': '<B'},
    'timeout'           : {'type': '<8B'},
}

Read_TEDS_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 3},
    'netSvcId'          : {'type': '<B', 'const': 2},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelId'         : {'type': '<2B'},
    'cmdClassid'        : {'type': '<B', 'const': 1}, # common cmd
    'cmdFunctionId'     : {'type': '<B', 'const': 2}, # Read TEDS
    'tedsAccessCode'    : {'type': '<B'},
    'tedsOffset'        : {'type': '<4B'},
    'timeout'           : {'type': '<8B'},
}

Read_TEDS_rep = {
    'netSvcType'        : {'type': '<B', 'const': 3},
    'netSvcId'          : {'type': '<B', 'const': 2},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'errorCode'         : {'type': '<H'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelId'         : {'type': '<2B'},
    'tedsOffset'        : {'type': '<4B'},
    'rawTEDSBlock'      : {'type': '$rawTEDS$', 'cmd': 'rawTEDS'},
}

class tpl2msg:
    def __init__(self, tpl, maxbytelength = 1024):
        self.tpl = tpl
        self.maxbytelength = maxbytelength

    def decode(self, entcode):
        retcode = 0
        rethash = []
        loc = 0
        lengthloc = 0
        lengthnum = 0
        lengthtype = ""
        for k, v in self.tpl.items():
            if('type' in v.keys()):
                if('const' in v.keys()):
                    constval = int(struct.unpack(v['type'], entcode, loc))
                    if(constval != v['const']):
                        print("Error: Message type mismatch")
                        retcode = 10
                    rethash[k] = constval
                    loc += struct.calcsize(v['type'])
                elif('cmd' in v.keys()):
                    if('length' in v['cmd']):
                        lengthloc = loc
                        lengthnum = int(struct.unpack(v['type'], entcode, loc))
                        rethash[k] = lengthnum
                        loc += struct.calcsize(v['type'])
                    elif('num' in v['cmd']):
                        numof = int(struct.unpack('<B', entcode, loc))
                        print("numOf:", k, numof)
                        rethash[k] = numof
                        loc += struct.calcsize(v['type'])
                    elif('addrtype' in v['cmd']):
                        addrtype = int(struct.unpack('<B', entcode, loc))
                        print("addrType:", k, addrtype)
                        rethash[k] = addrtype
                        loc += struct.calcsize(v['type'])
                    elif('addr' in v['cmd']):
                        if 1 == addrtype:
                            ipent = ipaddress.ip_address(struct.unpack('<4B', entcode, loc))
                        elif 2 == addrtype:
                            ipent = ipaddress.ip_address(struct.unpack('<8B', entcode, loc))
                        rethash[k] = ipent 
                        loc += struct.calcsize(v['type'])
                    elif('array' == v['cmd']):
                        ent = []
                        for i in range(numof):
                            ent.append(struct.unpack_from(v['type'], entcode, loc))
                            loc += struct.calcsize(v['type'])
                        rethash[k] = ent
                    elif('rawTEDS' == v['cmd']):
                        rethash[k] = entcode[loc:]
                        # rethash[k] = memoryview(entcode[loc:]).cast('H')
                    else:
                        print("Error: unknown cmd", v['cmd'])
                        retcode = 20
                else:
                    rethash[k] = struct.unpack_from(v['type'], entcode, loc)
                    loc += struct.calcsize(v['type'])
            else:
                print("Error: no type in ", k)
                retcode = 30
        if(lengthloc > 0):
            if(lengthnum != loc):
                print("Error: length mismatch cal:", loc, " given:", lengthnum)
                retcode = 40
        return rethash, retcode

    def encode(self, enthash):
        retcode = 0
        loc = 0
        buffer = bytearray([0x0]*self.maxbytelength)
        lengthnum = 0
        lengthloc = 0
        lengthtype = ""
        for k, v in self.tpl.items():
            if('type' in v.keys()):
                if('const' in v.keys()):
                    constval = enthash[k]
                    if(not constval):
                        constval = v['const']
                    elif(constval != v['const']):
                        print("Error: Message type mismatch")
                        retcode = 10
                    struct.pack_into(v['type'], buffer, loc, constval)
                    loc += struct.calcsize(v['type'])
                elif('cmd' in v.keys()):
                    if('length' in v['cmd']):
                        lengthloc = loc
                        lengthtype = v['type']
                        loc += struct.calcsize(v['type'])
                    elif('num' in v['cmd']):
                        numof = enthash[k]
                        print("numOf:", k, numof)
                        struct.pack_into(v['type'], buffer, loc, numof)
                        loc += struct.calcsize(v['type'])
                    elif('addrtype' in v['cmd']):
                        addrtype = enthash[k]
                        print("addrType:", k, addrtype)
                        struct.pack_into(v['type'], buffer, loc, addrtype)
                        loc += struct.calcsize(v['type'])
                    elif('addr' in v['cmd']):
                        if 1 == addrtype:
                            ipent = ipaddress.IPv4Address(enthash[k]).packed
                            iptype = '4s'
                        elif 2 == addrtype:
                            ipent = ipaddress.IPv6Address(enthash[k]).packed
                            iptype = '16s'
                        struct.pack_into(iptype, buffer, loc, ipent)
                        loc += struct.calcsize(iptype)
                    elif('array' == v['cmd']):
                        ent = []
                        for i in range(numof):
                            struct.pack_into(v['type'], buffer, loc, enthash[k,i])
                            loc += struct.calcsize(v['type'])
                    else:
                        print("Error: unknown cmd", v['cmd'])
                        retcode = 20
                else:
#                    print(v['type'], buffer, loc, k, enthash[k], type(enthash[k]))
                    struct.pack_into(v['type'], buffer, loc, enthash[k])
                    loc += struct.calcsize(v['type'])
            else:
                print("Error: no type in ", k)
                retcode = 30
        if(lengthloc > 0):
            struct.pack_into(lengthtype, buffer, lengthloc, loc)
        return buffer[:loc], retcode

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

ncap_announcement_test = {
    'netSvcType'        : 1, #{'type': '<B', 'const': 1},
    'netSvcId'          : 1, #{'type': '<B', 'const': 1},
    'msgType'           : 3, #{'type': '<B', 'const': 3},
    'msgLength'         : 10, #{'type': '<H'},
    'ncapId'            : b'\x12\x34\x56\x78\x9a\xbc\xde\xf0\x12\x34\x56\x78\x9a\xbc\xde\xf0', #{'type': '<16s'},
    'ncapName'          : 'Name for NCAP1'.encode(), #{'type': '<16s'},
    'addressType'       : 1, #{'type': '<B', 'cmd':'addrtype'},
    'ncapAddress'       : '10.1.1.2', #{'type': '$addrtype$', 'cmd':'addr'},
}

print(ncap_announcement_func.encode(ncap_announcement_test))
