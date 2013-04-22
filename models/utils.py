#!/usr/bin/env python
# -*- coding:utf-8 -*-

import uuid

def gen_uuid():
    return str(uuid.uuid1()).replace('-', '')
