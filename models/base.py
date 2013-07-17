#!/usr/bin/env python
# -*- coding:utf-8 -*-

import inspect

from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import Table, MetaData, Column
from sqlalchemy import Integer, String, Unicode, UnicodeText, Boolean, DateTime, Float, Text, Binary, DECIMAL
from sqlalchemy.orm import mapper, class_mapper
from sqlalchemy import func, or_

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

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SessionHolder(object):
    __metaclass__ = Singleton

    def __init__(self, Session):
        self.Session = Session

    def get_db_session(self):
        return self.Session()

    def close_session(self, db_session):
        if db_session:
            db_session.close()
            self.Session.remove()

    @classmethod
    def need_session(instance, func):
        def wrapper(*args, **kwargs):
            func_args = inspect.getargspec(func)[0]
            if not 'db_session' in func_args:
                return func(*args, **kwargs)
            else:
                has_db_session = False
                if 'db_session' in kwargs and kwargs['db_session']:
                    has_db_session = True

                if not has_db_session:
                    idx = func_args.index('db_session')
                    has_db_session = idx < len(args)

                if not has_db_session:
                    db_session = SessionHolder().get_db_session()
                    kwargs['db_session'] = db_session
                    ret = func(*args, **kwargs)
                    SessionHolder().close_session(db_session)
                    return ret

        return wrapper
    

class Entity(object):

    __table__ = None

    __ignore_fields__ = []

    @classmethod
    def get_db_session(cls):
        from tank import config
        Session = config.build_db_session(app_config)

        
        

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

    @classmethod
    @SessionHolder.need_session
    def get_by_pk(cls, pk = None, db_session = None):
        q = db_session.query(cls)
        name = class_mapper(cls).primary_key[0].name
        return q.filter_by(**{name : pk}).first()

    @classmethod
    def get_all(cls, db_session, **kvargs):
        return cls.get_all_by(db_session, **kvargs)

    @classmethod
    def _get_query(cls, db_session, **kvargs):
        q = db_session.query(cls)

        limit = offset = None

        if 'limit' in kvargs:
            limit = kvargs['limit']
            del kvargs['limit']

        if 'offset' in kvargs:
            offset = kvargs['offset']
            del kvargs['offset']

        if len(kvargs) > 0:
            q = q.filter_by(**kvargs)

        # limit and offset method must invoke after filter_by
        if limit:
            q = q.limit(limit)

        if offset:
            q = q.offset(offset)

        return q

    @classmethod
    def get_by(cls, db_session, **kvargs):
        return cls._get_query(db_session, **kvargs).first()

    @classmethod
    def get_all_by(cls, db_session, **kvargs):
        limit = offset = None
        
        if 'limit' in kvargs:
            limit = kvargs['limit']
            del kvargs['limit']

        if 'offset' in kvargs:
            limit = kvargs['offset']
            del kvargs['offset']

        print kvargs
            
        q = cls._get_query(db_session, **kvargs)

        if limit:
            q = q.limit(limit)

        if offset:
            q = q.offset(offset)

        return q.all()

    def set_attrs_by_handler(self, handler, attrs):
        for attr in attrs:
            setattr(self, attr, handler.get_argument(attr, None))

Base = declarative_base()

def wrapper_property(name, default_prop):
    def wrapper_func(func):
        def _(*args, **kwargs):
            obj = args[0]
            if hasattr(obj, name):
                return getattr(obj, name)
            _prop = func(*args, **kwargs)
            if not _prop:
                _prop = default_prop
            setattr(obj, name, _prop)
            return _prop
        return _
    return wrapper_func
