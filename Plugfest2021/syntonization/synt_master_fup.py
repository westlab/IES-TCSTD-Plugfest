#!/usr/bin/env python3

"""
BR-Sync (Syntonization)
Master clock client
"""

# Parameters
broker='192.168.0.10'
client_id='BR-Sync_Master_FUP'
topic_fup='location/TIME/FUP'
# topic_syn='location/TIME/SYN'
# message_syn='SYN'

# Initialization
import asyncio
from datetime import datetime
import gmqtt
ts_dict=dict()
STOP = asyncio.Event()

def ask_exit(*args):
    STOP.set()

def on_connect(client, flags, rc, properties):
    print('Connected with flags:',flags)

def on_disconnect(client, packet, exc=None):
    print('Disconnected.')

def on_message(client, topic, payload, qos, properties):
    print('Message received from', topic)
    msg=str(payload.decode("utf-8"))
    print('  Received message:', msg)
    print('  Properties in received message:', properties)

def assign_callbacks_to_client(client):
  client.on_connect = on_connect
  client.on_message = on_message
  client.on_disconnect = on_disconnect

async def main(broker_host):
    client = gmqtt.Client(client_id)

    assign_callbacks_to_client(client)

    await client.connect(broker_host)

    print('Subscribe ', topic_fup)
    client.subscribe(topic_fup)

    await STOP.wait()
    await client.disconnect()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(broker))
#     try:
#       loop.run_until_complete(asyncio.wait_for(main(broker), TIMEOUT))
#     except asyncio.TimeoutError:
#       print('Timeout.')
