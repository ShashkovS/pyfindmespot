#!/bin/bash
repo_path=/web/pyfindmespot/pyfindmespot

echo 'Обновляем код с githubа'
cd $repo_path
git reset --hard HEAD && git pull origin master

echo 'Переходим в venv'
source ../pyfindmespot_env/bin/activate

echo 'Ставим библиотеки'
pip install -r requirements.txt


echo 'Стопим gunicorn'
systemctl stop gunicorn.pyfindmespot.socket

echo 'Обновляем конфиги'
yes | cp -u -f /web/pyfindmespot/pyfindmespot/config/gunicorn.pyfindmespot.service /etc/systemd/system/gunicorn.pyfindmespot.service
yes | cp -u -f /web/pyfindmespot/pyfindmespot/config/gunicorn.pyfindmespot.socket /etc/systemd/system/gunicorn.pyfindmespot.socket
yes | cp -u -f /web/pyfindmespot/pyfindmespot/config/gunicorn.pyfindmespot.conf  /etc/tmpfiles.d/gunicorn.pyfindmespot.conf
yes | cp -u -f /web/pyfindmespot/pyfindmespot/config/nginx.pyfindmespot.conf /etc/nginx/default.d/nginx.pyfindmespot.conf

echo 'Перезапускаем всё'
systemctl daemon-reload
systemctl restart gunicorn.pyfindmespot.socket
# Проверяем корректность конфига
nginx -t
# Перезапускаем nginx
systemctl reload nginx.service

echo 'Тестируем: дёргаем сокет локально'
echo
curl -sS --unix-socket /web/pyfindmespot/pyfindmespot.socket http://localhost/test_app_is_working_kQK74RxmgPPm69 | head -n 5
echo

echo 'Тестируем: дёргаем приложение через вебсервис'
echo
curl -sS https://proj179.ru/pyfindmespot/test_app_is_working_kQK74RxmgPPm69 | head -n 5
echo
