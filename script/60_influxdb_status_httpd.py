#!/usr/bin/env python3
import os
import json
import datetime
import subprocess
import logging
import sys
import logging.handlers
import socket

HOSTNAME = socket.gethostname()
FILE_NAME = "/var/log/influxdb/influxd.access.log"
LINE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
CURRENT_DATE = datetime.datetime.now().strftime("%Y%m%d")
LOG_FILE = "/usr/local/mallard/mallard-agent/var/60_influxdb_status_httpd_error.log"


def set_log():
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '[%(asctime)s,%(process)d-%(thread)d,%(filename)s,%(lineno)d,%(levelname)s] %(message)s')
    filehandler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=1)
    filehandler.setFormatter(formatter)
    log.addHandler(filehandler)


def write_or_update_meta(current_line_number, line_number_filename):
    logging.error("Did not change the file, update the line number")
    with open(line_number_filename, mode='w') as f:
        f.write(json.dumps(
            {'file_date': datetime.datetime.now().strftime("%Y%m%d"), 'last_read_line_num': current_line_number}))


def read_meta(line_number_filename):
    with open(line_number_filename) as f:
        return json.loads(f.read())


def get_total_lines(filename1):
    wc_result = subprocess.Popen(['wc', '-l', filename1], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    wc_result.wait()
    # 读取输出并提取总行数
    output, error = wc_result.communicate()
    total_lines = int(output.split()[0])
    return total_lines


def retrieve_last_read_line_number(line_number_filename):
    if not os.path.exists(line_number_filename):
        return 1
    latest_json = read_meta(line_number_filename)
    if latest_json['file_date'] != CURRENT_DATE:
        return 1
    start_line_number = latest_json['last_read_line_num']
    return start_line_number


def execute_log_query(line_number_filename, filter_words, mantissa=None):
    start_line_number = retrieve_last_read_line_number(line_number_filename)
    cmd = f"sed -n '{start_line_number}, {mantissa}' {FILE_NAME} | grep '/{filter_words}?'"
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True,
                            check=True)
    return result, start_line_number


def generate_mallard(current_timestamp, mallard_name, p99_collection):
    p99_dict = {
        'name': mallard_name,
        'time': int(current_timestamp),
        'endpoint': HOSTNAME,
        'fields': {
            'p99': p99_collection[0],
            'p995': p99_collection[1],
            'p999': p99_collection[2]
        },
        'tags': {},
        'step': 60,
        'value': 1
    }
    return p99_dict


def calculate_p99_value(time_list, mallard_name):
    p99_collection = []
    if time_list:
        time_list.sort()
        length = len(time_list)
        p99_value = time_list[int(length * 0.99)]
        p995_value = time_list[int(length * 0.995)]
        p999_value = time_list[int(length * 0.999)]
        p99_collection.extend([p99_value, p995_value, p999_value])
    else:
        p99_collection = [0, 0, 0]
    current_timestamp = datetime.datetime.now().timestamp()
    p99_dict = generate_mallard(current_timestamp, mallard_name, p99_collection)
    return p99_dict


def read_elapsed_time(line_number_file, filter_words, mallard_name, mantissa):
    result, start_line_number = execute_log_query(line_number_file, filter_words, mantissa)
    if result.stdout:
        time_list = [int(line.split(" ")[-1]) for line in result.stdout.splitlines()]
    else:
        time_list = []
    p99_dict = calculate_p99_value(time_list, mallard_name)
    return p99_dict


def compute_write_query_duration_p99():
    total_lines = get_total_lines(FILE_NAME)
    mallard_name = 'influxdb_status_httpd_writeDuration'
    line_file = ".line_number_meta.txt"
    line_number_file = f"{LINE_DIRECTORY}/{line_file}"
    filter_words = "write"
    mantissa = str(total_lines) + 'p'
    write_p99_dict = read_elapsed_time(line_number_file, filter_words, mallard_name, mantissa)

    mallard_name = 'influxdb_status_httpd_queryDuration'
    filter_words = "query"
    query_p99_dict = read_elapsed_time(line_number_file, filter_words, mallard_name, mantissa)

    dump_list = [write_p99_dict, query_p99_dict]
    write_or_update_meta(total_lines, line_number_file)
    logging.info('The line number file was updated successfu')

    return dump_list


def report():
    dump_list = compute_write_query_duration_p99()
    print(json.dumps(dump_list))
    logging.info("write to file successfully")


if __name__ == '__main__':
    set_log()

    logging.info('Start calculating influxdb write consumption time and query time p99')

    report()

    logging.info('Completed')