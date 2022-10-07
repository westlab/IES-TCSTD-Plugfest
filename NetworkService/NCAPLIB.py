#!/usr/bin/python3
import struct
import ipaddress

# msgType: Reserved 0 Command 1 Reply 2 Announcement 3 Notification 4 Callback 5
# addressType: IPv4 1 IPv6 2
# UUID field and subfields arrangement:
#    Location (48 bits) Byte 15-10 encodes latitude (24 bits) and longitude (24 bits)
#    Manufacturer (24 bits) Byte 9-7
#    Year (16 bits) Byte 6-5 from the 0 AD base year.
#    Time (40 bits) Byte 4-0

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
    'timeout'           : {'type': '<Q'},
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
    'addressType'       : {'type': '<B', 'cmd': 'addrtype'},
    'ncapAddress'       : {'type': '$addrtype$', 'cmd': 'addr'},
}

ncap_tim_discovery_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 5},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'timeout'           : {'type': '<Q'},
}

ncap_tim_discovery_rep = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 5},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'errorCode'         : {'type': '<H'},
    'numOfTims'         : {'type': '<2s', 'cmd': 'num'},
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
    'timeout'           : {'type': '<Q'},
}

ncap_tim_transducer_discovery_rep = {
    'netSvcType'        : {'type': '<B', 'const': 1},
    'netSvcId'          : {'type': '<B', 'const': 6},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'errorCode'         : {'type': '<H'},
    'numOfTransducerChannels'   : {'type': '<2s', 'cmd': 'num'},
    'transducerChannelIds'      : {'type': '<16s', 'cmd':  'array'},
    'transducerChannelNames'    : {'type': '<16s', 'cmd':  'array'},

}

# 10.2.1

Synchronous_read_transducer_sample_data_from_a_channel_of_a_TIM_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 2},
    'netSvcId'          : {'type': '<B', 'const': 1},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelId'         : {'type': '<2s'},
    'samplingMode'      : {'type': '<B'},
    'timeout'           : {'type': '<Q'},
}

Synchronous_read_transducer_sample_data_from_a_channel_of_a_TIM_rep = {
    'netSvcType'        : {'type': '<B', 'const': 2},
    'netSvcId'          : {'type': '<B', 'const': 1},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'errorCode'         : {'type': '<H'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelId'         : {'type': '<2s'},
    'transducersampleData'  : {'type': '<16s'},
    'timestamp'         : {'type': '<8s'},
}

# 10.2.2

Synchronous_read_transducer_block_data_from_a_channel_of_a_TIM_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 2},
    'netSvcId'          : {'type': '<B', 'const': 2},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelId'         : {'type': '<2s'},
    'timeout'           : {'type': '<Q'},
    'numOfSamples'      : {'type': '<4s'},
    'sampleInterval'    : {'type': '<8s'},
    'startTime'         : {'type': '<8s'},
}

Synchronous_read_transducer_block_data_from_a_channel_of_a_TIM_rep = {
    'netSvcType'        : {'type': '<B', 'const': 2},
    'netSvcId'          : {'type': '<B', 'const': 2},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'errorCode'         : {'type': '<H'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelId'         : {'type': '<2s'},
    'transducerBlockData'   : {'type': '$block$', 'cmd': 'block'},
    'endTimestamp'      : {'type': '<8s'},
}

# 10.2.3 to be updated

Synchronous_read_transducer_sample_data_from_multiple_channel_of_a_TIM_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 2},
    'netSvcId'          : {'type': '<B', 'const': 3},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelIds'        : {'type': '<2s', 'cmd': 'block'},
    'timeout'           : {'type': '<Q'},
    'samplingMode'      : {'type': '<B'},
}

