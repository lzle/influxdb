#!/usr/bin/env python2
# coding: utf-8

import time
import json
import socket
import requests
import logging
import logging.handlers

HOSTNAME = socket.gethostname()
PORT = '8087'
HTTP_URL = 'http://{hostname}:{port}/ping'.format(hostname=HOSTNAME, port=PORT)
LOG_FILE = '/usr/local/mallard/mallard-agent/var/60_influxdb_alive_report.log'
IMPORTANCE_LEVEL = 'P2'


def set_log():
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')
    filehandler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=1)
    filehandler.setFormatter(formatter)
    log.addHandler(filehandler)


def check_influxdb_alive():
    try:
        resp = requests.get(url=HTTP_URL, timeout=5)
        if resp.status_code == 204:
            return 1

    except Exception as e:
        logging.error("Request to %s get state error %s" % (HTTP_URL, repr(e)))

    return 0


def report():
    alive = check_influxdb_alive()

    mallard_data = [{
        "name": "influxdb_alive",
        "time": int(time.time()),
        "endpoint": HOSTNAME,
        "tags": {
            'level': IMPORTANCE_LEVEL
        },
        "fields": {},
        "step": 60,
        "value": alive,
    }]

    print(json.dumps(mallard_data))


if __name__ == "__main__":
    set_log()

    logging.info('Start to report InfluxDB alive')

    report()

    logging.info('Completed')
