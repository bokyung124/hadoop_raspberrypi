import board
import adafruit_dht as dht
import time
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import boto3
from datetime import timedelta

s3 = boto3.client('s3')
dht_sensor = dht.DHT22(board.D4)

bucket_name = 'raspberrypi-dacos'

data = {'Time': [],
        'Temperature': [],
        'Humidity': []}

def read_adc(pin):
    """Read analog input from the specified pin."""
    bus.write_byte(DEVICE_ADDR, pin)  # set PCF8591 control byte to select the specified pin
    value = bus.read_byte(DEVICE_ADDR) # read the analog input value
    return value

while True:
    try:
        timestamp = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())
        date = timestamp.split(' ')[0]  # Get date from timestamp
        h = dht_sensor.humidity
        t = dht_sensor.temperature

        if h is not None and t is not None:
            print(timestamp, f'Temp={t:0.1f}C Humidity={h:0.1f}%')

            data['Time'].append(timestamp)
            data['Temperature'].append(t)
            data['Humidity'].append(h)

            # If time has changed, upload previous day's data to S3 and start new DataFrame
            if timestamp >= prev_timestamp + timedelta(minutes=10):
                df = pd.DataFrame(data)
                filename = 'temperature_{}.csv'.format(prev_timestamp)
                table = pa.Table.from_pandas(df)
                pq.write_table(table, filename)
                s3.upload_file(filename, bucket_name, filename)

                print('Uploaded to S3')

                # Start new DataFrame
                data = {'Time': [],
                        'Temperature': [],
                        'Humidity': []}

                prev_timestamp = timestamp

            else:
                print('Failed to get reading')
                print(f't: {t}, h: {h}')

        time.sleep(1)

    except Exception as e:
        print(e)
