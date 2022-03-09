#!/usr/bin/env bash

mkdir -p /config/nginx/site-confs
mkdir -p /config/log/nginx
[[ ! -f /config/nginx/nginx.conf ]] && \
  cp /defaults/nginx.conf /config/nginx/nginx.conf
[[ ! -f /config/nginx/site-confs/default ]] && \
  cp /defaults/default /config/nginx/site-confs/default

chown -R nbxyz:nbxyz /assets
chown -R nbxyz:nbxyz /var/lib/nginx
chown -R nbxyz:nbxyz /var/log/nginx
chown -R nbxyz:nbxyz /config

supervisord -c /etc/supervisor.conf
