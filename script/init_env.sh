#!/bin/bash

echo '''/dev/sdb  /metadata xfs defaults,noatime 0 0
/dev/sdc  /data xfs defaults,noatime 0 0
''' >> /etc/fstab


cp -rf /etc/influxdb/influxdb.conf /etc/influxdb/influxdb.conf-bak

echo '''reporting-disabled = true
bind-address = ":8088"

[meta]
  dir = "/metadata/influxdb/meta"
  retention-autocreate = true
  logging-enabled = true

[data]
  dir =  "/data/influxdb/data"
  wal-dir = "/metadata/influxdb/wal"
  wal-fsync-delay = "1s"
  index-version = "tsi1"
  trace-logging-enabled = true
  query-log-enabled = true
  strict-error-handling = false
  validate-keys = false
  cache-max-memory-size = "16g"
  cache-snapshot-memory-size = "256m"
  cache-snapshot-write-cold-duration = "20m"
  compact-full-write-cold-duration = "24h"
  max-concurrent-compactions = 8
  compact-throughput = "80m"
  compact-throughput-burst = "100m"
  max-series-per-database = 0
  max-values-per-tag = 20000000
  max-index-log-file-size = "1m"

[coordinator]
  write-timeout = "60s"
  max-concurrent-queries = 0
  query-timeout = "60s"
  log-queries-after = "15s"
  max-select-point = 0
  max-select-series = 0
  max-select-buckets = 0

[retention]
  enabled = true
  check-interval = "20m"

[shard-precreation]
  enabled = true
  check-interval = "10m"
  advance-period = "30m"

[monitor]
  store-enabled = false

[subscriber]
  enabled = false

[http]
  enabled = true
  bind-address = ":8087"
  auth-enabled = true
  log-enabled = true
  write-tracing = false
  pprof-enabled = true
  https-enabled = false
  max-row-limit = 100000000
  access-log-path = "/var/log/influxdb/influxd.access.log"

[[graphite]]
  enabled = false

[[collectd]]
  enabled = false

[[opentsdb]]
  enabled = false

[[udp]]
  enabled = false

[continuous_queries]
  log-enabled = true
  enabled = true
  run-interval = "1s"

[logging]
  format = "auto"
  level = "debug"
  suppress-logo = false
''' > /etc/influxdb/influxdb.conf


echo '''# If you modify this, please also make sure to edit init.sh

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
''' > /etc/systemd/system/influxd.service

echo '''/var/log/influxdb/influxd.access.log {
    daily
    rotate 7
    missingok
    dateext
    copytruncate
    compress
}''' > /etc/logrotate.d/influxdb



echo '''/var/log/influxdb/influxd.info.log {
    daily
    rotate 7
    missingok
    dateext
    copytruncate
    compress
}''' > /etc/logrotate.d/influxdb-info


(crontab -l; echo "#Ansible: Logrotate")| crontab
(crontab -l; echo "0 0 * * * /usr/sbin/logrotate -f /etc/logrotate.d/influxdb > /dev/null 2>&1")| crontab
(crontab -l; echo "0 0 * * * /usr/sbin/logrotate -f /etc/logrotate.d/influxdb-info > /dev/null 2>&1")| crontab

mkdir /metadata
mkdir /data
chown -R influxdb:influxdb /data/
chown -R influxdb:influxdb /metadata/



wget http://ss.bscstorage.com/baishan-s2/script/60_influxdb_status_report.py && chmod 755 60_influxdb_status_report.py  && mv -f 60_influxdb_status_report.py /usr/local/mallard/mallard-agent/plugin/sys/
wget http://ss.bscstorage.com/baishan-s2/script/60_influxdb_alive_report.py && chmod 755 60_influxdb_alive_report.py  && mv -f 60_influxdb_alive_report.py /usr/local/mallard/mallard-agent/plugin/sys/
wget http://ss.bscstorage.com/baishan-s2/script/influxdb_extract_sql.py && chmod 755 influxdb_extract_sql.py  && mv -f influxdb_extract_sql.py /etc/influxdb/



