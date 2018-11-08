# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import os
import time
import threading
from glob import glob

import genpac
from genpac import GenPAC, Config, Namespace


# 使用进程 uwsgi需使用参数--enable-threads
# REF:
# https://stackoverflow.com/questions/32059634/python3-threading-with-uwsgi
def start_watch(app):
    t = threading.Thread(target=watch, args=[app])
    t.setDaemon(True)
    t.start()
    return t


def watch(app):
    with app.app_context():
        if not app.config.options.config_file:
            print('GenPAC: config file missing, watch can\'t start.')
            return
        print('Start Watch...')
        mtimes = {}
        while True:
            if app.config.options.watch_enabled:
                for filename in app.config.options.watch_files:
                    # print(filename)
                    try:
                        mtime = os.stat(filename).st_mtime
                    except OSError:
                        continue

                    old_time = mtimes.get(filename)
                    mtimes[filename] = mtime
                    if old_time is None:
                        continue
                    elif mtime > old_time:
                        print('GenPAC: {} changed.'.format(filename))
                        build(app)
            autobuild_interval = app.config.options.autobuild_interval
            passed = time.time() - app.extensions['genpac'].last_builded
            if autobuild_interval > 0 and passed > autobuild_interval:
                build(app)
            time.sleep(1)


def build(app):
    print('GenPAC: rebuild...')
    try:
        gp = GenPAC(config_file=app.config.options.config_file,
                    argv_enabled=False)
        gp.add_job({'format': 'genpac-server-domains',
                    'output': app.config.options.domains_file})
        if app.config.options.server_rule_enabled:
            with open(app.config.options.server_rule_file, 'r') as fp:
                for line in fp.readlines():
                    gp.add_rule(line.strip())
        gp.run()
    except Exception as e:
        print('GenPAC: build fail: {}'.encode('utf-8').format(e))
    else:
        # 删除hash文件
        for hashfile in glob(os.path.join(app.config.options.target_path,
                                          '*.hash')):
            os.remove(hashfile)
        print('GenPAC: build success.')
        app.extensions['genpac'].domains_outdate = True
        app.extensions['genpac'].last_builded = time.time()
