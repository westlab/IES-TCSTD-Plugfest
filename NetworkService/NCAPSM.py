import signal
import time
import pprint
from threading import Timer

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

annoucementTimerInterval = 1.0

NCAPstate = stateINITIAL
class NCAPstatemachine:
    def __init__(self):
        self.state = stateINITIAL
        self.nextstate = stateINITIAL
    def transition(self, fire):
        self.state = self.nextstate
        if self.state == stateINITIAL:
            if fire == tokenTIM:
                self.nextstate = stateTIM
            elif fire == tokenANNOUNCEMENT:
                self.nextstate = stateANNOUNCEMENT
            elif fire == tokenDISCOVERY:
                self.nextstate = stateDISCOVERY
            elif fire == tokenSECESSION:
                self.nextstate = stateSECESSION
            elif fire == tokenSYNCACCESS:
                self.nextstate = stateSYNCACCESS
            elif fire == tokenASYNCACCESS:
                self.nextstate = stateASYNCACCESS
            elif fire == tokenASYNCACCESS:
                self.nextstate = stateASYNCTERMINATE
            else:
                raise Exception("Error: Illegal token")
        elif self.state == stateANNOUNCEMENT:
            # generate and send message
            self.nextstate = stateINITIAL
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

class RepeatableTimer(object):
    def __init__(self, interval, function, args=[], kwargs={}):
        self._interval = interval
        self._function = function
        self._args = args
        self._kwargs = kwargs
    def start(self):
        t = Timer(self._interval, self._function, *self._args, **self._kwargs)
        t.start()

def actionNCAPAnnouncement():
    ### TODO implement NCAP announcement
    # print("TODO implement NCAP announcement")
    timerNCAPAnnouncement.start()

def actionASYNCACCESS():
    ### TODO implement async access
    # print("TODO implement async access")
    timerASYNCACCESS.start()

timerNCAPAnnouncement = RepeatableTimer(5.0, actionNCAPAnnouncement, ())
timerNCAPAnnouncement.start()
timerASYNCACCESS = RepeatableTimer(1.5, actionASYNCACCESS, ())
timerASYNCACCESS.start()
