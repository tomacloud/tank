#!/usr/bin/env python
# -*- coding:utf-8 -*-

import memcache

client = None

def create_client(app_config):
    if not client:
        global client

        mem_config = app_config['memcached']

        mem_url = "%s:%s" % (mem_config['host'], mem_config['port'])
        debug = int(mem_config['debug']) if mem_config.has_key('debug') else 0

        client = memcache.Client([mem_url], debug = debug)

    return client
