class MBRtable:
    def __init__(self, ):
        self.timtbl = []
        self.apptbl = []
    # from NCAP
    def addtim(self, timId, timName):
        for timent in self.timtbl:
            if timent['id'] == timId:
                print('Warning: timId(', timId, ') is duplicated')
        self.timtbl.append({'id':timId, 'name':timName, 'xdcrs':[]})
    def deletetim(self, timId):
        for timent in self.timtbl:
            if timent['id'] == timId:
                return pop(i)
        print('Warning: timId(', timId, ') is not found in deleting')
    def addxdcr(self, timId, xdcrId, xdcrName):
        for timent in self.timtbl:
            if timent['id'] == timId:
                for xdcrent in timent['xdcrs']:
                    if xdcrent['id'] == xdcrid:
                        print('Warning: xdcrId(', xdcrId, ') is duplicated')
                timid['xdcr'].append({'id':xdcrId, 'name':xdcrName})
                return
        print('Warning: timId(', timId, ') is not found in adding')
    def deletexdcr(self, timId, xdcrId):
        for timent in self.timtbl:
            if timent['id'] == timId:
                for i, xdcrent in enumerate(timent['xdcrs']):
                    if xdcrent['id'] == xdcrid:
                        return pop(i)
                print('Warning: xdcrId(', xdcrId, ') is not found')
                return
        print('Warning: timId(', timId, ') is not found in deleting xdcr')
    # from APP
    def jointim(self, appId, timId):
        for timent in self.timtbl:
            if timent['id'] == timId:
                for tblent in self.apptbl:
                    if (tblent['appId'] == appId) and (tblent['timId'] == timId):
                        print('Warning: Already joined')
                        return
                self.apptbl.append({'appId':appId, 'timId':timId, 'xdcrIds':()})
                return
        print('Warning: timId(', timId, ') is not found in joining xdcr')
    def leavetim(self, appId, timId):
        for i, timent in enumerate(self.timtbl):
            if timent['id'] == timId:
                return pop(i)
        print('Warning: timId(', timId, ') is not found in leaving')
    def showtimlist(self):
        timla = []
        for i, timent in enumerate(self.timtbl):
            print('timId(', timent['id'], ') name:', timent['name'])
            timla.append([timent['id'], timent['name']])
        return timla
    def showxdcrlist(self, timId):
        for i, timent in enumerate(self.timtbl):
            print('timId(', timId,['id'], ') name:', timId['name'])
    def joinxdcr(self, appId, timId, xdcrId):
        for timent in self.timtbl:
            if timent['id'] == timId:
                for xdcrent in timent['xdcrs']:
                    if xdcrent['id'] == xdcrid:
                        for tblent in self.apptbl:
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
        print('Warning: timId(', timId, ') is not found in joining xdcr')
    def leavexdcr(self, appId, timId, xdcrId):
        for timent in self.timtbl:
            if timent['id'] == timId:
                for xdcrent in timent['xdcrs']:
                    if xdcrent['id'] == xdcrid:
                        for tblent in self.apptbl:
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
        print('Warning: timId(', timId, ') is not found in leaving xdcr')
    def showxdcrlist(self, appId, timId, xdcrId):
        pass

MBRTBL = MBRtable()

if __name__ == '__main__':
        MBRTBL.jointim('appId#1', 'TIMid#1')
        MBRTBL.showtimlist()
        MBRTBL.leavetim('appId#1', 'TIMid#1')
        MBRTBL.addtim('timId#2', 'TIMname#2')
        MBRTBL.showtimlist()
        MBRTBL.jointim('appId#2', 'TIMid#2')
        MBRTBL.leavetim('appId#2', 'TIMid#2')
        MBRTBL.jointim('appId#3', 'TIMid#3')

        MBRTBL.joinxdcr('appId#2', 'TIMId#3', 'xdcrId#1')
        MBRTBL.leavexdcr('appId#2', 'TIMId#3', 'xdcrId#1')
        MBRTBL.joinxdcr('appId#3', 'TIMId#3', 'xdcrId#3')
        MBRTBL.leavexdcr('appId#3', 'TIMId#3', 'xdcrId#3')
        MBRTBL.addxdcr('TIMId#3', 'xdcrId#3', 'xdcrName#3')
        MBRTBL.joinxdcr('appId#4', 'TIMId#4', 'xdcrId#4')
#        MBRTBL.deletexdcr('xdcrId#3')
        MBRTBL.joinxdcr('appId#4', 'TIMId#4', 'xdcrId#4')
#        MBRTBL.deletetim('timId#2')
        MBRTBL.deletexdcr('TIMId#4', 'xdcrId#3')
