#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
print os.getcwd()

from tank.models.base import SessionHolder
from tank.web.deps import *
from tank.web.handlers import *

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


    if app_config.has_key('mongodb'):
        from pymongo import MongoClient
        mongo_conf = app_config['mongodb']
        conn = MongoClient(mongo_conf['host'], mongo_conf['port'])
        settings['mongo_conn'] = conn

    if app_config.has_key('memcached'):
        from tank import mc
        mc.create_client(app_config)

    if app_config.has_key('redis'):
        import redis
        redis_conf = app_config['redis']
        r = redis.StrictRedis(
            host=redis_conf['host'],
            port=redis_conf['port'],
            db=redis_conf['db'])
        app_config['redis_client'] = r
    
    print settings


    _startpoint = None
    if app_config.has_key("startpoint") and app_config["startpoint"]:
        """
        `startpoint.py` can be imported in somewhere your project.
        Defualt place in `$PROJECT_ROOT/src/startpoint.py`
        The file will initialize your project, something tank not did.
        """
        import startpoint
        startpoint.__init__(app_config)
        _startpoint = startpoint
    
    def _build_handler(path, handler):
        return (path, handler,
                dict(app_config = app_config,
                     Session    = Session))

    from tank.web.handlers.stat import UserStatHandler
    handlers = [ #build_handler(r'/', IndexHandler),
        _build_handler(r'/__user_stat/([\w_]+)/([\w_]+)/([\w_]+)', UserStatHandler),
        ]

    if 'application' in app_config and 'handlers' in app_config['application']:
        for handler_module in app_config['application']['handlers']:
            module = __import__(handler_module, fromlist=[''])
            print handler_module, module
            handlers += module.get_handlers(app_config, Session)
    
    app = Application(handlers, **settings)

    app.listen(options.port)
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        if _startpoint:
            if hasattr(_startpoint, '__stop__'):
                __stop__ = getattr(_startpoint, '__stop__')
                try:
                    __stop__(app_config)
                except:
                    pass
        ioloop.IOLoop.instance().stop()
