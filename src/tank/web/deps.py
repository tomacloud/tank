#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import urllib
import datetime

from tornado.web import RequestHandler
from tornado.web import Application
from tornado.web import HTTPError
from tornado import ioloop

import tornado.escape

import tornadoext.oauth2

from tank import const
from tank import config
from tank import dtutils

#from tame.models import *
#from tame.services import *

class BaseHandler(RequestHandler):

    def initialize(self, app_config, Session):
        self.app_config = app_config
        self.Session = Session
        self.db_session = None

    def get_current_user(self):
        user_token = self.get_cookie('user_token')
        if not user_token:
            return None

        db_session = self.get_db_session()
        err, params = user_srv.decode_user_token(db_session, user_token)
        if err:
            return None
        else:
            return params['user_uuid']
        
        #userid = self.get_secure_cookie("userid")
        #return userid

    def get_db_session(self):
        if not self.db_session:
            self.db_session = self.Session()
            #self.db_session.begin()

        """
        #Remember to call session.remove() after using
        return self.Session()
        """
        return self.db_session

    def on_finish(self):
        if self.db_session:
            #self.db_session.commit()
            self.db_session.close()
            self.Session.remove()

    def run_with_db(self, func, *args, **kwargs):
        db_session = self.get_db_session()

        v = func(db_session, *args, **kwargs)
        return v

    def get_login_user(self, db_session = None, user_uuid = None):
        if not user_uuid:
            user_uuid = self.get_current_user()

        if not user_uuid:
            return None

        if db_session:
            user = user_srv.get_user(db_session, user_uuid = user_uuid)
        else:
            db_session = self.get_db_session()
            user = user_srv.get_user(db_session, user_uuid = user_uuid)

        return user

    def write_web_ret(self, ret):

        def _parse_object(ret):
            if isinstance(ret, Entity):
                ret = ret.toDict()
                
            if isinstance(ret, list):
                l = []
                for v in ret:
                    l.append(_parse_object(v))
                return l
            elif isinstance(ret, dict):
                d = {}
                for k, v in ret.iteritems():
                    d[k] = _parse_object(v)
                return d
            elif isinstance(ret, datetime.datetime):
                return dtutils.dt_to_str(ret)
            else:
                return ret
            
        ret = _parse_object(ret)
        #print ret
        self.write(json.dumps(ret))
        self.finish()

class DataBaseHandler(BaseHandler):

    def check_list_permission_web_ret(
        self, permissions = None, list_uuid_name = 'list_uuid'):
        
        ret = web_ret()

        user = self.get_login_user()
        if not user:
            ret['err_code'] = errcode.AUTH_NOT_SIGNIN
            self.write_web_ret(ret)
            return False

        list_uuid = self.get_argument(list_uuid_name)
        db_session = self.get_db_session()
        ul = query_srv.query_one(
            db_session,
            UserList,
            dict(user_uuid = user.uuid,
                 list_uuid = list_uuid)
            )

        if not permissions:
            permissions = [
                const.ListPermission.OWNER,
                const.ListPermission.MANAGER,
                const.ListPermission.WRITE,
                ]
            
        
        if ul and ul.permission in permissions:
            return ret, dict(login_user = user, list_uuid = list_uuid, ul = ul)
        else:
            ret['err_code'] = errcode.PERMISSION_WRITE_LIST_DENY
            self.write_web_ret(ret)
            return False



def web_ret():
    return dict(
        err_code = 0,
        err_msg  = '',
        result   = {},
        )
