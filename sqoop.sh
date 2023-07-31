# temperature table에 id 컬럼 추가
alter table temperature add column id int(20) PRIMARY KEY AUTO_INCREMENT;

# sqoop 설치
sudo wget https://archive.apache.org/dist/sqoop/1.4.6/sqoop-1.4.6.bin__hadoop-2.0.4-alpha.tar.gz

# HDFS 연결
sudo bin/sqoop import --connect jdbc:mysql://localhost:3306/sensor --table temperature --username root --password dlqhrud-1124 --target-dir /user/pi/temperature