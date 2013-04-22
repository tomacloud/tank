#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornado.options import options
from tank import config
from tank import const

def emmed_css(*args):
    app_config = get_app_config()
    css_path = "%s/src/static/css/" % (app_config['running_home'])
    content = ""
    
    for i in range(len(args)):
        css_file = "%s%s" % (css_path, args[i])
        
        handler = open(css_file, "r")
        content += handler.read()
        handler.close()
        
    return content

def get_app_config():
    app_config = config.build(const.PROJECT_NAME, options.running_dir)
    return app_config
