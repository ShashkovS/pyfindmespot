#!/bin/bash
repo_path=/website/findmespot/py_findmespot

echo 'Обновляем код с githubа'
cd $repo_path
git pull origin master

echo 'Обновляем конфиги'
cp -u config/gunicorn.service /etc/systemd/system/gunicorn.service
cp -u config/gunicorn.socket /etc/systemd/system/gunicorn.socket
cp -u config/gunicorn.conf  /etc/tmpfiles.d/gunicorn.conf 
cp -u config/findmespot.conf /etc/nginx/conf.d/findmespot.conf

echo 'Перезапускаем всё'
systemctl stop gunicorn.socket
systemctl start gunicorn.socket
systemctl reload nginx.service
