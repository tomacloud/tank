#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import inspect
import memcache

client_attrs = dir(memcache.Client)

def noop(*args): return None

class DummyClient:
    def __getattr__(self, name):
        if name not in client_attrs:
            raise AttributeError("'Client' object has no attribute '%s'" % name)
        else:
            return noop

class NullClient(object):
    def __getattr__(self, name):
        raise ValueError("'Client' has not yet been generated")


client = NullClient()

def get(key):
    return client.get(str(key))

def set(key, value):
    return client.set(str(key), value, time=3600)

def delete(key):
    return client.delete(str(key))

def create_client(app_config):
    global client

    if not client or isinstance(client, NullClient):
        if not app_config.has_key('memcached'):
            client = DummyClient()

        mem_config = app_config['memcached']

        mem_url = "%s:%s" % (mem_config['host'], mem_config['port'])
        debug = int(mem_config['debug']) if mem_config.has_key('debug') else 0

        client = memcache.Client([mem_url], debug = debug)

    return client

def cache(key_template):
    def wrapper(func):
        def wrapper_inner(*args, **kwargs):
            func_argspec = inspect.getargspec(func)
            func_args = func_argspec[0]
            func_defaults = func_argspec[3]

            for k, v in zip(func_args, args):
                kwargs[k] = v

            if func_args:
                for k, v in zip(reversed(func_args), reversed(func_defaults)):
                    if not kwargs.has_key(k):
                        kwargs[k] = v

            tpl_dict = {}
            for k, v in kwargs.iteritems():
                if isinstance(v, dict):
                    s = ''
                    for _k in sorted(v.iterkeys()):
                        s += "%s=%s&" % (_k, v[_k])
                    kwargs[k] = s

            key = re.sub(r'\{\w+\}', lambda m: (str(kwargs[m.group(0)[1:-1]]) if m.group(0) else m.group(0)), key_template)

            print 'cache key', key

            value = client.get(key)
            if not value:
                value = func(*args) #, **kwargs)
                client.set(key, value)

            return value

        return wrapper_inner

    return wrapper


if __name__ == "__main__":

    from tank import config
    app_config = config.quick_config('/opt/var/site/')

    @cache('get-name-{id}-{name}')
    def get_name(id, name="meng"):
        print 'not use cache'
        return '123'

    class CacheTest:

        @cache('class-get-name-{id}')
        def get_name(self, id=123, name="kona"):
            print 'not use cache'
            return '123'

    create_client(app_config)

    cache_test = CacheTest()

    print cache_test.get_name(2, name='abc')
    print cache_test.get_name(1)

    print get_name(2, name='yinwm')
    print get_name(1)
