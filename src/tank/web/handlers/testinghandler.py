#!/usr/bin/env python
# -*- coding:utf-8 -*-

import md5

from tank.web.deps import *

class TestingHandler(BaseHandler):

    def get(self):
        data = {'name':'tom'}
        self.render('testing.tpl', **data)


"""
    def get(self, user_name):
        login_user = self.get_login_user()
        db_session = self.get_db_session()
        results = list_srv.user_list(
            db_session, login_user,
            list_user_name = user_name,
            is_public = self.get_argument('is_public', None)
            )
        data = { 'title' : 'Title',
                 'app_config' : self.app_config,
                 'owner' : user_name,
                 'result' : results
                 }

        if results['user']:
            self.render('my-home.tpl', **data)
        else:
            raise HTTPError(404)


"""
