#!/usr/bin/env python2
# coding: utf-8

import time
import json
import socket
import requests
import logging
import logging.handlers

HOSTNAME = socket.gethostname()
LOG_FILE = '/usr/local/mallard/mallard-agent/var/60_influxdb_alive_remote_detect.log'


def set_log():
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')
    filehandler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=1)
    filehandler.setFormatter(formatter)
    log.addHandler(filehandler)


def check_influxdb_alive(http_url):
    try:
        resp = requests.get(url=http_url, timeout=5)
        if resp.status_code == 204:
            return 1

    except Exception as e:
        logging.error("Request to %s get state error %s" % (HTTP_URL, repr(e)))

    return 0


def report():

    remote_influxdb_services = {
        # 重保
        'P1' : {
            'dx-lt-yd-zhejiang-jinhua-5-183-131-198-22':'http://183.131.198.22:8087/ping',
            'dx-lt-yd-zhejiang-jinhua-5-183-131-198-27':'http://183.131.198.27:8087/ping',
            'dx-lt-yd-jiangsu-taizhou-4-58-222-58-46':'http://58.222.58.46:8087/ping',
            'dx-lt-yd-hebei-shijiazhuang-10-124-236-69-75':'http://124.236.69.75:8087/ping',
        },
        # 非重保
        'P2': {
            'dx-lt-yd-zhejiang-jinhua-5-10-104-1-22': 'http://influxdb.bs58i.baishancdnx.com/ping',
            'dx-lt-yd-zhejiang-jinhua-5-10-104-1-23': 'http://influxdb2.bs58i.baishancdnx.com/ping',
            'dx-lt-yd-zhejiang-jinhua-5-10-104-3-7': 'http://influxdb3.bs58i.baishancdnx.com/ping',
            'dx-lt-yd-zhejiang-jinhua-5-183-131-145-146': 'http://183.131.145.146:8087/ping',
            'dx-lt-yd-zhejiang-jinhua-5-183-131-145-176': 'http://183.131.145.176:8087/ping',
            'dx-lt-yd-zhejiang-huzhou-3-183-131-179-201': 'http://183.131.179.201:8087/ping',
            'dx-lt-yd-jiangsu-huaian-8-222-184-34-213': 'http://222.184.34.213:8087/ping',
            'dx-lt-yd-hebei-shijiazhuang-10-124-236-71-201': 'http://124.236.71.201:8087/ping',
            'dx-lt-yd-hebei-shijiazhuang-10-124-236-72-25': 'http://124.236.72.25:8087/ping',
            'dx-lt-yd-jiangsu-huaian-8-218-2-0-200': 'http://218.2.0.200:8087/ping',
            'dx-lt-yd-hebei-shijiazhuang-10-124-236-72-43': 'http://124.236.72.43:8087/ping',
            'dx-lt-yd-hebei-shijiazhuang-10-124-236-72-44': 'http://124.236.72.44:8087/ping',
            'dx-lt-yd-jiangsu-huaian-8-222-184-34-214': 'http://222.184.34.214:8087/ping',
            'dx-lt-yd-jiangsu-huaian-8-218-2-0-205': 'http://218.2.0.205:8087/ping',
            'dx-lt-yd-jiangsu-taizhou-4-58-222-58-48': 'http://58.222.58.48:8087/ping',
            'dx-lt-yd-zhejiang-huzhou-3-183-131-181-18': 'http://183.131.181.18:8087/ping',
            'dx-lt-yd-jiangsu-taizhou-4-58-222-57-99': 'http://58.222.57.99:8087/ping',
            'dx-lt-yd-zhejiang-jinhua-5-183-131-145-144': 'http://183.131.145.144:8087/ping',
            'dx-lt-yd-zhejiang-jinhua-5-183-131-145-15': 'http://101.69.181.15:8087/ping',
            'dx-lt-yd-zhejiang-huzhou-3-183-131-179-147': 'http://183.131.179.147:8087/ping',
            'dx-lt-yd-zhejiang-huzhou-3-183-131-179-203': 'http://183.131.179.203:8087/ping',
            'dx-lt-yd-zhejiang-jinhua-5-101-66-255-183': 'http://101.66.255.183:8087/ping',
        }
    }

    dump_list = []
    for level, services in remote_influxdb_services.items():
        for address, http_url in services.items():

            alive = check_influxdb_alive(http_url)

            mallard_data = {
                "name": "influxdb_alive_remote_detect",
                "time": int(time.time()),
                "endpoint": HOSTNAME,
                "tags": {
                    'hostname': address,
                    'level': level
                },
                "fields": {},
                "step": 60,
                "value": alive,
            }

            dump_list.append(mallard_data)

    print(json.dumps(dump_list))


if __name__ == "__main__":
    set_log()

    logging.info('Start to report InfluxDB alive')

    report()

    logging.info('Completed')
