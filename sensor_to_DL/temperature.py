import RPi.GPIO as GPIO
import Adafruit_DHT as dht
import pymysql
import time
import sys
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import boto3

s3 = boto3.client('s3')

bucket_name = 'raspberrypi-dacos'

db = pymysql.connect(host='localhost', user='root', password='dlqhrud-1124', db='sensor')

data = {'Time': [],
        'Temperature': [],
        'Humidity': []}

prev_date = None

while True:
    try:
        with db.cursor() as cur:
            sql = 'insert into temperature (time, tem, hum) values(%s, %s, %s);'

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            date = timestamp.split(' ')[0]  # Get date from timestamp
            h, t = dht.read_retry(dht.DHT22, 4)
            if h is not None and t is not None:
                print(timestamp, f'Temp={t:0.1f}C Humidity={h:0.1f}%')

                data['Time'].append(timestamp)
                data['Temperature'].append(t)
                data['Humidity'].append(h)

                # If date has changed, upload previous day's data to S3 and start new DataFrame
                if date != prev_date:
                    if prev_date is not None:  # Skip upload on first run
                        df = pd.DataFrame(data)
                        filename = 'temperature_{}.parquet'.format(prev_date)
                        table = pa.Table.from_pandas(df)
                        pq.write_table(table, filename)
                        s3.upload_file(filename, bucket_name, filename)

                        print('Uploaded to S3')

                    # Start new DataFrame
                    data = {'Time': [],
                            'Temperature': [],
                            'Humidity': []}

                cur.execute(sql, (timestamp, t, h))
                db.commit()

                prev_date = date

            else:
                print('Failed to get reading')
                print(f't: {t}, h: {h}')

        time.sleep(600)

    except Exception as e:
        print(e)
    finally:
        db.close()