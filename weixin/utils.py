#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import sha
from lxml import etree

from tank import dtutils
from tank import const

def is_number(text):
    compiler = re.compile(const.r_numberic)
    return compiler.findall(text)

def check_signature(token, signature, timestamp, nonce):
    tem_arr = [str(token), str(timestamp), str(nonce)]
    tem_arr = sorted(tem_arr)
    tem_str = "".join(tem_arr)
    tem_str = sha.new(tem_str).hexdigest()

    if tem_str == signature:
        return True
    else:
        return False
