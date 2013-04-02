#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tank.web.deps import *

class CbWeixinHandler(BaseHandler):
    def get(self):
        try:
            signature = self.get_argument("signature", None)
            timestamp = self.get_argument("timestamp", None)
            nonce     = self.get_argument("nonce", None)
            echostr   = self.get_argument("echostr", None)

            print "request params - signature: %s, timestamp: %s ,nonce: %s, echostr: %s" % (signature, timestamp, nonce, echostr)

            if utils.check_signature(config.TOKEN, signature, timestamp, nonce):
                self.write(echostr)
            else:
                pass # do nothing
        except Exception, e:
            pass
