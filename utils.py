#!/usr/bin/env python
# -*- coding:utf-8 -*-

class Map(dict):

    def __init__(self, d = None):
        if d:
            self.update(d)

    def __getitem__(self, k):
        if k in self:
            return dict.__getitem__(self, k)
        else:
            return None
