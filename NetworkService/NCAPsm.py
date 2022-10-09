import signal
import time
import pprint
from threading import Timer

import NCAPlib

stateINITIAL = 0
stateDISCOVERY = 1
stateSECESSION = 2
stateANNOUNCEMENT = 3
stateSYNCACCESS = 4
stateSEND = 5
stateSYNCREPLY = 6
stateASYNCACCESS = 7
stateASYNCTERMINATE = 8
stateASYNCSEND = 9
stateTIM = 9

tokenINITIAL = 0
tokenDISCOVERY = 1
tokenSECESSION = 2
tokenANNOUNCEMENT = 3
tokenSYNCACCESS = 4
tokenSEND = 5
tokenSYNCREPLY = 6
tokenASYNCACCESS = 7
tokenASYNCTERMINATE = 8
tokenTIM = 9

NCAPannoucementTimerInterval = 5.0
TIMannoucementTimerInterval = 5.0
XDCRannoucementTimerInterval = 5.0

msgtype = 0

class NCAPstatemachine:
    def __init__(self):
        self.state = stateINITIAL
        self.nextstate = stateINITIAL
        self.ncapapps = []
    def transition(self, fire):
        if fire == tokenTIM:
            self.nextstate = stateTIM
        #elif fire == tokenNCAPANNOUNCEMENT:
        # Implemented as a timer interruption
        #elif fire == tokenTIMANNOUNCEMENT:
        # Implemented as a timer interruption
        #elif fire == tokenXDCRANNOUNCEMENT:
        # Implemented as a timer interruption
        #elif fire == tokenNCAPDISCOVERY:
        # Implemented as a callback function of MQTT
        #elif fire == tokenTIMDISCOVERY:
        # Implemented as a callback function of MQTT
        #elif fire == tokenXDCRDISCOVERY:
        # Implemented as a callback function of MQTT
        #---TIM or Xder trouble---
        #elif fire == tokenTIMunavailable (NCAP->APP)
        #elif fire == tokenXDCRunavailable (NCAP->APP)
        #elif fire == tokenTIMdisconnect (APP->NCAP)
        #elif fire == tokenXDCRdisconnect (APP->NCAP)
        elif fire == tokenSYNCACCESS:
            self.nextstate = stateSYNCACCESS
        elif fire == tokenASYNCACCESS:
            self.nextstate = stateASYNCACCESS
        elif fire == tokenASYNCACCESS:
            self.nextstate = stateASYNCTERMINATE
        else:
            raise Exception("Error: Illegal token")

        #elif self.state == stateANNOUNCEMENT:
        #    generate and send message
        elif self.state == stateDISCOVERY:
            # Update discovery table according to DISCOVERY
            # generate message and send
            self.nextstate = stateINITIAL
        elif self.state == stateSECESSION:
            # remove entry from discovery table
            self.nextstate = stateINITIAL
        elif self.state == stateSYNCACCESS:
            # request to read sensor data
            # update sensor request table
            self.nextstate = stateINITIAL
        elif self.state == stateASYNCACCESS:
            # complete reading sensor data
            # generate message and send
            self.nextstate = stateINITIAL
        elif self.state == stateASYNCTERMINATE:
            # remove entry from ASYNC read
            self.nextstate = stateINITIAL
        elif self.state == stateTIM:
            # sensor becomes active and get data
            # check async table
            # if table has entry:
                # self.nextstate = stateASYNCSEND
            # check sync table
                # self.nextstate = stateSEND
            self.nextstate = stateINITIAL
        elif self.state == stateASYNCSEND:
            # send async callback message
            self.nextstate = stateINITIAL
        elif self.state == stateSEND:
            # send sync reply message
            self.nextstate = stateINITIAL
        else:
            raise Exception("Error: Illegal state")
        # check timer and remove the expired entries in discovery table

NCAPSM = NCAPstatemachine()

