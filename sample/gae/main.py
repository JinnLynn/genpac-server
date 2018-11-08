# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import genpac
from pprint import pprint
from genpac_server import create_app

import os

pprint(genpac.__version__)
config_file = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'data/_config.ini')

print(config_file)

app = create_app(config_file=config_file)