Synchronous_read_transducer_sample_data_from_multiple_channel_of_a_TIM_rep = {
    'netSvcType'        : {'type': '<B', 'const': 2},
    'netSvcId'          : {'type': '<B', 'const': 3},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'errorCode'         : {'type': '<H'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelIds'        : {'type': '<2s', 'cmd': 'block'},
    'transducerSampleDatas' : {'type': '$block$', 'cmd': 'block'},
    'timestamp'         : {'type': '<8s'},
}

# 10.2.4 to be update

Synchronous_read_transducer_block_data_from_multiple_channel_of_a_TIM_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 2},
    'netSvcId'          : {'type': '<B', 'const': 3},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelIds'        : {'type': '<2s', 'cmd': 'block'},
    'timeout'           : {'type': '<Q'},
    'numOfSamples'      : {'type': '<4s'},
    'sampleInterval'    : {'type': '<8s'},
    'startTime'         : {'type': '<8s'},
}

Synchronous_read_transducer_block_data_from_multiple_channel_of_a_TIM_rep = {
    'netSvcType'        : {'type': '<B', 'const': 2},
    'netSvcId'          : {'type': '<B', 'const': 3},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'errorCode'         : {'type': '<H'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelIds'        : {'type': '<2s', 'cmd': 'block'},
    'transducerSampleDatas' : {'type': '$block$', 'cmd': 'block'},
    'endTimestamp'      : {'type': '<8s'},
}

# 10.2.7 not yet

Synchronous_write_transducer_sample_data_from_a_channel_of_a_TIM_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 2},
    'netSvcId'          : {'type': '<B', 'const': 1},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelId'         : {'type': '<2s'},
    'samplingMode'      : {'type': '<B'},
    'timeout'           : {'type': '<Q'},
}

