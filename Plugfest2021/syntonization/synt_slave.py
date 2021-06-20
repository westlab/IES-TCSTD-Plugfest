#!/usr/bin/env python3

"""
BR-Sync (Syntonization)
Slave clock client
"""

# Parameters
broker='192.168.0.10'
client_id='BR-Sync_Slave'
topic_syn='location/TIME/SYN'
topic_fup='location/TIME/FUP'
message_fup='Follow-up message from ' + client_id

# TIMEOUT=60.0

# Mode
keep_connected=True

# Initialization
import asyncio
import gmqtt
from datetime import datetime
from datetime import timedelta
import yaml
STOP = asyncio.Event()
ts = ''
delay = list()
last_received_time = list()

# Import config
conf_file='./config.yaml'
conf=dict()
with open(conf_file) as f:
    conf=yaml.safe_load(f)

def ask_exit(*args):
    STOP.set()

def on_connect(client, flags, rc, properties):
    print('Connected with flags:',flags)

def on_disconnect(client, packet, exc=None):
    print('Disconnected.')

def on_message(client, topic, payload, qos, properties):
    received_time = datetime.today()
    print('Message received.')
    print('Properties in received message:', properties)
    if topic == topic_syn:
        if len(last_received_time) != 0:
            print('  last_received_time: ', last_received_time[0])
            if timedelta(seconds=conf['trial_timeout']) < (received_time - last_received_time[0]):
                print('')
                print('  Reset measuring time')
                print('')
                delay.clear()

        user_property = properties['user_property']
        for i in user_property:
            if i[0] == 'timestamp':
                ts = datetime.fromisoformat(i[1])
                break

        delay.append(received_time - ts)
        print('  timestamp: ', ts, ' when slave clock is ', received_time)
        print('  delay: ', received_time - ts)

        last_received_time.clear()
        last_received_time.append(received_time)

        if len(delay) == int(conf['trials']):
            delay_sum = timedelta()
            for d in delay:
                delay_sum += d

            delay_average = delay_sum / len(delay)
            print('')
            print('  delay(Averave): ', delay_average)
            delay.clear()
            del delay_sum
            client.publish(topic_fup, message_fup)
            if not keep_connected:
                ask_exit()

        print('')

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

    print('Subscribe SYN')
    client.subscribe(topic_syn)
    await STOP.wait()
    await client.disconnect()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(broker))
#     try:
#         loop.run_until_complete(asyncio.wait_for(main(broker), TIMEOUT))
#     except asyncio.TimeoutError:
#         print('Timeout.')
