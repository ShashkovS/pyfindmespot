#!/bin/bash
repo_path=/website/findmespot/py_findmespot

echo 'Обновляем код с githubа'
cd $repo_path
git pull origin master

echo 'Обновляем конфиги'
cp scripts/gunicorn.service /etc/systemd/system/gunicorn.service
cp scripts/gunicorn.socket /etc/systemd/system/gunicorn.socket
cp scripts/gunicorn.conf  /etc/tmpfiles.d/gunicorn.conf 
cp scripts/findmespot.conf /etc/nginx/conf.d/findmespot.conf

echo 'Перезапускаем всё'
systemctl stop gunicorn.socket
systemctl start gunicorn.socket
systemctl reload nginx.service
