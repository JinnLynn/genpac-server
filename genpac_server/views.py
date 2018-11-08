# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import os
import time
from functools import wraps
from urlparse import urlparse
from pprint import pprint

from flask import Flask, Response, render_template, request, url_for
from flask import current_app, jsonify, redirect
import genpac

from . import __version__, __project_url__
from . import main
from .utils import calc_hash, surmise_domain, replace_all, get_genpac_version
from .utils import query2replacements, replacements2query


def send_file(filename, replacements={}, mimetype=None, add_etags=True):
    # 忽略文件名以`_`开始的文件
    if filename.startswith('_'):
        return current_app.make_response(('Not Found.', 404))

    replacements.update(query2replacements(request.values))

    try:
        if not os.path.isabs(filename):
            filename = os.path.abspath(
                os.path.join(current_app.config.options.target_path,
                             filename))

        with open(filename) as fp:
            content = fp.read()
        if replacements:
            content = replace_all(content, replacements)

        resp = current_app.make_response(content)
        resp.mimetype = mimetype or 'text/plain'
        resp.last_modified = os.path.getmtime(filename)

        if add_etags:
            etag = '{}-{}-{}-{}'.format(filename,
                                        os.path.getmtime(filename),
                                        os.path.getsize(filename),
                                        replacements2query(replacements))
            etag = calc_hash(etag)
            resp.set_etag(etag)
        return resp
    except Exception as e:
        print('GenPAC Error: {}'.format(e))

    return current_app.make_response(('Not Found.', 404))


def is_authorized():
    if not current_app.config.options.auth_token:
        return True

    auth_token = request.headers.get('Token', None)
    if auth_token is None:
        auth_token = request.values.get('token', None)
    if auth_token == current_app.config.options.auth_token:
        return True

    return False


def authorized(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if is_authorized():
            return func(*args, **kwargs)
        return current_app.make_response(('Unauthorized.', 401))
    return wrapper


def make_res_data(data={}, code=0, msg='成功'):
    return jsonify({'data': data, 'code': code, 'msg': msg})


@main.before_request
def load_domains():
    if not current_app.extensions['genpac'].domains_outdate:
        return
    current_app.logger.info('Domains Loaded.')
    with open(current_app.config.options.domains_file) as fp:
        domains = {'p': [], 'd': []}
        for line in fp.readlines():
            t, d = line.split(',')
            domains[t.strip()].append(d.strip())
        current_app.extensions['genpac'].domains_proxy = domains['p']
        current_app.extensions['genpac'].domains_direct = domains['d']
        current_app.extensions['genpac'].domains_outdate = False


@main.app_template_global('powered_by')
def powered_by():
    try:
        if current_app.extensions['genpac'].last_builded <= 0:
            statinfo = os.stat(current_app.config.options.domains_file)
            current_app.extensions['genpac'].last_builded = statinfo.st_mtime
    except Exception:
        build_date = '-'
    else:
        build_date = time.strftime(
            '%Y-%m-%d %H:%M:%S',
            time.localtime(current_app.extensions['genpac'].last_builded))
    pb = 'Last Builded: {}&nbsp;&nbsp;&nbsp;' \
        'Powered by <a href="{}">GenPAC v{}</a> ' \
        '<a href="{}">GenPAC-Server v{}</a>'
    return pb.format(
        build_date,
        genpac.__project_url__, get_genpac_version(),
        __project_url__, __version__)


@main.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html',
                           ip_srvs=current_app.config.options.ip_srvs)


@main.route('/pac/<location>/', methods=['GET', 'POST'])
@authorized
def get_pac(location):
    proxy = current_app.config.options.pacs.get(location) or location
    return send_file('pac.tpl', replacements={'__PROXY__': proxy},
                     mimetype='application/javascript')


@main.route('/file/<filename>', methods=['GET', 'POST'])
@authorized
def get_file(filename):
    return send_file(filename)


@main.route('/rules/', methods=['GET', 'POST'])
def rules():
    if not current_app.config.options.server_rule_enabled:
        return current_app.make_response(('Not Found.', 404))

    content = ''
    try:
        with open(current_app.config.options.server_rule_file) as fp:
            content = fp.read()
    except Exception as e:
        pass

    return render_template('rules.html',
                           content=content,
                           action_url=url_for('.rules_update'),
                           token=request.values.get('token', ''))


@main.route('/s/<code>', methods=['POST', 'GET'])
@authorized
def shortener(code):
    try:
        code_cfg = current_app.config.options.shortener.get(code)
        cfgs = code_cfg.split(' ')
        cfgs.append('')
        filename, query = cfgs[0:2]
    except Exception as e:
        print('shortener ERROR: {}'.format(e))
        return current_app.make_response(('Not Found.', 404))

    rms = query2replacements(query)
    return send_file(filename, replacements=rms)


@main.route('/test/', methods=['GET', 'POST'])
def test():
    url = request.values.get('url', None)
    if not url:
        return make_res_data(code=1, msg='地址不能为空')

    data = current_app.extensions['genpac']
    domain = surmise_domain(url)
    return make_res_data(data={
        'd': domain in data.domains_direct,
        'p': domain in data.domains_proxy,
        'domain': domain,
        'url': url})


@main.route('/rules-update/', methods=['POST'])
def rules_update():
    if not current_app.config.options.server_rule_enabled:
        return make_res_data(code=404, msg='服务端用户规则未启用')

    if not is_authorized():
        return make_res_data(code=401, msg='未授权, token错误')

    try:
        content = request.form.get('rules', '')
        with open(current_app.config.options.server_rule_file, 'w') as fp:
            fp.write(content.strip())
        return make_res_data()
    except Exception as e:
        return make_res_data(code=1, msg='出错了, {}'.format(e))


@main.route('/ip/')
def show_ip():
    ip = request.remote_addr
    return Response(
        '{}\n'.format(ip), mimetype="text/plain",
        headers={'X-Your-Ip': ip,
                 'Access-Control-Allow-Origin': '*'})
