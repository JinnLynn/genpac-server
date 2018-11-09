# Google App Engie

在GAE上运行，见 https://genpac-server.appspot.com/

注: GAE无法正常的服务文件系统，因此自动生成等功能是被禁用的，需在本地生成

## 本地调试运行

安装GAE环境后

```
pip install -U genpac-server
# 生成
python -c "import genpac, genpac_server; genpac.run()" -c data/_config.ini
# 安装GAE环境依赖
pip install -U -t libs -r requirements.txt
# 运行
dev_appserver.py app.yaml
```

## 发布到GAE

```
python -c "import genpac, genpac_server; genpac.run()" -c data/_config.ini
gcloud app deploy --project PROJECT_ID
```
