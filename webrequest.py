#!/usr/bin/env python
# -*- coding:utf-8 -*-

class WebRequest:
    def __init__(self, uri):
        self.uri = uri
        self.params = {}

        if "?" in uri:
            self.path = uri.split("?")[0]

            param = uri.split("?")[1]
            params = param.split("&")

            for k, v in [p.split("=") for p in params]:
                self.params[k] = v
        else:
            self.path = uri

        _path = self.path
        if _path.startswith('/'):
            _path = _path[1:]
            
        if _path.endswith('/'):
            _path = _path[0:len(_path)-1]

        self.module_list = _path.split('/')

    def get_param(self, name):
        if self.params.has_key(name):
            return self.params[name]
        else:
            return ""

    def get_module(self, index):
        try:
            return self.module_list[index]
        except IndexError, e:
            return None
    def get_module_size(self):
        return len(self.module_list)

    def is_index(self):
        return self.get_module_size() == 0

    def build_url(self, params = {}, removes = []):
        url = self.path
        _param_list = []

        if self.params:
            for p in self.params:
                if p not in params and p not in removes:
                    params[p] = self.params[p]

        if params:
            for k, v in params.iteritems():
                _param_list.append("%s=%s" % (k, v))

            url += "?" + "&".join(_param_list)

        return url
