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

def xml_to_dict(xml_text):
    root = etree.fromstring(xml_text)
    data = dict()

    for node in root:
        data[node.tag] = node.text

    return data

def dict_to_xml(data):
    root = etree.Element("xml")
    
    for tag, text in data.iteritems():
        node = etree.Element(tag)
        node.text = text if is_number(text) else etree.CDATA(text)
        root.append(node)
        
    return etree.tostring(root, encoding = "utf-8")

def gen_response_dict(to_user, from_user, msg_type):
    data = dict()
    
    data['ToUserName'] = to_user
    data['FromUserName'] = from_user
    data['MsgType'] = msg_type
    data['CreateTime'] = str(dtutils.now_timestamp())

    return data

def gen_text_response(to_user, from_user, content):
    resp_data = gen_response_dict(to_user, from_user, "text")
    resp_data['Content'] = content
    
    resp_text = dict_to_xml(resp_data)

    return resp_text

def gen_image_response(): pass
def gen_music_response(to_user, from_user, music_url, hq_music_url): pass

