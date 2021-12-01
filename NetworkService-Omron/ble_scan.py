from bluepy import btle

class ScanDelegate(btle.DefaultDelegate):
    def __init__(self): # コンストラクタ
        btle.DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):  # スキャンハンドラー
        if isNewDev:  # 新しいデバイスが見つかったら
            print('found dev (%s)' % dev.addr)

scanner = btle.Scanner().withDelegate(ScanDelegate())
while True:
    scanner.scan(10.0) 
