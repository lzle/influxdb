#!/bin/sh
ts=`date +%s`
cmd=""
#influxdb_list="unit7.mallard.i.qingcdn.com unit2.mallard.i.qingcdn.com unit4.mallard.i.qingcdn.com unit6.mallard.i.qingcdn.com unit1.mallard.i.qingcdn.com unit5.mallard.i.qingcdn.com 183.136.205.47 183.136.205.49 117.184.40.93 183.136.205.48 183.136.205.50"
#influxdb_list="unit2.mallard.i.qingcdn.com unit4.mallard.i.qingcdn.com unit6.mallard.i.qingcdn.com unit1.mallard.i.qingcdn.com unit5.mallard.i.qingcdn.com 183.136.205.47 183.136.205.49 117.184.40.93 183.136.205.48 183.136.205.50"
#influxdb_list="183.136.205.47 183.136.205.49 45.115.145.221 183.136.205.48 36.248.9.27 113.113.106.54 116.207.164.11 118.180.6.154 183.136.205.50 45.115.145.222 183.131.64.244 45.115.145.224 58.222.16.9"
#influxdb_list="183.131.145.143 183.131.145.144 183.131.145.145 183.131.145.146 45.115.145.221 36.248.9.27 113.113.106.54 116.207.164.11 118.180.6.154 45.115.145.222 183.131.64.244 45.115.145.224 58.222.16.9"
#influxdb_list="183.131.145.143 183.131.145.144 183.131.145.145 183.131.145.146 45.115.145.221 113.113.106.54 116.207.164.11 118.180.6.154 45.115.145.222 183.131.64.2444 45.115.145.224 58.222.16.9 219.150.124.158 219.150.124.166"
influxdb_list="183.131.145.144 183.131.145.146 58.222.58.46 58.222.58.48 183.131.179.147 183.131.181.18"
for influxdb in $influxdb_list
do
	code=`curl -s -m 5 -w %{http_code} 'http://'$influxdb':8087/ping'`
	[ "$cmd" != "" ] && cmd="$cmd,"
	if [ $code -eq 204 ]; then
    code=204
  else
   code=0
  fi
	cmd=$cmd"{\"metric\": \"check_influxdb\",\"value\": $code, \"tags\":\"address=$influxdb,level=p1\", \"fields\": \"success=$code\",\"timestamp\": $ts,\"step\": 60}"

done

influxdb_list_h="183.131.198.22 183.131.198.27 101.69.181.144 58.222.57.99 183.131.179.203 183.131.179.201 183.131.145.176 101.66.255.137 58.222.57.99"
for influxdb_h in $influxdb_list_h
do
	code=`curl -s -m 5 -w %{http_code} 'http://'$influxdb_h':8087/ping'`
	[ "$cmd" != "" ] && cmd="$cmd,"
	if [ $code -eq 204 ]; then
    code=204
  else
    code=0
  fi
	cmd=$cmd"{\"metric\": \"check_influxdb\",\"value\": $code, \"tags\":\"address=$influxdb_h,level=p0\", \"fields\": \"success=$code\",\"timestamp\": $ts,\"step\": 60}"

done

code=`curl -s -m 5 -w %{http_code} 'http://influxdb.bs58i.baishancdnx.com/ping'`
	[ "$cmd" != "" ] && cmd="$cmd,"
	if [ $code -eq 204 ]; then
    code=204
  else
    code=0
  fi
	cmd=$cmd"{\"metric\": \"check_influxdb\",\"value\": $code, \"tags\":\"address=inner,level=p1\", \"fields\": \"success=$code\",\"timestamp\": $ts,\"step\": 60}"

code=`curl -s -m 5 -w %{http_code} 'http://influxdb2.bs58i.baishancdnx.com/ping'`
	[ "$cmd" != "" ] && cmd="$cmd,"
	if [ $code -eq 204 ]; then
    code=204
  else
    code=0
  fi
	cmd=$cmd"{\"metric\": \"check_influxdb\",\"value\": $code, \"tags\":\"address=inner2,level=p1\", \"fields\": \"success=$code\",\"timestamp\": $ts,\"step\": 60}"


cmd="[$cmd]"
echo "$cmd"