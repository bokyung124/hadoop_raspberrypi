import RPi.GPIO as GPIO
import Adafruit_DHT as dht
import pymysql
import time
import sys

db = pymysql.connect(host='localhost', user='root', password='***', db='sensor')

try:
    with db.cursor() as cur:
        sql = 'insert into temperature (time, tem, hum) values(%s, %s, %s)'
        while True:
            h, t = dht.read_retry(dht.DHT22, 4)
            if h is not None and t is not None:
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), \
                      'Temp={t:0.1f}C Humidity={h:0.1f}%')
                cur.execute(sql, (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), t, h))
                db.commit()
            

            else:
                print('Failed to get reading')
            time.sleep(1)
except KeyboardInterrupt:
    exit()
finally:
    db.close()