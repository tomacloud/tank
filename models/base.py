#!/usr/bin/env python
# -*- coding:utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import Table, MetaData, Column
from sqlalchemy import Integer, Unicode, UnicodeText, Boolean, DateTime, Float, Text
from sqlalchemy.orm import mapper

from sqlalchemy import or_


#metadata = MetaData()

#print Base.__metaclass__


"""
def parse_fields(instance, d):
    for c in instance.__table__.columns:
        #print c.name
        if c.name in d:
            setattr(instance, c.name, d[c.name])
"""

"""
class QueryableEntity(type):
    def __init__(cls, classname, bases, dict_):
        print('QueryableEntity')
        return type.__init__(cls, classname, bases, dict_)

    def __getattr__(self, name):

        def query(*args, **kwargs):
            pass
        
        print 'QUERY able ', name

        return query

print  QueryableEntity        
"""
class Entity(object):

    __table__ = None

    __ignore_fields__ = []

    def __str__(self):
        return self.__repr__()

    def _get_ext_fields(self):
        if not hasattr(self, '__ext_fields'):
            setattr(self, '__ext_fields', {})

        return getattr(self, '__ext_fields')

    def __repr__(self):
        s = "<" + self.__table__.name + ">\n"

        ext_fields = self._get_ext_fields()
        for name, v in ext_fields.iteritems():
            if isinstance(v, unicode):
                v = v.encode('utf8')
            s += "\t%s=%s\n" % (name, v)
            
        for c in self.__table__.columns:
            v = getattr(self, c.name)
            if isinstance(v, unicode):
                v = v.encode('utf8')
            s += "\t%s=%s\n" % (c.name, v)

        return s

    def attach_ext_field(self, name, value):
        ext_fields = self._get_ext_fields()
        ext_fields[name] = value

    def toDict(self):
        d = {}
        ext_fields = self._get_ext_fields()
        for name, v in ext_fields.iteritems():
            if not name in self.__ignore_fields__:
                d[name] = v

        for c in self.__table__.columns:
            if not c.name in self.__ignore_fields__:
                d[c.name] = getattr(self, c.name)


        return d
        

Base = declarative_base()