class MBRtable:
    def __init__(self, ):
        timtbl = []
        apptbl = []
    # from NCAP
    def addtim(self, timId, timName):
        for timent in timtbl:
            if timent['id'] == timId:
                print('Warning: timId(', timId, ') is duplicated')
        timtbl.append({'id':timId, 'name':timName, 'xdcrs':[]})
    def deletetim(self, timId):
        for timent in timtbl:
            if timent['id'] == timId:
                return pop(i)
        print('Warning: timId(', timId, ') is not found')
    def addxdcr(self, timId, xdcrId, xdcrName):
        for timent in timtbl:
            if timent['id'] == timId:
                for xdcrent in timent['xdcrs']:
                    if xdcrent['id'] == xdcrid:
                        print('Warning: xdcrId(', xdcrId, ') is duplicated')
                timid['xdcr'].append({'id':xdcrId, 'name':xdcrName})
                return
        print('Warning: timId(', timId, ') is not found')
    def deletexdcr(self, xdcrId):
        for timent in timtbl:
            if timent['id'] == timId:
                for i, xdcrent in enumerate(timent['xdcrs']):
                    if xdcrent['id'] == xdcrid:
                        return pop(i)
                print('Warning: xdcrId(', xdcrId, ') is not found')
                return
        print('Warning: timId(', timId, ') is not found')
    # from APP
    def jointim(self, appId, timId):
        for timent in timtbl:
            if timent['id'] == timId:
                for tblent in apptbl:
                    if (tblent['appId'] == appId) and (tblent['timId'] == timId):
                        print('Warning: Already joined')
                        return
                apptbl.append(('appId':appId, 'timId':timId, 'xdcrIds':()))
                return
        print('Warning: timId(', timId, ') is not found')
    def leavetim(self, appId, timId):
        for i, timent in enumerate(timtbl):
            if timent['id'] == timId:
                return pop(i)
        print('Warning: timId(', timId, ') is not found')
    def joinxdcr(self, appId, timId, xdcrId):
        for timent in timtbl:
            if timent['id'] == timId:
                for xdcrent in timent['xdcrs']:
                    if xdcrent['id'] == xdcrid:
                        for tblent in apptbl:
                            if (tblent['appId'] == appId) and (tblent['timId'] == timId):
                                if xdcrId in tblent['xdcrIds']:
                                    print('Warning: Already joined')
                                    return
                                tblent['xdcrIds'].append(xdcrId)
                                return
                        print('Warning: timid(', timid, ') for appId', appId, ') is not registered')
                        return
                print('Warning: xdcrId(', xdcrId, ') is not found')
                return
        print('Warning: timId(', timId, ') is not found')
    def leavexdcr(self, appId, timId, xdcrId):
        for timent in timtbl:
            if timent['id'] == timId:
                for xdcrent in timent['xdcrs']:
                    if xdcrent['id'] == xdcrid:
                        for tblent in apptbl:
                            if (tblent['appId'] == appId) and (tblent['timId'] == timId):
                                if xdcrId in tblent['xdcrIds']:
                                    tblent['xdcrIds'].remove(xdcrId)
                                    return
                                print('Warning: xdcrId(', xdcrId, ') is not registed')
                                return
                        print('Warning: timid(', timid, ') for appId', appId, ') is not registered')
                        return
                print('Warning: xdcrId(', xdcrId, ') is not found')
                return
        print('Warning: timId(', timId, ') is not found')


APPTBL = APPtable()

class RepeatableTimer(object):
    def __init__(self, interval, function, args=[], kwargs={}):
        self._interval = interval
        self._function = function
        self._args = args
        self._kwargs = kwargs
    def start(self):
        t = Timer(self._interval, self._function, *self._args, **self._kwargs)
        t.start()


ncapId   = b'\x12\x34\x56\x78\x9a\xbc\xde\xf0\x12\x34\x56\x78\x9a\xbc\xde\xf0',
ncapName = 'Name for NCAP1'.encode()
ncapAddress = '192.168.1.1'
timId    = b'\x34\x56\x78\x9a\xbc\xde\xf0\x12\x34\x56\x78\x9a\xbc\xde\xf0\x12',
timName  = 'Name for TIM1'.encode()
xdcrChId = b'\x34\x56\x78\x9a\xbc\xde\xf0\x12\x34\x56\x78\x9a\xbc\xde\xf0\x12',
xdcrName = 'Name for Ch1'.encode()

ncap_announcement_msg = {
    'netSvcType'    : 1, # if specified, it will be checked. it can be omiteed.
    'netSvcId'      : 1, #
    'msgType'       : 3, #
    'msgLength'     : 0, #{'type': '<H'},
    'ncapId'        : ncapId,
    'ncapName'      : ncapName,
    'addressType'   : 1,
    'ncapAddress'   : ncapAddress,
}

ncap_tim_announcement = {
    'netSvcType'    : 1,
    'netSvcId'      : 2,
    'msgType'       : 3,
    'msgLength'     : 0,
    'ncapId'        : ncapId,
    'timId'         : timId,
    'timName'       : TIM1,
}

