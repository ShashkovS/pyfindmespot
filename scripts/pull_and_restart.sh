#!/bin/bash
repo_path=/website/findmespot/py_findmespot

echo 'Обновляем код с githubа'
cd $repo_path
git pull origin master

echo 'Перезапускаем всё'
systemctl stop gunicorn.socket
systemctl start gunicorn.socket
systemctl reload nginx.service
