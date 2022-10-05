import signal
import time
import pprint
from threading import Timer

stateINITIAL = 0
stateDISCOVERY = 1
stateANNOUNCEMENT = 1
stateSYNCACCESS = 2
stateSEND
stateSYNCREPLY = 3
stateASYNCACCESS = 4
stateASYNCTERMINATE = 5
stateTIM = 6

tokenINITIAL = 0
tokenDISCOVERY = 1
tokenANNOUNCEMENT = 1
tokenSYNCACCESS = 2
tokenSEND
tokenSYNCREPLY = 3
tokenASYNCACCESS = 4
tokenASYNCTERMINATE = 5
tokenTIM = 6

annoucementTimerInterval = 1

NCAPstate = stateINITIAL
class NCAPstatemachine:
    def __init__(self):
        self.state = stateINITIAL
        self.nextstate = stateINITIAL
    def transition(self, fire):
        self.state = self.nextstate
        if self.state == stateINITIAL:
            if fire == tokenTIM:
            elif fire == tokenANNOUNCEMENT:
                self.nextstate = stateANNOUNCEMENT
            elif fire == tokenDISCOVERY:
                self.nextstate = stateDISCOVERY
            elif fire == tokenSYNCACCESS:
                self.nextstate = stateSYNCACCESS
            elif fire == tokenSYNCSEND:
                self.nextstate = stateSEND
            elif fire == tokenASYNCACCESS:
                self.nextstate = stateASYNCACCESS
            elif fire == tokenASYNCACCESSTERMINATE:
                self.nextstate = stateASYNCTERMINATE
            elif fire == tokenTIM:
                self.nextstate = stateTIM
            else:
                raise Exception("Error: Illegal state")
        elif self.state == DISCOVERY:
            # generate 
'''
In the INITIAL state
 - send the announcement message in an interval (but the interval is not given in the .0)
  - If discovery message is received go to DISCOVERY
   - If sync read/write cmd receives go to SYNCACC
    - If syncaccwait table is not null, do pooling of all entries
        - and if sensor data is updated, go to SYNCSEND
         - If async read/write cmd receives go to ASYNCACC
          - If sensor trigger is issued and sensor data generated go to TIM state

          in the DISCOVERY state
           - Update ncap service friends table according to DISCOVERY
           (the need of this table is not given in .0)
            - send DISCOVERY reply and return to INITIAL

            in the SYNCACC state
             - Assert sensor active and update syncaccwait table
              - return to INITIAL

              in the SYNCSEND state
               - generate (reply) message of sensor data and remove the entry from syncaccwait table
                - return to INITIAL

                in the ASYNCACC state
                 - update asyncaccwait table
                  - return to INITIAL

                  in the TIM state
                   - check the table of asyncaccwait table and send (push) message of sensor data 
'''

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

    timerNCAPAnnouncement.start()

timerNCAPAnnouncement = RepeatableTimer(5.0, actionNCAPAnnouncement, ())
timerNCAPAnnouncement.start()
timerASYNCACCESS = RepeatableTimer(1.5, actionASYNCACCESS, ())
timerASYNCACCESS.start()
