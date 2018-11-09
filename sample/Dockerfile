FROM jinnlynn/alpine

LABEL maintainer="JinnLynn <eatfishlin@gmail.com>"

# 配置文件
ENV GENPAC_CONFIG /app/etc/config.ini

RUN set -ex && \
    apk add --no-cache python && \
    wget -O- https://bootstrap.pypa.io/get-pip.py | python && \
    apk add --no-cache --virtual .build-deps build-base linux-headers python-dev && \
    pip install -U --no-cache-dir genpac-server uwsgi && \
    apk del --no-cache .build-deps

COPY app.py /app/opt
COPY config.ini /app/etc

WORKDIR /app/opt

EXPOSE 80

CMD ["uwsgi", "--http", ":80", "--module", "app:app"]
