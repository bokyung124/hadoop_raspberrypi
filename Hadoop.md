1. 설치
```bash
wet http://wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
```

2. ~/.bashrc
```bash
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:jre/bin/java::")
export HADOOP_HOME=/opt/hadoop

export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export HADOOP_COMMOM_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export YARN_HOME=$HADOOP_HOME
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export YARN_CONF_DIR=$HADOOP_HOME/etc/hadoop
export HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib/native"
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

export SQOOP_HOME=/opt/sqoop
export PATH=$PATH:$SQOOP_HOME/bin
```

3. hadoop-env.sh
```bash
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:jre/bin/java::")
export HADOOP_HOME=/opt/hadoop
```

4. core-site.xml
```bash
<configuration>
    <property>
        <name>fs.default.name</name>
        <value>hdfs://localhost:54310</value>
    </property>
    <property>
        <name>hadoop.tmp.dir</name>
        <value>/hdfs/tmp</value>
    </property>
</configuration>
```
> `/hdfs/tmp` 폴더 생성

5. hdfs-site.xml
```bash
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
</configuration>
```

6. mapred-site.xml
```bash
<configuration>

# Site specific YARN configuration properties 

    <property> 
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property> 
    <property> 
        <name>yarn.app.mapreduce.am.env</name>
        <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
    </property> 
    <property> 
        <name>mapreduce.map.env</name>
        <value>HADOOP_MARED_HOME=$HADOOP_HOME</value>
    </property> 
    <property> 
        <name>mapreduce.reduce.envs</name>
        <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
    </property> 
    <property> 
        <name>yarn.app.mapreduce.am.resource.memory-mb</name>
        <value>512</value>
    </property> 
    <property>  
        <name>mapreduce.map.resource.memory-mb</name>
        <value>256</value>
    </property> 
    <property> 
        <name>mapreduce.reduce.resource.memory-mb</name>
        <value>256</value>
    </property>
</configuration>
```

7. yarn-site.xml
```bash
<configuration>

# Site specific YARN configuration properties 
    <property> 
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property> 
    <property>
        <name>yarn.nodemanager.resource.cpu-vcores</name>
        <value>4</value>
    </property> 
    <property> 
        <name>yarn.nodemanager.resource.memory-mb</name>
        <value>768</value>
    </property> 
    <property> 
        <name>yarn.scheduler.minimum-allocation-mb<name>
        <value>128</value>
    </property> 
    <property> 
        <name>yarn.scheduler.maximum-allocation-mb</name>
        <value>768</value>
    </property> 
    <property> 
        <name>yarn.scheduler.minimum-allocation-vcores</name>
        <value>1</value>
    </property> 
    <property> 
        <name>yarn.scheduler.maximum-allocation-vcores</name>
        <value>4</value>
    </property>
</configuration>    
```
