#!/bin/bash
repo_path=/website/findmespot/py_findmespot

echo 'Обновляем код с githubа'
cd $repo_path
git pull origin master

echo 'Стопим gunicorn'
systemctl stop gunicorn.socket

echo 'Обновляем конфиги'
yes | cp -u -f /website/findmespot/py_findmespot/config/gunicorn.service /etc/systemd/system/gunicorn.service
yes | cp -u -f /website/findmespot/py_findmespot/config/gunicorn.socket /etc/systemd/system/gunicorn.socket
yes | cp -u -f /website/findmespot/py_findmespot/config/gunicorn.conf  /etc/tmpfiles.d/gunicorn.conf 
yes | cp -u -f /website/findmespot/py_findmespot/config/findmespot.conf /etc/nginx/conf.d/findmespot.conf

echo 'Перезапускаем всё'
systemctl start gunicorn.socket
systemctl reload nginx.service

echo 'Тестируем: дёргаем сокет локально'
curl --unix-socket /website/findmespot/app.socket http | head -n 3

echo 'Тестируем: дёргаем приложение через вебсервис'
curl http://v.shashkovs.ru/findmespot/test | head -n 3
