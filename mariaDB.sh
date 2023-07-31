# sensor database 생성
create database sensor;

use sensor;

# 온습도 센서 table 생성 (temperature)
create table temperature (
    time    datetime,
    tem     float,
    hum     float
);