Synchronous_write_transducer_sample_data_from_a_channel_of_a_TIM_rep = {
    'netSvcType'        : {'type': '<B', 'const': 2},
    'netSvcId'          : {'type': '<B', 'const': 1},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'errorCode'         : {'type': '<H'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelId'         : {'type': '<2s'},
    'transducersampleData'      : {'type': '<16s'},
    'timestamp'           : {'type': '<8s'},
}

Read_TEDS_cmd = {
    'netSvcType'        : {'type': '<B', 'const': 3},
    'netSvcId'          : {'type': '<B', 'const': 2},
    'msgType'           : {'type': '<B', 'const': 1},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelId'         : {'type': '<2s'},
    'cmdClassid'        : {'type': '<B', 'const': 1}, # common cmd
    'cmdFunctionId'     : {'type': '<B', 'const': 2}, # Read TEDS
    'tedsAccessCode'    : {'type': '<B'},
    'tedsOffset'        : {'type': '<4s'},
    'timeout'           : {'type': '<Q'},
}

Read_TEDS_rep = {
    'netSvcType'        : {'type': '<B', 'const': 3},
    'netSvcId'          : {'type': '<B', 'const': 2},
    'msgType'           : {'type': '<B', 'const': 2},
    'msgLength'         : {'type': '<H', 'cmd': 'length'},
    'errorCode'         : {'type': '<H'},
    'ncapId'            : {'type': '<16s'},
    'timId'             : {'type': '<16s'},
    'channelId'         : {'type': '<2s'},
    'tedsOffset'        : {'type': '<4s'},
    'rawTEDSBlock'      : {'type': '$block$', 'cmd': 'block'},
}

class Tpl2Msg:
    def __init__(self, tpl, maxbytelength = 1024):
        self.tpl = tpl
        self.maxbytelength = maxbytelength

    def decode(self, entcode):
        rethash = {}
        loc = 0
        lengthloc = 0
        lengthnum = 0
        arrayloc = 0
        for k, v in self.tpl.items():
            if 'type' in v.keys():
                if 'const' in v.keys():
                    constval = struct.unpack_from(v['type'], entcode, loc)[0]
                    if constval != v['const']:
                        raise Exception("Error: Message type mismatch")
                    rethash[k] = constval
                    loc += struct.calcsize(v['type'])
                elif 'cmd' in v.keys():
                    if 'length' in v['cmd']:
                        lengthloc = loc
                        lengthnum = struct.unpack_from(v['type'], entcode, loc)[0]
                        rethash[k] = lengthnum
                        loc += struct.calcsize(v['type'])
                    elif 'num' in v['cmd']:
                        numof = struct.unpack_from('<B', entcode, loc)[0]
                        rethash[k] = numof
                        loc += struct.calcsize(v['type'])
                    elif 'addrtype' in v['cmd']:
                        addrtype = struct.unpack_from('<B', entcode, loc)[0]
                        rethash[k] = addrtype
                        loc += struct.calcsize(v['type'])
                    elif 'addr' in v['cmd']:
                        if 1 == addrtype:
                            iptype = '<4s'
                        elif 2 == addrtype:
                            iptype = '<16s'
                        ipent = ipaddress.ip_address(struct.unpack_from(iptype, entcode, loc)[0])
                        rethash[k] = ipent
                        loc += struct.calcsize(iptype)
                    elif 'array' == v['cmd']:
                        ent = []
                        for _ in range(numof):
                            ent.append(struct.unpack_from(v['type'], entcode, loc)[0])
                            loc += struct.calcsize(v['type'])
                        rethash[k] = ent
                    elif 'block' == v['cmd']:
                        alltplkeys = list(self.tpl.keys())
                        restkeys = alltplkeys[arrayloc+1:]
                        restloc = 0
                        for restent in restkeys:
                            restloc += struct.calcsize(self.tpl[restent]['type'])
                        rethash[k] = entcode[loc:-restloc]
                        loc = len(entcode)-restloc
                    elif 'rawTEDS' == v['cmd']:
                        rethash[k] = entcode[loc:]
                        # rethash[k] = memoryview(entcode[loc:]).cast('H')
                    else:
                        raise Exception("Error: unknown cmd", v['cmd'])
                else:
                    rethash[k] = struct.unpack_from(v['type'], entcode, loc)[0]
                    loc += struct.calcsize(v['type'])
            else:
                raise Exception("Error: no type in ", k)
            arrayloc += 1
        return rethash

    def encode(self, enthash):
        loc = 0
        buffer = bytearray([0x0]*self.maxbytelength)
        lengthloc = 0
        lengthtype = ""
        for k, v in self.tpl.items():
            if 'type' in v.keys():
                if 'const' in v.keys():
                    if k in enthash.keys():
                        constval = enthash[k]
                        if constval != v['const']:
                            raise Exception("Error: Message type mismatch")
                    else:
                        constval = v['const']
                    struct.pack_into(v['type'], buffer, loc, constval)
                    loc += struct.calcsize(v['type'])
                elif 'cmd' in v.keys():
                    if 'length' in v['cmd']:
                        lengthloc = loc
                        lengthtype = v['type']
                        loc += struct.calcsize(v['type'])
                    elif 'num' in v['cmd']:
                        numof = enthash[k]
                        struct.pack_into(v['type'], buffer, loc, numof)
                        loc += struct.calcsize(v['type'])
                    elif 'addrtype' in v['cmd']:
                        addrtype = enthash[k]
                        struct.pack_into(v['type'], buffer, loc, addrtype)
                        loc += struct.calcsize(v['type'])
                    elif 'addr' in v['cmd']:
                        if 1 == addrtype:
                            ipent = ipaddress.IPv4Address(enthash[k]).packed
                            iptype = '4s'
                        elif 2 == addrtype:
                            ipent = ipaddress.IPv6Address(enthash[k]).packed
                            iptype = '16s'
                        struct.pack_into(iptype, buffer, loc, ipent)
                        loc += struct.calcsize(iptype)
                    elif 'block' == v['cmd']:
                        if v['type'] == '$block$':
                            entlen = len(enthash[k])
                            typestr = str(entlen)+'s'
                            struct.pack_into(typestr, buffer, loc, bent)
                            loc += struct.calcsize(typestr)
                        else:
                            for bent in enthash[k]:
                                struct.pack_into(v['type'], buffer, loc, bent)
                                loc += struct.calcsize(v['type'])
                    elif 'array' == v['cmd']:
                        for i in range(numof):
                            struct.pack_into(v['type'], buffer, loc, enthash[k,i])
                            loc += struct.calcsize(v['type'])
                    else:
                        raise Exception("Error: unknown cmd", v['cmd'])
                else:
                    struct.pack_into(v['type'], buffer, loc, enthash[k])
                    loc += struct.calcsize(v['type'])
            else:
                raise Exception("Error: no type in ", k)
        if lengthloc > 0:
            struct.pack_into(lengthtype, buffer, lengthloc, loc)
        return buffer[:loc]

# test
ncap_announcement_func = Tpl2Msg(ncap_announcement)
ncap_tim_announcement_func = Tpl2Msg(ncap_tim_announcement)
ncap_tim_transducer_announcement_func = Tpl2Msg(ncap_tim_transducer_announcement)
ncap_discovery_cmd_func = Tpl2Msg(ncap_discovery_cmd)
ncap_discovery_rep_func = Tpl2Msg(ncap_discovery_rep)
ncap_tim_discovery_cmd_func = Tpl2Msg(ncap_tim_discovery_cmd)
ncap_tim_discovery_rep_func = Tpl2Msg(ncap_tim_discovery_rep)
ncap_tim_transducer_discovery_cmd_func = Tpl2Msg(ncap_tim_transducer_discovery_cmd)
ncap_tim_transducer_discovery_rep_func = Tpl2Msg(ncap_tim_transducer_discovery_rep)
Synchronous_read_transducer_sample_data_from_a_channel_of_a_TIM_cmd_func = \
    Tpl2Msg(Synchronous_read_transducer_sample_data_from_a_channel_of_a_TIM_cmd)
Synchronous_read_transducer_sample_data_from_a_channel_of_a_TIM_rep_func = \
    Tpl2Msg(Synchronous_read_transducer_sample_data_from_a_channel_of_a_TIM_rep)
Synchronous_read_transducer_block_data_from_a_channel_of_a_TIM_cmd_func = \
    Tpl2Msg(Synchronous_read_transducer_block_data_from_a_channel_of_a_TIM_cmd)
Synchronous_read_transducer_block_data_from_a_channel_of_a_TIM_rep_func = \
    Tpl2Msg(Synchronous_read_transducer_block_data_from_a_channel_of_a_TIM_rep)
Read_TEDS_cmd_func = Tpl2Msg(Read_TEDS_cmd)

ncap_announcement_test = {
    'netSvcType'    : 1, # if specified, it will be checked. it can be omiteed.
    'netSvcId'      : 1, #
    'msgType'       : 3, #
    'msgLength'     : 10, #{'type': '<H'},
    'ncapId'        : b'\x12\x34\x56\x78\x9a\xbc\xde\xf0\x12\x34\x56\x78\x9a\xbc\xde\xf0',
    'ncapName'      : 'Name for NCAP1'.encode(), #{'type': '<16s'},
    'addressType'   : 1, #{'type': '<B', 'cmd':'addrtype'},
    'ncapAddress'   : '10.1.1.2', #{'type': '$addrtype$', 'cmd':'addr'},
}

encoded_na = ncap_announcement_func.encode(ncap_announcement_test)
print(encoded_na)
decoded_na = ncap_announcement_func.decode(encoded_na)
print(decoded_na)

sync_read_xdcr_blk_mult_channel_rep = {
    'netSvcType'    : 2,
    'netSvcId'      : 3,
    'msgType'       : 1,
    'msgLength'     : 10,
    'ncapId'        : b'\x12\x34\x56\x78\x9a\xbc\xde\xf0\x12\x34\x56\x78\x9a\xbc\xde\xf0',
    'timId'         : b'\x34\x56\x78\x9a\xbc\xde\xf0\x12\x34\x56\x78\x9a\xbc\xde\xf0\x12',
    'channelIds'    : [b'\x00\xff' , b'\x01\xff', b'\x02\xff', b'\x03\xff'],
    'timeout'       : 23423,
    'samplingMode'  : 1,
}

sync_read_xdcr_blk_mul_channel_func = Tpl2Msg(
        Synchronous_read_transducer_sample_data_from_multiple_channel_of_a_TIM_cmd)
read_na = sync_read_xdcr_blk_mul_channel_func.encode(sync_read_xdcr_blk_mult_channel_rep)
print(read_na)
read_na = sync_read_xdcr_blk_mul_channel_func.decode(read_na)
print(read_na)
