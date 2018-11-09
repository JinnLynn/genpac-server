# -*- coding: utf-8 -*-
import os
from genpac_server import create_app

app = create_app(
    config_file=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'data/_config.ini'))
