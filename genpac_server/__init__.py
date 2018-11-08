# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import os
import sys
import time
import threading
from glob import glob
from pprint import pprint
from tempfile import mkstemp
import copy
import logging

import flask
from flask import Flask, Blueprint, url_for
from flask_compress import Compress
import genpac
from genpac import GenPAC
from genpac.util import conv_bool, conv_list, conv_path

from .utils import FmtDomains, print_and_raise
from .build import start_watch, build

__version__ = '1.0a1'
__author__ = 'JinnLynn <eatfishlin@gmail.com>'
__license__ = 'The MIT License'
__copyright__ = 'Copyright 2018 JinnLynn'
__project_url__ = 'https://github.com/JinnLynn/genpac-server'

main = Blueprint('main', __name__, static_folder='static')

_DEFAULT_OPTIONS = genpac.Namespace(
    config_file=None, auth_token=None,
    autobuild_interval=3600, build_on_start=True,
    watch_enabled=True, watch_files=set(), target_path=None,
    server_rule_enabled=True, server_rule_file='server-rules.txt',
    domains_file='_genpac-server-domains', pacs={}, shortener={},
    ip_srvs={'inland': '//myip.ipip.net',
             'abroad': '//icanhazip.com',
             'gfwed': '//jeekerip.appspot.com'})


def create_app(config_file=None):
    from . import views
    app = Flask(__name__)

    read_config(app, config_file)
    app.register_blueprint(main)
    Compress(app)

    app.extensions['genpac'] = genpac.Namespace(
        last_builded=0,
        domains_proxy=[], domains_direct=[], domains_outdate=True)

    if app.config.options.build_on_start:
        build(app)
    if app.config.options.autobuild_interval > 0 or \
            app.config.options.watch_enabled:
        start_watch(app)

    return app


def read_config(app, config_file):
    options = copy.deepcopy(_DEFAULT_OPTIONS)
    cfg = {}

    def _val(key, default, *convs):
        if key not in cfg:
            return default
        val = cfg[key]
        for conv in convs:
            val = conv(val)
        return val

    def _update(attr, *convs, **kwargs):
        if not hasattr(options, attr):
            logging.warn('ATTR MISSING: {}'.format(attr))
            return
        key = kwargs.get('key', attr.strip().replace('_', '-'))
        default = kwargs['default'] if 'default' in kwargs else \
            getattr(options, attr)
        val = _val(key, default, *convs)
        setattr(options, attr, val)

    value = config_file or os.environ.get('GENPAC_CONFIG')
    value = conv_path(value)
    if not os.path.exists(value):
        print_and_raise('GenPAC Error: config file {} missing.'.format(value))
    options.config_file = value

    config = genpac.Config()
    config.read(options.config_file)
    cfg = config.section('server') or {}

    _update('auth_token')
    _update('build_on_start', conv_bool)
    _update('autobuild_interval', int)
    _update('watch_enabled', conv_bool)
    _update('watch_files', conv_list, conv_path, set,
            key='watch-extra-files')

    # 默认target_path与配置文件同目录
    _update('target_path', conv_path,
            default=os.path.dirname(options.config_file))

    _update('server_rule_enabled', conv_bool)
    _update('server_rule_file', conv_path,
            default=os.path.join(options.target_path,
                                 options.server_rule_file))
    if options.server_rule_enabled and \
            not os.path.exists(options.server_rule_file):
        with open(options.server_rule_file, 'w') as fp:
            fp.write('# GenPAC Server rules\n\n')

    _update('domains_file', conv_path,
            default=os.path.join(options.target_path,
                                 options.domains_file))

    # 侦测IP的服务器列表
    options.ip_srvs['inland'] = _val('ip.inland', options.ip_srvs['inland'])
    options.ip_srvs['abroad'] = _val('ip.abroad', options.ip_srvs['abroad'])
    options.ip_srvs['gfwed'] = _val('ip.gfwed', options.ip_srvs['gfwed'])

    cfg = config.section('server-pac')
    for k in cfg.keys():
        options.pacs[k] = cfg[k].strip('"')

    cfg = config.section('server-shortener')
    for k in cfg.keys():
        options.shortener[k] = cfg[k].strip('"')

    # 如果允许监控文件更改
    if options.watch_enabled:
        gp = GenPAC(config_file=options.config_file)
        # 添加config_file到监控列表
        options.watch_files.add(options.config_file)
        if options.server_rule_enabled:
            # 添加服务器上的规则文件
            options.watch_files.add(options.server_rule_file)
        # 添加user_rule_from到监控文件列表
        for jobs in gp.jobs:
            options.watch_files.update(jobs.user_rule_from)

    app.config.options = options
    pprint(app.config.options)
