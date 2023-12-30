## 라즈베리파이 IP 주소 확인

- 라즈베리파이 모니터에 연결 
- preperences - interface에서 ssh 연결 허용
- 터미널에서 `ifconfig` 실행 후 wlan0에 있는 IP 주소 확인

<br>

- 노트북 터미널에서 `ssh pi@[ip 주소]`로 연결 
    - pw: `raspberry`


## 하둡 설치

[hadoop.md](https://github.com/bokyung124/hadoop_raspberrypi/blob/main/Hadoop.md) 참고


## 온습도 센서 연결

### 라이브러리 설치

```bash
pip install Adafruit-DHT pymysql
```

### `This environment is externally managed` 오류 발생 시

```bash
sudo rm /usr/lib/python3.11/EXTERNALLY-MANAGED
```

입력 후 실행

### python 파일 실행 

- 온도, 습도 우선 출력만

- print_temperature.py

```python
import RPi.GPIO as GPIO
import Adafruit_DHT as dht
import time
import sys

try:
    while True:
        h, t = dht.read_retry(dht.DHT22, 4)
        if h is not None and t is not None:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), \
                    f'Temp={t}C Humidity={h}%')

        else:
            print('Failed to get reading')
        time.sleep(1)
except KeyboardInterrupt:
    exit()
```

```bash
python print_temperature.py
```

<img width="639" alt="스크린샷 2023-12-30 오후 12 18 13" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/1fa25b22-9e8d-441b-8113-85e124b90b3a">


## MariaDB 설치

[mariaDB.sh](https://github.com/bokyung124/hadoop_raspberrypi/blob/main/mariaDB.sh) 참고

### 접속 및 비밀번호 설정

```bash
sudo mysql -u root
```

```sql
use mysql
select user, host, plugin from mysql.user;
```

- root의 plugin이 **mysql_native_password** 이어야 함

<br>

- 비밀번호 설정

```sql
alter user 'root'@'localhost' identified by 'pwd';
```

<br>

- exit 후 `mysql -u root -p` 로 다시 접속!

## MariaDB 적재

- temperature.py

```python
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
```

<br>

<img width="775" alt="스크린샷 2023-12-30 오후 12 57 34" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/dfe4b035-4f3d-4ea0-a203-b461216a4582">