


class NCAP:
    def __init__(self) -> None:
        self.appTable = {}

        ### TODO implement Announcement
        ### TODO implement Async Publish

    def descovery(self) -> None:
        """
        Add app to appTable.
        """
        pass

    def secession(self) -> None:
        """
        Delete app from appTable
        """
        pass

    def syncAccess(self) -> None:
        """
        Process a request for SyncRead
        """
        pass

    def asyncAccess(self) -> None:
        """
        Add app to asyncList
        """
        pass
    
    def asyncTerminate(self) -> None:
        """
        Remove app from asyncList
        """
        pass

    def getAsyncList(self) -> list:
        """
        get list of apps hich subscribe AsyncRead
        """
        pass
    
    def asyncPublish(self) -> None:
        """
        Publish sensor data to clients in AsyncList
        """
        asyncList = self.getAsyncList()
        for app in asyncList:
            ### TODO implement publish sensor data to apps
            pass

    def startService(self) -> None:
        """
        Start while statement
        """

        ### TODO implement ParseRequest

        ### TODO implement if statement
        if req == discovery:
            self.descovery()
        elif req == secession:
            self.secession()
        elif req == syncAccess:
            self.syncAccess()
        elif req == asyncAccess:
            self.asyncAccess()
        elif req == asyncTerminate:
            self.asyncTerminate()
        else:
            raise Exception("Illigal reqest")