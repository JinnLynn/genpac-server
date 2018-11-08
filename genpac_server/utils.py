# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import hashlib
from urllib import urlencode
from werkzeug.urls import url_decode

import genpac
from genpac import surmise_domain, FatalError
from genpac.util import replace_all


@genpac.formater('genpac-server-domains')
class FmtDomains(genpac.FmtBase):
    def __init__(self, *args, **kwargs):
        super(FmtDomains, self).__init__(*args, **kwargs)

    def generate(self, replacements):
        gfwed = ['p,{}'.format(s) for s in self.gfwed_domains]
        ignored = ['d,{}'.format(s) for s in self.ignored_domains]
        return '\n'.join(gfwed + ignored).strip()


def calc_hash(content):
    m = hashlib.md5()
    m.update(content)
    return m.hexdigest()


def get_genpac_version():
    return genpac.__version__


def print_and_raise(msg):
    print(msg)
    raise FatalError(msg)


def query2replacements(query):
    if isinstance(query, basestring):
        query = url_decode(query)
    replacements = {}
    for k, v in query.iteritems():
        if k.startswith('__') and k.endswith('__'):
            replacements[k] = v
    return replacements


def replacements2query(replacements):
    return urlencode(sorted(replacements.items()))
