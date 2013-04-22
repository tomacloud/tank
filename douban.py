#!/usr/bin/env python
# -*- coding:utf-8 -*-

from douban_client import DoubanClient

def get_douban_client(app_config):

    scope = 'douban_basic_common,movie_basic_r,movie_advance_r'

    client = DoubanClient(
        app_config['douban_app_key'],
        app_config['douban_app_secret'],
        app_config['douban_redirect_url'],
        scope)

    return client