ncap_tim_transducer_announcement = {
    'netSvcType'    : 1,
    'netSvcID'      : 3,
    'msgType'       : 3,
    'msgLength'     : 0,
    'ncapId'        : ncapId,
    'timId'         : timId,
    'transducerChannelId'   : xdcrChId,
    'transducerChannelName' : xdcrName,
}

ncap_discovery_cmd = {
    'netSvcType'    : 1,
    'netSvcId'      : 4,
    'msgType'       : 1,
    'msgLength'     : 0,
    'appId'         : {'type': '<16s'},
    'timeout'       : {'type': '<Q'},
}

ncap_discovery_rep = {
    'netSvcType'    : 1,
    'netSvcId'      : 4,
    'msgType'       : 2,
    'msgLength'     : 0,
    'errorCode'     : 0
    'appId'         : {'type': '<16s'},
    'ncapId'        : {'type': '<16s'},
    'ncapName'      : {'type': '<16s'},
    'addressType'   : {'type': '<B', 'cmd': 'addrtype'},
    'ncapAddress'   : {'type': '$addrtype$', 'cmd': 'addr'},
}

ncap_tim_discovery_cmd = {
    'netSvcType'    : 1,
    'netSvcId'      : 5,
    'msgType'       : 1,
    'msgLength'     : 0,
    'ncapId'        : {'type': '<16s'},
    'timeout'       : {'type': '<Q'},
}

ncap_tim_discovery_rep = {
    'netSvcType'    : 1,
    'netSvcId'      : 5,
    'msgType'       : 2,
    'msgLength'     : 0,
    'errorCode'     : {'type': '<H'},
    'numOfTims'     : {'type': '<2s', 'cmd': 'num'},
    'timIds'        : {'type': '<16s', 'cmd': 'array'},
    'timNames'      : {'type': '<16s', 'cmd': 'array'},
}

ncap_tim_transducer_discovery_cmd = {
    'netSvcType'    : 1,
    'netSvcId'      : 6,
    'msgType'       : 1,
    'msgLength'     : 0,
    'ncapId'        : {'type': '<16s'},
    'timId'         : {'type': '<16s'},
    'timeout'       : {'type': '<Q'},
}


Synchronous_read_transducer_sample_data_from_a_channel_of_a_TIM_cmd = {
    'netSvcType'    : 2,
    'netSvcId'      : 1,
    'msgType'       : 1,
    'msgLength'     : 10,
    'ncapId'        : ncapId,
    'timId'         : timId,
    'channelId'     : xdcrChId,
    'samplingMode'  : 5, # DampleMode.Immediate
    'timeout'       : 0,
}

def actionNCAPAnnouncement():
    ncap_announcement_func = NCAPlib.Tpl2Msg(ncap_announcement, msgtype)
    msg = ncap_announcement_func.msg(ncap_announcement_msg)
    print("SEND NCAPA:", msg)
    # NCAPnet.send(topic, msg)
    timerNCAPAnnouncement.start()
timerNCAPAnnouncement = RepeatableTimer(NCAPannoucementTimerInterval, actionNCAPAnnouncement, ())
timerNCAPAnnouncement.start()

def actionTIMAnnouncement():
    tim_announcement_func = NCAPlib.Tpl2Msg(tim_announcement, msgtype)
    msg = tim_announcement_func.msg(tim_announcement_msg)
    print("SEND TIMA:", msg)
    # NCAPnet.send(topic, msg)
    timerTIMAnnouncement.start()
timerTIMAnnouncement = RepeatableTimer(TIMannoucementTimerInterval, actionTIMAnnouncement, ())
timerTIMAnnouncement.start()

def actionXDCRAnnouncement():
    xdur_announcement_func = NCAPlib.Tpl2Msg(xdur_announcement, msgtype)
    msg = xdcr_announcement_func.msg(xdcr_announcement_msg)
    print("SEND XDCRA:", msg)
    # NCAPnet.send(topic, msg)
    timerXDCRAnnouncement.start()
timerXDCRAnnouncement = RepeatableTimer(XDCRannoucementTimerInterval, actionXDCRAnnouncement, ())
timerXDCRAnnouncement.start()

def actionASYNCACCESS():
    ### TODO implement async access
    # print("TODO implement async access")
    timerASYNCACCESS.start()
timerASYNCACCESS = RepeatableTimer(1.5, actionASYNCACCESS, ())
timerASYNCACCESS.start()
