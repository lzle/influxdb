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
HTTP_URL = 'http://{hostname}:{port}/debug/vars'.format(hostname=HOSTNAME, port=PORT)
LOG_FILE = '/usr/local/mallard/mallard-agent/var/60_influxdb_stats_report.log'


def set_log():
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')
    filehandler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=1)
    filehandler.setFormatter(formatter)
    log.addHandler(filehandler)


def get_influxdb_status():
    try:
        resp = requests.get(url=HTTP_URL)
        return json.loads(resp.content)

    except Exception as e:
        logging.error("Request to %s get state error %s" % (HTTP_URL, repr(e)))


def gen_mallard_data(name, fields, tags={}):
    md = {
        "name": "influxdb_status_{}".format(name),
        "time": int(time.time()),
        "endpoint": HOSTNAME,
        "tags": tags,
        "fields": fields,
        "step": 60,
        "value": 0,
    }

    return md


def report():
    content = get_influxdb_status()

    if not content:
        return

    dump_list = []
    collect_keys = ['runtime', 'queryExecutor', 'write', 'cq', 'httpd::{}'.format(PORT)]

    # normal key
    for key in collect_keys:
        metric = content.get(key)
        if not metric:
            continue

        dump_list.append(gen_mallard_data(name=metric['name'], fields=metric['values']))

    # database key
    for key in content:
        if key.startswith('database') or key.startswith('tsm1_engine'):
            metric = content[key]
            dump_list.append(gen_mallard_data(name=metric['name'], fields=metric['values'], tags=metric['tags']))

    print(json.dumps(dump_list))


if __name__ == "__main__":
    set_log()

    logging.info('Start to report InfluxDB status')

    report()

    logging.info('Completed')
