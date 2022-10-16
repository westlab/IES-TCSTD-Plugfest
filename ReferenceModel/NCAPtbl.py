#!/usr/bin/python3
from pprint import pprint

class MBRtbl:
    def __init__(self, ):
        self.timtbl = []
    # from NCAP
    def addtim(self, timId, timName):
        for timent in self.timtbl:
            if timent['id'] == timId:
                print('Warning: timId(', timId, ') was duplicated')
                return
        self.timtbl.append({'id':timId, 'name':timName, 'xdcrs':[], 'apps':[]})
    def deletetim(self, timId):
        for i, timent in enumerate(self.timtbl):
            if timent['id'] == timId:
                return self.timtbl.pop(i-1)
        print('Warning: timId(', timId, ') was not found in deleting')
    def addxdcr(self, timId, xdcrId, xdcrName, teds='', textteds=''):
        for timent in self.timtbl:
            if timent['id'] == timId:
                for xdcrent in timent['xdcrs']:
                    if xdcrent['id'] == xdcrId:
                        print('Warning: xdcrId(', xdcrId, ') was duplicated')
                        return
                timent['xdcrs'].append({'id':xdcrId, 'name':xdcrName, 'teds':teds, 'textteds':textteds, 'apps':[]})
                return
        print('Warning: timId(', timId, ') was not found in adding')
    def deletexdcr(self, timId, xdcrId):
        for timent in self.timtbl:
            if timent['id'] == timId:
                for i, xdcrent in enumerate(timent['xdcrs']):
                    if xdcrent['id'] == xdcrId:
                        return timent['xdcrs'].pop(i-1)
                print('Warning: xdcrId(', xdcrId, ') was not found')
                return
        print('Warning: timId(', timId, ') was not found in deleting xdcr')
    def gettimlist(self, show=0):
        timla = []
        for i, timent in enumerate(self.timtbl):
            if show:
                print('SHOW TL:timId:', timent['id'], ' name:', timent['name'])
            timla.append([timent['id'], timent['name'], timent['apps']])
        return timla
    def getxdcrlist(self, timId, show=0):
        xdcra = []
        for timent in self.timtbl:
            if timent['id'] == timId:
                for xdcrent in timent['xdcrs']:
                    if show:
                        print('SHOW XL:xdcrId:', xdcrent['id'], ' name:', xdcrent['name'],\
                            ' apps:', xdcrent['apps'],\
                            ' of timId:', timent['id'], ' name:', timent['name'])
                    xdcra.append([xdcrent['id'], xdcrent['name'], xdcrent['apps'],\
                        timent['id'], timent['name']])
                return xdcra
        print('Warning: No timid')
        return
    def showtimlist(self, str=''):
        if str:
            print(str)
        pprint(self.timtbl)
    # from APP
    def jointim(self, appId, timId):
        for timent in self.timtbl:
            if timent['id'] == timId:
                if appId in timent['apps']:
                    print('Warning: Already joined')
                    return
                timent['apps'].append(appId)
                return
        print('Warning: timId(', timId, ') was not found in joining tim')
    def leavetim(self, appId, timId):
        for i, timent in enumerate(self.timtbl):
            if timent['id'] == timId:
                if appId in timent['apps']:
                    return timent['apps'].remove(appId)
                print('Warning: appId was not found in leaving')
        print('Warning: timId(', timId, ') was not found in leaving')
    def joinxdcr(self, appId, timId, xdcrId):
        for timent in self.timtbl:
            if timent['id'] == timId:
                for xdcrent in timent['xdcrs']:
                    if xdcrent['id'] == xdcrId:
                        if appId in xdcrent['apps']:
                            print('Warning: Already joined')
                            return
                        xdcrent['apps'].append(appId)
                        return
                print('Warning: xdcrId(', xdcrId, ') was not found')
                return
        print('Warning: timId(', timId, ') was not found in joining xdcr')
    def leavexdcr(self, appId, timId, xdcrId):
        for timent in self.timtbl:
            if timent['id'] == timId:
                for xdcrent in timent['xdcrs']:
                    if xdcrent['id'] == xdcrid:
                        if appId in xdcrent['apps']:
                            return tblent['xdcrIds'].remove(xdcrId)
                        print('Warning: xdcrId(', xdcrId, ') was not registed')
                        return
                print('Warning: xdcrId(', xdcrId, ') was not found')
                return
        print('Warning: timId(', timId, ') was not found in leaving xdcr')
    def gettimapp(self, appId, show=0): # get app by appId
        timla = []
        for i, timent in enumerate(self.timtbl):
            if appId in timent['apps']:
                if show:
                    print('SHOW TA:timId:', timent['id'], ' of AppID:', timent['appId'])
                timla.append([timent['id'], timent['name']])
        return timla
    def getxdcrapp(self, appId, show=0): # get xdcrid by appId
        xdcra = []
        for timent in self.timtbl:
            for xdcrent in timent['xdcrs']:
                if appId in xdcrent['apps']:
                    if show:
                        print('SHOW XA:xdcrId:', xdcrent['id'], ' name:', xdcrent['name'],\
                            ' of timId:', timent['id'], ' name:', timent['name'])
                    xdcra.append([timent['id'], timent['name'], xdcrent['id'], xdcrent['name']])
        return xdcra
    def gettimbyattr(self, attrname, attrvalue, show=0):
        timla = []
        for i, timent in enumerate(self.timtbl):
            if attrvalue in timent[attrname]:
                if show:
                    print('SHOW TB:timId:', timent['id'], ' name:', timent['name'], 'of AppID:', timent['apps'])
                timla.append(timent['id'])
        return timla
    def getxdcrbyattr(self, attrname, attrvalue, show=0):
        xdcra = []
        for timent in self.timtbl:
            for xdcrent in timent['xdcrs']:
                if attrvalue in xdcrent[attrname]:
                    if show:
                        print('SHOW XB:xdcrId:', xdcrent['id'], ' name:', xdcrent['name'],\
                            ' of timId:', timent['id'], ' name:', timent['name'])
                    xdcra.append([timent['id'], timent['name'], xdcrent['id'], xdcrent['name']])
        return xdcra
    def getattroftim(self, attr, show=0):
        timla = []
        for i, timent in enumerate(self.timtbl):
            if show:
                print('SHOW AT:timId:', timent['id'], ' name:', timent['name'], 'of AppID:',\
                    timent['apps'], ' ', attr, ':', timent[attr])
            timla.append([timent['id'], timent[attr]])
        return timla
    def getattrofxdcr(self, attr, show=0):
        xdcra = []
        for timent in self.timtbl:
            for xdcrent in timent['xdcrs']:
                if show:
                    print('SHOW AX:xdcrId:', xdcrent['id'], ' name:', xdcrent['name'],\
                        ' of timId:', timent['id'], ' name:', timent['name'], ' ', attr, ':', timent[attr])
                xdcra.append([timent['id'], timent['name'], xdcrent['id'], xdcrent['name'], xdcrent[attr]])
        return xdcra

