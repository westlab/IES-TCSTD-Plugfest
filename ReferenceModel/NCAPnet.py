#!/usr/bin/python3
# Install and run EMQ Broker
# docker run -d --name emqx -p 1883:1883 -p 18083:18083 emqx/emqx

import asyncio
import uuid

import gmqtt

from NCAPlib import Tpl2Msg
from NCAPOP import confread
from NCAPsm import MBRtable

addr = uuid.UUID(int=uuid.getnode()).hex[-12:] + "mqtt"
client = gmqtt.Client(addr)

mbrTable = MBRtable()

def on_connect(client, flags, rc, properties):
    print('[CONNECTED {}]'.format(client._client_id))

def on_disconnect(client, packet, exc=None):
    print('[DISCONNECTED {}]'.format(client._client_id))

def on_subscribe(client, mid, qos, properties):
    print('on subscribe')
    print('[SUBCRIBED {} MID: {} QOS: {} PROPERTIES: {}]'.format(client._client_id, mid, qos, properties))

def on_message(client, topic, payload, qos, properties):
    print('[RECV MSG {}] TOPIC: {} PAYLOAD: {} QOS: {} PROPERTIES: {}'
        .format(client._client_id, topic, payload, qos, properties))

    ### TODO implement ParseRequest

    ### TODO implement if statement
    if req == reqDiscovery:
        descovery()
    elif req == reqSecession:
        secession()
    elif req == reqSyncAccess:
        syncAccess()
    elif req == reqAsyncAccess:
        asyncAccess()
    elif req == reqAsyncTerminate:
        asyncTerminate()
    else:
        raise Exception("Illigal reqest")

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
    get list of apps which subscribe AsyncRead
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

async def start(host, port, subscriptor):
    await client.connect(host, port)
    client.subscribe(subscriptor, subscription_identifier=len(subscriptor))
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("demonstration start")
    # confread()
    
    print('MQTT client setup. Client ID:', addr)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    SUBSCRIPTOR = [
        gmqtt.Subscription("hoge", qos=2), gmqtt.Subscription("fuga", qos=2)
    ]

    print("waiting access from app")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start("localhost", "1883", SUBSCRIPTOR))
    
