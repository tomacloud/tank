#!/usr/bin/env python
# -*- coding:utf-8 -*-

import memcache

client_attrs = dir(memcache.Client)

def noop(*args): return None


class DummyClient:
    def __getattr__(self, name):
        if name not in client_attrs:
            raise AttributeError("'Client' object has no attribute '%s'" % name)
        else:
            return noop


client = DummyClient()


def create_client(app_config):
    global client

    if not client:
        mem_config = app_config['memcached']

        mem_url = "%s:%s" % (mem_config['host'], mem_config['port'])
        debug = int(mem_config['debug']) if mem_config.has_key('debug') else 0

        client = memcache.Client([mem_url], debug = debug)

    return client

if __name__ == "__main__":

    try:
        client.xxx()
        raise Exception('client.xxx is not raise an exception')

    except AttributeError, e:
        pass

    except Exception, e:
        raise Exception


    assert(client.get('name') == None)
    assert(client.set('name', 'value') == None)
