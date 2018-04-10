#!/bin/bash
repo_path=/website/findmespot/py_findmespot

echo 'Обновляем код с githubа'
cd $repo_path
git pull origin master
git fetch --all
git reset --hard origin/master


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
echo
curl -sS --unix-socket /website/findmespot/app.socket http://localhost/test_app_is_working_kQK74RxmgPPm69 | head -n 5
echo

echo 'Тестируем: дёргаем приложение через вебсервис'
echo
curl -sS http://v.shashkovs.ru/findmespot/test_app_is_working_kQK74RxmgPPm69 | head -n 5
echo
