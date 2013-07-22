#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
Configuration, may should put into lib repository
'''

import os
import logging
import imp

import yaml
import logger

_loaded = False
_config = None

def _process(app_config):
    gvars = globals()
    lvars = locals()
    
    if type(app_config) == dict:
        nd = {}
        for key, value in app_config.iteritems():
            if type(value) == str:
                if value.startswith('(') and value.endswith(')'):

                    value = value[1:-1]
                    ridx = value.rfind('.')
                    module_name = value[:ridx]
                    idx = -1
                    while True:
                        idx = module_name.find('.', idx + 1)
                        if idx < 0:
                           break 
                        mn = module_name[:idx]
                        __import__(mn, gvars, lvars, [''], 0)
                    __import__(module_name, gvars, lvars, [''], 0)

                    nd[key] = eval(value, gvars, lvars)
                    try:
                        nd[key] = int(nd[key])
                    except:
                        pass
                        
                else:
                    nd[key] = value
            elif type(value) == list:
                nd[key] = _process(value)
            elif type(value) == dict:
                nd[key] = _process(value)
            else:
                nd[key] = value
            
        return nd
    elif type(app_config) == list:
        nl = []
        for v in app_config:
            nl.append(v)
        return nl
    else:
        return app_config


def _parse(conf, runtime='development'):
    final_conf = {}
    if 'global' in conf and isinstance(conf['global'], dict):
        final_conf = conf['global']

    if runtime in conf:
        runtime_dict = conf[runtime]
        if isinstance(runtime_dict, dict):
            for k, v in runtime_dict.iteritems():
                final_conf[k] = v

    final_conf = _process(final_conf)
    final_conf['runtime'] = runtime
    if 'application' in conf:
        final_conf['application'] = conf['application']
        
    return final_conf

def build(running_dir = ''):
    global _loaded, _config
    if _loaded:
        return _config
    
    import sys


    """
    home_env_name = project_prefix + '_HOME'
    if not home_env_name in os.environ:
        print 'Please set environment variable %s' % (home_env_name,)
        exit()
    """
        
    config_dir =  "%s/conf" % (running_dir, )
    config_file = "%s/conf/app.yaml" % (running_dir, )
    local_config_file = '%s/conf/app.local.yaml' % (running_dir, )
        
    if not os.path.exists(config_file):
        print 'No application configuration file found, in ', config_file
        exit()

    stream = file(config_file, 'r')
    conf = yaml.load(stream)
    app_name = conf['application']['name']
    
    app_prefix = app_name.upper().replace('.', '_')
    runtime_name = app_prefix + '_RUNTIME'
    runtime = runtime_name in os.environ and os.environ[runtime_name] or 'development'
    
    config = _parse(conf, runtime)
    if os.path.exists(local_config_file):
        stream = file(local_config_file, 'r')
        local_conf = yaml.load(stream)
        if local_conf:
            config.update(local_conf)

    config['runtime'] = runtime
    config['running_home'] = running_dir

    if 'logging_file' in config:
        logging_file = config['logging_file']
    else:
        logging_file = config_dir + '/logconf.ini'
    config['logging_file'] = logging_file

    for key, v in config.iteritems():
        if isinstance(v, str):
            config[key] = v.replace('$CONF_DIR', config_dir)

    #logging_file = logging_file.replace('$CONF_DIR', config_dir)
    #config['logging_file'] = logging_file
    logger.config(config['logging_file'])



    _loaded = True
    _config = config
    return config

def get_config():
    global _config
    return _config

def build_db_session(app_config):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session
    from sqlalchemy.pool import NullPool

    connect_args = {
        'user': app_config['mysql']['username'],
        'passwd': app_config['mysql']['password'],
        'charset': 'utf8'
        }
    db_url = 'mysql://%s:%s/%s?charset=utf8&use_unicode=1' \
             % (app_config['mysql']['host_master'],
                app_config['mysql']['port_master'],
                app_config['mysql']['database'],
                )
    echo = 'echo' in app_config['mysql'] and app_config['mysql']['echo']
    
    engine = create_engine(db_url,
                           connect_args = connect_args,
                           poolclass=NullPool,
                           echo=echo)
    #some_engine = create_engine('postgresql://scott:tiger@localhost/')
    Session = scoped_session(
        sessionmaker(bind=engine, autocommit=True, autoflush=True, expire_on_commit=False)
    )

    return Session

def quick_config(running_dir):
    app_config = build(running_dir)
    Session = build_db_session(app_config)
    from tank.models.base import SessionHolder
    SessionHolder(Session)
    return app_config


if __name__ == '__main__':
    pass
    

