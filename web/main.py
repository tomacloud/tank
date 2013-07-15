#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
print os.getcwd()

from tank.models.base import SessionHolder
from tank.web.deps import *
from tank.web.handlers import *

class NotFoundHandler(BaseHandler):
    
    def get(self):
        raise HTTPError(404)
    
    def post(self):
        raise HTTPError(404)


if __name__ == '__main__':

    from tornado.options import define, options
    define("port", default=8888, help="run on the given port", type=int)
    define("running_dir", help="running dir", type=str)

    options.parse_command_line()

    print options, dir(options)
    print options.port, options.running_dir
    app_config = config.build(options.running_dir)

    for k, v in app_config.iteritems():
        if not isinstance(v, unicode):
            v = str(v)
        print "%s\t\t= %s" % (str(k), v)

    Session = config.build_db_session(app_config)
    SessionHolder(Session)

    debug = app_config['runtime'] == 'development'


    settings = dict(
        cookie_secret   = 'e7fd35339b7411e29298c8bcc88efaac',
        debug           = debug,
        template_path   = "%s/src/tpls/" % (app_config['running_home']),
        login_url       = '/signin',
        )
    
    print settings
    
    def build_handler(path, handler):
        return (path, handler,
                dict(app_config = app_config,
                     Session    = Session))

    from tank.web.handlers.stat import UserStatHandler
    handlers = [ #build_handler(r'/', IndexHandler),
                 build_handler(r'/__user_stat/([\w_]+)/([\w_]+)/([\w_]+)', UserStatHandler),
                 ]

    if 'application' in app_config and 'handlers' in app_config['application']:
        for handler_module in app_config['application']['handlers']:
            module = __import__(handler_module, fromlist=[''])
            print handler_module, module
            handlers += module.get_handlers(app_config, Session)
            
    handlers += [build_handler(r'.*', NotFoundHandler)]
    
    app = Application(handlers, **settings)

    app.listen(options.port)
    ioloop.IOLoop.instance().start()
