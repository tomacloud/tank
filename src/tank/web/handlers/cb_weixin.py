#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tank.web.deps import *
from tank.weixin import utils as weixin_utils

class CbWeixinHandler(BaseHandler):
    def get(self):
        try:
            signature = self.get_argument("signature", None)
            timestamp = self.get_argument("timestamp", None)
            nonce     = self.get_argument("nonce", None)
            echostr   = self.get_argument("echostr", None)

            print "request params - signature: %s, timestamp: %s ,nonce: %s, echostr: %s" % (signature, timestamp, nonce, echostr)

            if weixin_utils.check_signature(self.app_config['weixin_token'], signature, timestamp, nonce):
                self.write(echostr)
            else:
                pass # do nothing
        except Exception, e:
            if self.app_config['runtime'] == 'development':
                raise e
            pass

    def post(self):
        req_xml = self.request.body

        req_data = weixin_utils.xml_to_dict(req_xml)
        
        me = req_data["ToUserName"]
        user = req_data["FromUserName"]
        
        resp_xml = weixin_utils.gen_text_response(user, me, u"欢迎您关注")
        
        self.write(resp_xml)