MBRTBL = MBRtbl()

if __name__ == '__main__':
        MBRTBL.jointim('appId#1', 'TIMid#1')
        MBRTBL.gettimlist(1)
        MBRTBL.leavetim('appId#1', 'TIMid#1')
        MBRTBL.gettimlist(1)
        MBRTBL.addtim('timid#0', 'timname#0')
        print(" add #0")
        MBRTBL.gettimlist(1)
        MBRTBL.addtim('TIMid#2', 'TIMname#2')
        print(" add #2")
        MBRTBL.gettimlist(1)
        print(" join #2")
        MBRTBL.jointim('appId#2', 'TIMid#2')
        MBRTBL.gettimapp(1)
        print(" leave #2")
        MBRTBL.leavetim('appId#2', 'TIMid#2')
        MBRTBL.gettimapp(1)
        MBRTBL.jointim('appId#3', 'TIMid#3')
        print(" delete #0")
        MBRTBL.deletetim('timid#0')
        MBRTBL.gettimlist(1)
        MBRTBL.addtim('TIMid#3', 'TIMname#3')
        MBRTBL.jointim('appId#4', 'TIMid#3')

        MBRTBL.joinxdcr('appId#2', 'TIMid#3', 'xdcrId#1')
        MBRTBL.leavexdcr('appId#2', 'TIMid#3', 'xdcrId#1')
        MBRTBL.joinxdcr('appId#3', 'TIMid#3', 'xdcrId#3')
        MBRTBL.leavexdcr('appId#3', 'TIMid#3', 'xdcrId#3')
        print(" add x#3")
        MBRTBL.addxdcr('TIMid#3', 'xdcrid#3', 'xdcrName#3')
        MBRTBL.getxdcrlist('TIMid#3', 1)
        MBRTBL.joinxdcr('appId#4', 'TIMid#3', 'xdcrId#4')
        print(" add x#4")
        MBRTBL.addxdcr('TIMid#3', 'xdcrid#4', 'xdcrName#4')
        MBRTBL.getxdcrlist('TIMid#3', 1)
        print(" join x#4")
        MBRTBL.showtimlist('CHECK1')
        MBRTBL.joinxdcr('appId#5', 'TIMid#3', 'xdcrid#4')
        MBRTBL.showtimlist('CHECK2')
        MBRTBL.getxdcrlist('TIMid#3', 1)
        MBRTBL.getxdcrapp(1)
        MBRTBL.showtimlist()
        print(" delete x#4")
        MBRTBL.deletexdcr('TIMid#3', 'xdcrid#4')
        MBRTBL.getxdcrlist('TIMid#3', 1)
        MBRTBL.joinxdcr('appId#6', 'TIMid#3', 'xdcrid#4')
        MBRTBL.showtimlist()

        pprint(MBRTBL.gettimbyattr('name', 'TIMname#3', 1))
        pprint(MBRTBL.getxdcrbyattr('name', 'xdcrName$4#', 1))
        pprint(MBRTBL.getattroftim('name', 1))
        pprint(MBRTBL.getattrofxdcr('name', 1))
