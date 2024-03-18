#!/usr/bin/python3
# -*- coding: utf-8 -*-


from influxdb import InfluxDBClient
client = InfluxDBClient('localhost', 8086, 'admin', 'mallardadmin')  # 连接数据库
client.create_database('mydb')  # 创建数据库

points = [ # 待写入数据库的点组成的列表
    {
        "measurement": "cpu_load",
        "tags": {
            "host": "server01",
        },
        # "time": "2009-11-10T23:00:00Z",
        "fields": {
            "info": "北京",
            "value": 100
        }
    },
    {
        "measurement": "cpu_load",
        "tags": {
            "host": "server09999",
        },
        # "time": "2009-11-10T23:00:00Z",
        "fields": {
            "info": "上海",
            "value": 100
        }
    },
]
client.write_points(points, database='mydb')  # 将这些点写入指定database
# 查询刚刚写入的点
# result = client.query('select value from cpu_load_short;', database='mydb')
# print(result)
