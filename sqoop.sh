# sqoop 설치
sudo wget https://archive.apache.org/dist/sqoop/1.4.6/sqoop-1.4.6.bin__hadoop-2.0.4-alpha.tar.gz

# HDFS 연결
sudo bin/sqoop import --connect jdbc:mysql://localhost:3306/sensor --table temperature --username root --password dlqhrud-1124 --target-dir /user/pi/temperature

# 파일 확인
hadoop fs -ls /user/pi/temperature

hadoop fs -cat /user/pi/temperature/part-m-00000
...
