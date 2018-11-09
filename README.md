GenPAC Server
=============

[![pypi-version]][pypi] [![pypi-license]][pypi] [![demo-img]][demo-link]

GenPAC的服务器端应用，定时或按需生成GenPAC所支持的代理配置文件。

![Screenshot](https://github.com/JinnLynn/genpac-server/raw/master/sample/screenshot.png)

## 演示

http://genpac-server.appspot.com/

[PAC Template](/sample/gae/data/_config.ini#L15):  https://genpac-server.appspot.com/pac/outer

[Shortener](/sample/gae/data/_config.ini#L20): https://genpac-server.appspot.com/s/gwd

[File Download](/sample/gae/data/_config.ini#L46):

* https://genpac-server.appspot.com/file/ss.acl

* https://genpac-server.appspot.com/file/dnsmasq.tpl

* https://genpac-server.appspot.com/file/dnsmasq.tpl?__DNS__=8.8.8.8%2353&__IPSET__=GFWIPSET

## 安装

```shell
# 安装或更新
$ pip install -U genpac-server
# 或从github安装更新开发版本
$ pip install -U https://github.com/JinnLynn/genpac-server/archive/master.zip

# 卸载
$ pip uninstall genpac-server
```

## 运行

### 本地运行测试

```shell
mkdir genpac-server-test
cd genpac-server-test

curl -sL -O https://github.com/JinnLynn/genpac-server/raw/master/sample/app.py
curl -sL -O https://github.com/JinnLynn/genpac-server/raw/master/sample/config.ini

FLASK_APP=app.py FLASK_DEBUG=1 GENPAC_CONFIG=config.ini flask run
```

### Google App Engine

[GAE README](/sample/gae/README.md)

[pypi]:             https://pypi.org/project/genpac-server/
[pypi-version]:     https://img.shields.io/pypi/v/genpac-server.svg?style=flat
[pypi-license]:     https://img.shields.io/pypi/l/genpac-server.svg?style=flat
[demo-link]:        http://genpac-server.appspot.com/
[demo-img]:         https://img.shields.io/badge/Demo-GAE-orange.svg
