#!/usr/bin/env python
# -*- coding:utf-8 -*-

import inspect
import re

from tank.mc import cache
from tank import mc

from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import Table, MetaData, Column
from sqlalchemy import Integer, String, Unicode, UnicodeText, Boolean, DateTime, Date, Float, Text, Binary, DECIMAL
from sqlalchemy.orm import mapper, class_mapper
from sqlalchemy import func, and_, or_, desc

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

class QueryCondition(object):

    def __init__(self, value):
        self.value = value

class ConditionGT(QueryCondition):

    def __init__(self, value):
        QueryCondition.__init__(self, value)

    def get_condition(self, col):
        return col > self.value

class ConditionGE(QueryCondition):

    def __init__(self, value):
        QueryCondition.__init__(self, value)

    def get_condition(self, col):
        return col >= self.value

class ConditionLT(QueryCondition):

    def __init__(self, value):
        QueryCondition.__init__(self, value)

    def get_condition(self, col):
        return col < self.value

class ConditionLE(QueryCondition):

    def __init__(self, value):
        QueryCondition.__init__(self, value)

    def get_condition(self, col):
        return col <= self.value

class ConditionNot(QueryCondition):

    def __init__(self, value):
        QueryCondition.__init__(self, value)

    def get_condition(self, col):
        return col != self.value


def gt(value):
    return ConditionGT(value)

def ge(value):
    return ConditionGE(value)

def lt(value):
    return ConditionLT(value)

def le(value):
    return ConditionLE(value)

def neq(value):
    return ConditionNot(value)


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
                else:
                    return func(*args, **kwargs)

        return wrapper


class Entity(object):

    __table__ = None

    __ignore_fields__ = []

    def __str__(self):
        return self.__repr__()

    def _get_ext_fields(self):
        if not hasattr(self, '__ext_fields__'):
            setattr(self, '__ext_fields__', {})

        return getattr(self, '__ext_fields__')

    def __repr__(self):
        s = "<" + self.__table__.name + ">\n"

        ext_fields = self._get_ext_fields()
        for f in ext_fields:
            v = getattr(self, f)
            if isinstance(v, unicode):
                v = v.encode('utf8')

            s += "\t%s=%s\n" % (f, v)

        for c in self.__table__.columns:
            v = getattr(self, c.name)
            if isinstance(v, unicode):
                v = v.encode('utf8')
            s += "\t%s=%s\n" % (c.name, v)

        return s

    def attach_ext_field(self, name, value):
        setattr(self, name, value)

    def toDict(self):
        d = {}
        ext_fields = self._get_ext_fields()
        for f in ext_fields:
            if not f in self.__ignore_fields__:
                d[f] = getattr(self, f)

        for c in self.__table__.columns:
            if not c.name in self.__ignore_fields__:
                d[c.name] = getattr(self, c.name)


        return d

    def _del_pk_cache(self):
        pks = class_mapper(self.__class__).primary_key
        pk_values = {}

        for pk in pks:
            name = pk.name
            value = getattr(self, name)
            pk_values[name]= value

        s = ''
        for k in sorted(pk_values.iterkeys()):
            s += "%s=%s&" % (k, pk_values[k])

        print 'pk values', s
        key_template = "entity:pk:{pk}"
        key = re.sub(r'\{\w+\}', s, key_template)

        print '------ delete cache key', key
        mc.delete(key)


    @SessionHolder.need_session
    def delete(self, db_session = None):
        self._del_pk_cache()

        with db_session.begin():
            db_session.delete(self)
            db_session.flush()

    @SessionHolder.need_session
    def save(self, db_session = None):
        self._del_pk_cache()

        pks = class_mapper(self.__class__).primary_key
        new = False
        if len(pks) == 1:
            pk = pks[0]
            value = getattr(self, pk.name)
            if not value:
                new = True

        with db_session.begin():
            if new:
                db_session.add(self)
            else:
                db_session.merge(self)

            if new:
                setattr(self, pk.name, db_session.scalar("SELECT LAST_INSERT_ID()"))
            db_session.flush()

        #with db_session

    @classmethod
    @SessionHolder.need_session
    @cache('entity:pk:{pk}')
    def get_by_pk(cls, pk = None, db_session = None):
        q = db_session.query(cls)
        pks = class_mapper(cls).primary_key

        if len(pks) == 1:
            n = pks[0].name
            cond = {}
            if isinstance(pk, dict):
                cond[n] = pk[n]
            else:
                cond[n] = pk
        else:
            cond = pk

        print 'pk', cond
        values = cond.values()
        if len(values) >= 1 or values[0]:
            return q.filter_by(**cond).first()
        else:
            return None

    @classmethod
    @SessionHolder.need_session
    def get_all(cls, db_session = None, **kvargs):
        return cls.get_all_by(db_session, **kvargs)


    @classmethod
    @SessionHolder.need_session
    def count(cls, db_session = None, **kvargs):
        name = class_mapper(cls).primary_key[0].name
        q = db_session.query(func.count(getattr(cls, name)))
        cols = cls.__table__.c

        for k, v in kvargs.iteritems():
            if isinstance(v, list):
                q = q.filter(cols[k].in_(v))
            elif isinstance(v, QueryCondition):
                q = q.filter(v.get_condition(cols[k]))
            else:
                q = q.filter(cols[k] == v)

        return q.first()[0]

    @classmethod
    def _get_query(cls, db_session, **kvargs):
        q = db_session.query(cls)

        order_by = limit = offset = None

        if 'limit' in kvargs:
            limit = kvargs['limit']
            del kvargs['limit']

        if 'offset' in kvargs:
            offset = kvargs['offset']
            del kvargs['offset']

        if 'order_by' in kvargs:
            order_by = kvargs['order_by']
            del kvargs['order_by']


        cols = cls.__table__.c
        for k, v in kvargs.iteritems():
            if isinstance(v, list):
                q = q.filter(cols[k].in_(v))
            elif isinstance(v, QueryCondition):
                q = q.filter(v.get_condition(cols[k]))
            else:
                q = q.filter(cols[k] == v)

        if order_by:
            order_by_list = order_by.split(' ')
            for ob in order_by_list:
                if ob.startswith('-'):
                    q = q.order_by(desc(ob[1:]))
                else:
                    if ob.startswith('+'):
                        ob = ob[1:]
                    q = q.order_by(ob)

        if limit:
            q = q.limit(limit)

        if offset:
            q = q.offset(offset)


        return q

    @classmethod
    @SessionHolder.need_session
    def get_by(cls, db_session = None, **kvargs):

        keys = set(kvargs.keys())
        pks = set([pk.name for pk in class_mapper(cls).primary_key])

        if keys == pks:

            cond = {}
            for pk in keys:
                cond[pk] = kvargs[pk]

            return cls.get_by_pk(cond, db_session)

        return cls._get_query(db_session, **kvargs).first()

    @classmethod
    @SessionHolder.need_session
    def get_all_by(cls, db_session = None, **kvargs):
        objs = cls._get_query(db_session, **kvargs).all()
        for k, v in kvargs.iteritems():
            if isinstance(v, list):
                new_ordered = []
                for _v in v:
                    for o in objs:
                        if getattr(o, k) == _v:
                            new_ordered.append(o)
                return new_ordered

        return objs


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
