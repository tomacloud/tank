#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Logging module wrapper
'''

import logging
import logging.config

def config(log_file):
    logging.config.fileConfig(log_file)

def get_logger(name = 'root'):
    return logging.getLogger(name)

