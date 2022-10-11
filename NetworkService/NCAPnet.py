# Install and run EMQ Broker
# docker run -d --name emqx -p 1883:1883 -p 18083:18083 emqx/emqx

import asyncio
import uuid

import gmqtt

from NCAPlib import Tpl2Msg
from NCAPsm import MBRTable

addr = uuid.UUID(int=uuid.getnode()).hex[-12:] + "mqtt"
client = gmqtt.Client(addr)

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

async def start(host, port, subscriptor):
    await client.connect(host, port)
    client.subscribe(subscriptor, subscription_identifier=len(subscriptor))
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("demonstration start")

    print('MQTT client setup. Client ID:', addr)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    SUBSCRIPTOR = [
        gmqtt.Subscription("hoge", qos=2), gmqtt.Subscription("fuga", qos=2)
    ]
    start("localhost", "1883", SUBSCRIPTOR)