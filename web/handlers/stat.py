#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tank.web.deps import *

class UserStatHandler(BaseHandler):

    @seed_user_token_cookie
    def get(self, app_id, wx_user_id, uuid):
        print app_id, wx_user_id, uuid

        self.write('')
        
