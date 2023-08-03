# install
sudo apt-get install mariadb-client mariadb-server

# port 확인
show global variables like 'port';
    # 3306
# raspberrypi에서 allow
sudo ufw allow 3306

# 유저 권한 부여
grant all privileges on *.* to 'root'@'localhost' identified by 'dlqhrud-1124';

flush privileges;

# sensor database 생성
create database sensor;

use sensor;

# 온습도 센서 table 생성 (temperature)
create table temperature (
    time    datetime,
    tem     float,
    hum     float
);

# sqoop 이용하기 위해 id 컬럼 추가
alter table temperature add column id int(20) PRIMARY KEY AUTO_INCREMENT;
