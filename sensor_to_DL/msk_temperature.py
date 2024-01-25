import RPi.GPIO as GPIO
import Adafruit_DHT as dht
import pymysql
import time
import sys
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import boto3
import json

from datetime import datetime, timedelta
from dateutil.parser import parse

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder

s3 = boto3.client('s3')
bucket_name = 'raspberrypi-dacos'

topic = "raspberrypi"
client_id = "temperature"

def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))

def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(
        return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        resubscribe_future.add_done_callback(on_resubscribe_complete)

def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))

def on_message_received(topic, payload, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))

def collect_and_send_data():
    publich_count = 0
    while(True):
        now = datetime.now()
        now_time = now.strftime('%Y-%m-%d %H:%M:%S')
        h, t = dht.read_retry(dht.DHT22, 4)
        if h is not None and t is not None:
            print(now_time, f'Temp={t:0.1f}C Humidity={h:0.1f}%')

            message = {
                "client_id": client_id,
                "timestamp": now_time,
                "humidity": h,
                "temperature": t,
                "count": publich_count
            }

            print("publishing message to topic '{}': {}".format(topic, message))

            mqtt_connection.publish(
                topic=topic,
                payload=json.dumps(message),
                qos=mqtt.Qos.AT_LEAST_ONCE)
            time.sleep(1)

            publich_count += 1

if __name__ == '__main__':
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint="a37y8b2vrsolby-ats.iot.ap-northeast-2.amazonaws.com",
        cert_filepath="raspberrypi-dacos.cert.pem",
        pri_key_filepath="raspberrypi-dacos.private.key",
        client_bootstrap=client_bootstrap,
        ca_filepath="root-CA.crt",
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=client_id
    )

    connect_future = mqtt_connection.connect()
    connect_future.result()
    print("Connected!")

    # Subscribe
    print("Subscribing to topic '{}'".format(topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received
    )

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    collect_and_send_data()