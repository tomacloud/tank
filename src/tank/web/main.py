#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
print os.getcwd()

from tank.web.deps import *
from tank.web.handlers import *

class IndexHandler(BaseHandler):
    def get(self):
        data = {
            'title'      : 'Title',
            'login_user' : '',
            'user_token' : '',
            'app_config' : self.app_config
            }
        login_user = self.get_login_user()
        if login_user:
            data['login_user'] = login_user.name
            data['user_token'] = self.get_cookie('user_token')
        print data
        self.render('index.tpl', **data)

        #self.write("Hello")

class GoogleOAuth2Handler(BaseHandler, tornadoext.oauth2.GoogleOAuth2Mixin):

    @tornado.web.asynchronous
    def get(self):
        self.authorize_redirect(self.settings['google_permissions'])


class GoogleOAuth2CallbackHandler(BaseHandler, tornadoext.oauth2.GoogleOAuth2Mixin):

    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("code", None):
            authorization_code = self.get_argument("code", None)
            print 'authorization_code', authorization_code
            self.get_authenticated_user(authorization_code, self.async_callback(self._on_auth))

    def _on_auth(self, session, response):
        print '*' * 100
        print 'SESSION', session
        print 'RESPONSE', response
        print 'headers', response.request.headers
        print 'headers2', response.headers
        print '*' * 100
        if response.error:
            raise tornado.web.HTTPError(500, "Google auth failed")

        content = response.body
        user = tornado.escape.json_decode(content)
        #session = tornado.escape.json_decode(session)

        db_session = self.get_db_session()
        with db_session.begin():
            user = GoogleUser(**user)
            db_session.merge(user)

            session['user_id'] = user.id
            session = GoogleOAuth2Session(**session)
            db_session.merge(session)

        self.remove_db_session(db_session)
        
        print user
        self.set_secure_cookie('userid', user.id)
        self.redirect("/")

        """
        self.redirect("/")
        """

class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        userid = self.get_current_user()
        db_session = self.get_db_session()
        user = db_session.query(GoogleUser).filter_by(id=userid).first()
        print "GUSER FROM DB", user
        self.remove_db_session(db_session)
        
        self.render('home.tpl', user = user)
        

if __name__ == '__main__':

    from tornado.options import define, options
    define("port", default=8888, help="run on the given port", type=int)
    define("running_dir", help="running dir", type=str)

    options.parse_command_line()

    print options, dir(options)
    print options.port, options.running_dir
    app_config = config.build(const.PROJECT_NAME, options.running_dir)

    for k, v in app_config.iteritems():
        print "%s\t\t= %s" % (str(k), str(v))


    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session
    from sqlalchemy.pool import NullPool

    connect_args = {
        'user': app_config['mysql']['username'],
        'passwd': app_config['mysql']['password'],
        'charset': 'utf8'
        }
    db_url = 'mysql://%s:%s/%s?charset=utf8&use_unicode=1' \
             % (app_config['mysql']['host_master'],
                app_config['mysql']['port_master'],
                app_config['mysql']['database'],
                )
    echo = 'echo' in app_config['mysql'] and app_config['mysql']['echo']
    
    engine = create_engine(db_url,
                           connect_args = connect_args,
                           poolclass=NullPool,
                           echo=echo)
    #some_engine = create_engine('postgresql://scott:tiger@localhost/')
    Session = scoped_session(
        sessionmaker(bind=engine, autocommit = True, autoflush=True)
    )

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

    app = Application(
        [ build_handler(r'/', IndexHandler),
          build_handler(r'/testing', TestingHandler),
          build_handler(r'/cb/weixin', CbWeixinHandler),
          ],
        **settings
        )

    app.listen(options.port)
    ioloop.IOLoop.instance().start()
