#!/usr/bin/env python3

"""
Synchronization
Slave clock client
"""

# Parameters
broker='192.168.0.10'
client_id='Sync_Slave'
topic_srq='location/TIME/SRQ'
topic_srs='location/TIME/SRS'
message_srs='SRS'

# Mode
keep_connected=True

# Initialization
import asyncio
import gmqtt
from datetime import datetime
STOP = asyncio.Event()

def ask_exit(*args):
    STOP.set()

def on_connect(client, flags, rc, properties):
    print('Connected with flags:',flags)

def on_disconnect(client, packet, exc=None):
    print('Disconnected.')

def on_message(client, topic, payload, qos, properties):
    T1 = ''
    t2 = datetime.today().isoformat()
    print('Message received.')
    print('Properties in received message:', properties)
    user_property = properties['user_property']
    for i in user_property:
        if i[0] == 'T1':
            T1 = i[1]
            break

    print('Publish SRS to ', topic_srs, '...')
    client.publish(topic_srs, message_srs, user_property=[('T1', T1), ('t2', t2), ('t3', datetime.today().isoformat())])
    print('Published.')
    if not keep_connected:
        ask_exit()

def on_subscribe(client, mid, qos, properties):
    print('Subscribed.')

def assign_callbacks_to_client(client):
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe

async def main(broker_host):
    client = gmqtt.Client(client_id)

    assign_callbacks_to_client(client)
    await client.connect(broker_host)

    print('Subscribe SRQ')
    client.subscribe(topic_srq)
    await STOP.wait()
    await client.disconnect()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(broker))
