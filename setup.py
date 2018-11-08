'''
|pypi version| |pypi license|

Web server for GenPAC.

For more information, please visit `project page`_.


.. |pypi version| image:: https://img.shields.io/pypi/v/genpac-server.svg
   :target: https://pypi.org/project/genpac-server/
.. |pypi license| image:: https://img.shields.io/pypi/l/genpac-server.svg
   :target: https://pypi.org/project/genpac-server/

.. _project page: https://github.com/JinnLynn/genpac-server/
'''
import re
import ast
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('genpac_server/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='genpac-server',
    version=version,
    license='MIT',
    author='JinnLynn',
    author_email='eatfishlin@gmail.com',
    url='https://github.com/JinnLynn/genpac-server',
    description='web server for genpac.',
    long_description=__doc__,
    packages=['genpac_server'],
    package_data={
        'genpac_server': ['templates/*', 'static/*']
    },
    install_requires=[
        'genpac>=2.1.0',
        'flask',
        'flask-compress'
    ],
    platforms='any',
    keywords='proxy pac gfwlist gfw',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
