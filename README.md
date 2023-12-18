## 目录

* [基础](#基础)
    * [安装](#安装)
    * [用户](#用户)
    * [创建库](#创建库)
    * [RP](#RP)
    * [命令](#命令)

* [进阶](#进阶)

## 基础

### 安装

[官网下载](https://www.influxdata.com/downloads/) 指定的版本，本章使用 1.8.6。

```bash
$ wget https://dl.influxdata.com/influxdb/releases/influxdb-1.8.6.x86_64.rpm
$ rpm -Uvh influxdb-1.8.6.x86_64.rpm
```

编辑配置文件&systemd配置

```bash
$ vim /etc/influxdb/influxdb.conf

$ vim /etc/systemd/system/influxd.service
# If you modify this, please also make sure to edit init.sh

[Unit]
Description=InfluxDB is an open-source, distributed, time series database
Documentation=https://docs.influxdata.com/influxdb/
After=network-online.target

[Service]
User=influxdb
Group=influxdb
LimitNOFILE=65536
EnvironmentFile=-/etc/default/influxdb
#ExecStart=/usr/bin/influxd -config /etc/influxdb/influxdb.conf $INFLUXD_OPTS
ExecStart=/bin/bash -c "/usr/bin/influxd -config /etc/influxdb/influxdb.conf >> /var/log/influxdb/influxd.info.log 2>&1"
KillMode=control-group
Restart=on-failure

[Install]
WantedBy=multi-user.target
Alias=influxd.service

$ chown -R influxdb:influxdb /data/
$ chown -R influxdb:influxdb /metadata/
```

启动

```bash
$ systemctl start influxdb

$ /usr/bin/influxd -config /etc/influxdb/influxdb.conf
```

停止

```bash
$ systemctl stop influxdb
```

日志 rotate
```
[root@dx-lt-yd-zhejiang-huzhou-3-183-131-179-201 logrotate.d]# cat /etc/logrotate.d/influxdb
/var/log/influxdb/influxd.access.log {
    daily
    rotate 7
    missingok
    dateext
    copytruncate
    compress
}

[root@dx-lt-yd-zhejiang-huzhou-3-183-131-179-201 logrotate.d]# cat /etc/logrotate.d/influxdb-info
/var/log/influxdb/influxd.info.log {
    daily
    rotate 7
    missingok
    dateext
    copytruncate
    compress
}
```
crotab

```
$ crotab -e
#Ansible: Logrotate
0 0 * * * /usr/sbin/logrotate -f /etc/logrotate.d/influxdb > /dev/null 2>&1
0 0 * * * /usr/sbin/logrotate -f /etc/logrotate.d/influxdb-info > /dev/null 2>&1
```


### 用户

登录管理交互终端

```bash
$ influx -host 127.0.0.1 -port 8087
Connected to http://127.0.0.1:8087 version 1.8.6
InfluxDB shell version: 1.8.6
>
```

创建用户、设置用户权限

```bash
> CREATE USER admin WITH PASSWORD 'mallardadmin' WITH ALL PRIVILEGES
> AUTH admin mallardadmin
> CREATE USER mallard2 WITH PASSWORD 'mallard2e8e8' WITH ALL PRIVILEGES
```

### 创建库

创建对应的数据库

```bash
$ influx -host 127.0.0.1 -port 8087 -username 'admin' -password 'mallardadmin' 
Connected to http://127.0.0.1:8087 version 1.8.6
InfluxDB shell version: 1.8.6
> create database mallard
> 
> show databases;
name: databases
name
----
mallard
```

### RP

数据保留策略，默认保存永久

```bash
> CREATE RETENTION POLICY "fiveweeks" ON mallard DURATION 5w REPLICATION 1 DEFAULT
> show retention policies on mallard
name      duration shardGroupDuration replicaN default
----      -------- ------------------ -------- -------
autogen   0s       168h0m0s           1        false
fiveweeks 840h0m0s 24h0m0s            1        true
```

修改保留策略

```bash
> ALTER RETENTION POLICY fiveweeks on mallard DURATION 5w SHARD DURATION 7d DEFAULT
> show retention policies on mallard
name      duration shardGroupDuration replicaN default
----      -------- ------------------ -------- -------
autogen   0s       168h0m0s           1        false
fiveweeks 840h0m0s 168h0m0s           1        true
```

### 命令

常用交互命令

```bash
> show databases

> use mallard

> show measurements

> show diagnostics
```

查看 measurement 的 fileds、tags

```bash
> show field keys from 'measurement';

> show tag keys from 'measurement';
```

查看数据库中 series 数量

```bash
$ influx -host 127.0.0.1 -port 8087 -username 'admin' -password 'mallardadmin' -execute 'show series on mallard' -format 'csv'
key
"cpu_load_short,host=server0,region=us-west"
"cpu_load_short,host=server01,region=us-west"
"cpu_load_short,host=server01,region1=us-west"
"cpu_load_short,host=server04,region=us-west"
"cpu_load_short,host=server1,region=us-west"
```

查看数据库 measurements 中 series 数量

```bash
$ influx -host 127.0.0.1 -port 8087 -username 'admin' -password 'mallardadmin' -execute 'show series exact cardinality on mydb' -format 'csv'
name,count
cpu_load_short,1003
```

## 相关链接

[Github Site](https://github.com/influxdata/influxdb)

[InfluxDB v1 documentation](https://docs.influxdata.com/influxdb/v1/)
