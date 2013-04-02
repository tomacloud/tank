#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sha

def check_signature(token, signature, timestamp, nonce):
    tem_arr = [str(token), str(timestamp), str(nonce)]
    tem_arr = sorted(tem_arr)
    tem_str = "".join(tem_arr)
    tem_str = sha.new(tem_str).hexdigest()
    
    if tem_str == signature:
        return True
    else:
        return False
