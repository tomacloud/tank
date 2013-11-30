#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime
import time

def now_timestamp():
    return int(time.time())

def dt_to_str(dt, format='%Y-%m-%d %H:%M:%S'):
    if dt:
        return dt.strftime(format)
    else:
        return ''


def str_to_dt(s, format='%Y-%m-%d %H:%M:%S'):
    if s:
        return datetime.datetime.strptime(s, format)
    else:
        return None

def weibo_str_to_dt(s):
    return str_to_dt(s, format='%Y-%m-%dT%H:%M:%S+08:00')

def now():
    return datetime.datetime.now()

def now_str(format='%Y-%m-%d %H:%M:%S'):
    return dt_to_str(datetime.datetime.now(), format)

def in_a_day(td):
    return in_peroid(td, 60 * 60 * 24)

def in_a_week(td):
    return in_peroid(td, 60 * 60 * 24 * 7)

def in_an_hour(td):
    return in_peroid(td, 60 * 60)

def in_peroid(td, peroid):
    """Peroid is the time in seconds
    """
    if isinstance(td, datetime.timedelta):
        delta_seconds = td.total_seconds()
    elif isinstance(td, datetime.datetime):
        delta_seconds = (now() - td).total_seconds()

    return peroid > delta_seconds

def today():
    return datetime.date.today()

def yesterday():
    return today() - datetime.timedelta(days=1)

def date_before_today(days = 1):
    return date_before_someday(days = days)

def date_before_someday(days = 1, someday = None):
    if not someday:
        someday = today()

    return someday - datetime.timedelta(days=days)

def parse_datetime(d, format='%Y-%m-%dT%H:%M:%SZ'):
    if isinstance(d, dict):
        if '_id' in d:
            del d['_id']
        for k, v in d.iteritems():
            d[k] = parse_datetime(v, format)
    elif isinstance(d, list):
        d = [parse_datetime(v, format) for v in d]
    elif isinstance(d, datetime.datetime):
        d = d.strftime(format)

    return d
            

if __name__ == '__main__':
    print now_str()
