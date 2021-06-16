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
message_srq='SRQ'

TIMEOUT=60.0

# Initialization
import asyncio
from datetime import datetime
from datetime import timedelta
import gmqtt
import yaml
ts_dict=dict()
STOP = asyncio.Event()
last_received_time = list()
delay = list()
offset = list()
RTT = list()

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
    T4 = datetime.today()  # datetime.datetime format
    print('Message received from', topic)
    msg=str(payload.decode("utf-8"))
    print('  Received message:', msg)
    print('  Properties in received message:', properties)
    if topic == topic_srs:
        if len(last_received_time) != 0:
            print('  last_received_time: ', last_received_time[0])
            if timedelta(seconds=conf['trial_timeout']) < (T4 - last_received_time[0]):
                print('TIMEOUT')
                ask_exit()

        user_property = properties['user_property']
        for i in user_property:
            ts_dict[i[0]] = datetime.fromisoformat(i[1])  # str -> datetime.datetime

        ts_dict['T4'] = T4

        delay.append(((ts_dict['t2']-ts_dict['T1']) + (ts_dict['T4']-ts_dict['t3'])) / 2)
        offset.append(((ts_dict['t2']-ts_dict['T1']) - (ts_dict['T4']-ts_dict['t3'])) / 2)
        RTT.append((ts_dict['t2']-ts_dict['T1']) + (ts_dict['T4']-ts_dict['t3']))

        print('  Trial ', len(delay), ' of ', conf['trials'])
        print('  T1: ', ts_dict['T1'])
        print('  t2: ', ts_dict['t2'])
        print('  t3: ', ts_dict['t3'])
        print('  T4: ', ts_dict['T4'])
        print('  delay: ', delay[-1])
        print('  offset', offset[-1])
        print('  RTT', RTT[-1])

        if len(delay) == int(conf['trials']):
            delay_sum = timedelta()
            offset_sum = timedelta()
            RTT_sum = timedelta()
            for i in range(len(delay)):
                delay_sum += delay[i]
                offset_sum += offset[i]
                RTT_sum += RTT[i]
            delay_average = delay_sum / len(delay)
            offset_average = offset_sum / len(offset)
            RTT_average = RTT_sum / len(RTT)
            print('')
            print('  Average of trials:')
            print('    delay: ', delay_average)
            print('    offset: ', offset_average)
            print('    RTT: ', RTT_average)
            ask_exit()

        last_received_time.clear()
        last_received_time.append(T4)

        print('')

def assign_callbacks_to_client(client):
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

async def main(broker_host):
    client = gmqtt.Client(client_id)

    assign_callbacks_to_client(client)

    await client.connect(broker_host)

    print('Subscribe ', topic_srs)
    client.subscribe(topic_srs)

    for t in range(int(conf['trials'])):
        client.publish(topic_srq, message_srq, user_property=[('T1',datetime.today().isoformat())])
        await asyncio.sleep(float(conf['interval']))

    # print('Publish T1 to ', topic_srq)
    client.publish(topic_srq, message_srq, user_property=[('T1',datetime.today().isoformat())])

    await STOP.wait()
    await client.disconnect()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(asyncio.wait_for(main(broker), TIMEOUT))
    except asyncio.TimeoutError:
        print('Timeout.')
