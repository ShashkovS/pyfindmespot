#!/usr/bin/env bash
# Ставим всё и настраиваем вебсервер
# Работаем в предположении, что nginx уже установлен
# https://tutorials.technology/tutorials/71-How-to-setup-Flask-with-gunicorn-and-nginx-with-examples.html
# https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-14-04


# Создаём папку проектов (если ещё не) 
cd /
mkdir -m 755 web 

# Содержимое каждого сайта будет находиться в собственном каталоге, поэтому создаём нового пользователя 
# и отдельный каталог для разграничения прав доступа:
#  -b папка в которой будет создан каталог пользователя
#  -m создать каталог
#  -U создаём группу с таким же именем как у пользователя
#  -s /bin/false отключаем пользователю shell
useradd pyfindmespot -b /web/ -m -U -s /bin/false

# Делаем каталоги для данных сайта (файлы сайта, логи и временные файлы):
mkdir -p -m 754 /web/pyfindmespot/www
mkdir -p -m 754 /web/pyfindmespot/logs
mkdir -p -m 777 /web/pyfindmespot/tmp

# Делаем юзера и его группу владельцем  всех своих папок
chown -R pyfindmespot:pyfindmespot /web/pyfindmespot/

# Изменяем права доступа на каталог
chmod 755 /web/pyfindmespot

# Чтобы Nginx получил доступ к файлам сайта, добавим пользователя nginx в группу
usermod -a -G pyfindmespot nginx


# Создаём виртуальное окружение и ставим в него пакеты
cd /web/pyfindmespot
python3 -m venv --without-pip pyfindmespot_env
source pyfindmespot_env/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python3
deactivate
source pyfindmespot_env/bin/activate
pip install click Flask geojson gpxpy gunicorn itsdangerous Jinja2 MarkupSafe Werkzeug requests pyperclip
deactivate





# Создаём ключ для ssh+github
mkdir /web/pyfindmespot/.ssh
chmod 0700 /web/pyfindmespot/.ssh
touch /web/pyfindmespot/.ssh/authorized_keys
chmod 0644 /web/pyfindmespot/.ssh/authorized_keys
ssh-keygen -t rsa -b 4096 -C "pyfindmespot@v.shashkov.ru"
  /web/pyfindmespot/.ssh/pyfindmespot_rsa_key_for_github
ssh-keygen -t rsa -b 4096 -C "pyfindmespot@v.shashkov.ru"
  /web/pyfindmespot/.ssh/pyfindmespot_rsa_key_for_ssh

cat /web/pyfindmespot/.ssh/pyfindmespot_rsa_key_for_github.pub >> /web/pyfindmespot/.ssh/authorized_keys
cat /web/pyfindmespot/.ssh/pyfindmespot_rsa_key_for_ssh.pub >> /web/pyfindmespot/.ssh/authorized_keys
# выгружаем pyfindmespot_rsa_key_for_ssh наружу
rm -rf /web/pyfindmespot/.ssh/pyfindmespot_rsa_key_for_ssh*

# Копируем ключ для гитхаба
cat /web/pyfindmespot/.ssh/pyfindmespot_rsa_key_for_github.pub
# Вставляем в deploy keys https://github.com/ShashkovS/pyfindmespot/settings/keys

# Создаём настройки для github'а
touch /web/pyfindmespot/.ssh/config
chmod 0644 /web/pyfindmespot/.ssh/config
echo 'Host github.com
  IdentityFile /web/pyfindmespot/.ssh/pyfindmespot_rsa_key_for_github' > /web/pyfindmespot/.ssh/config

# Клонируем репу
cd /web/pyfindmespot/
ssh-agent bash -c 'ssh-add /web/pyfindmespot/.ssh/pyfindmespot_rsa_key_for_github; git clone https://github.com/ShashkovS/pyfindmespot.git'
cd /web/pyfindmespot/pyfindmespot
git pull origin master








# Создаём тестовое pyfindmespot_app-приложение
# /web/pyfindmespot/pyfindmespot
rm /web/pyfindmespot/pyfindmespot/pyfindmespot_app.py
touch /web/pyfindmespot/pyfindmespot/pyfindmespot_app.py
echo 'from flask import Flask
from werkzeug.contrib.fixers import ProxyFix  # For Gunicorn

application = Flask(__name__)
application.config["APPLICATION_ROOT"] = "/pyfindmespot"
# @application.route("/")

@application.route('/', defaults={'path': ''})
@application.route('/<path:path>')
def hello(path):
    return """<h1>Hello world!</h1><p>Path is: """ + path


application.wsgi_app = ProxyFix(application.wsgi_app)  # For Gunicorn
if __name__ == "__main__":
    application.run(host="0.0.0.0")
' >> /web/pyfindmespot/pyfindmespot/pyfindmespot_app.py

# Тестово запускаем из командной строки
gunicorn pyfindmespot_app:application






# Даём права всем заинтересованным пинать pyfindmespot
usermod -a -G abishev pyfindmespot
usermod -a -G diakonov pyfindmespot
usermod -a -G serge pyfindmespot
usermod -a -G shuliatev pyfindmespot
usermod -a -G yudv pyfindmespot



# Делаем юзера владельцем всех своих папок последний раз
chown -R pyfindmespot:pyfindmespot /web/pyfindmespot/









# Настраиваем автозапуск
rm -f /etc/systemd/system/gunicorn.pyfindmespot.service
touch /etc/systemd/system/gunicorn.pyfindmespot.service
echo '[Unit]
Description=Gunicorn instance to serve pyfindmespot
Requires=gunicorn.pyfindmespot.socket
After=network.target

[Service]
PIDFile=/web/pyfindmespot/pyfindmespot.pid
Restart=on-failure
User=pyfindmespot
Group=nginx
RuntimeDirectory=gunicorn
WorkingDirectory=/web/pyfindmespot/pyfindmespot
Environment="PATH=/web/pyfindmespot/pyfindmespot_env/bin"
ExecStart=/web/pyfindmespot/pyfindmespot_env/bin/gunicorn  --pid /web/pyfindmespot/pyfindmespot.pid  --workers 1  --bind unix:/web/pyfindmespot/pyfindmespot.socket  -m 007  pyfindmespot_app:app
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
' >> /etc/systemd/system/gunicorn.pyfindmespot.service


# Создаём socket-файл
rm -f /etc/systemd/system/gunicorn.pyfindmespot.socket
touch /etc/systemd/system/gunicorn.pyfindmespot.socket
echo '[Unit]
Description=gunicorn.pyfindmespot.socket

[Socket]
ListenStream=/web/pyfindmespot/pyfindmespot.socket

[Install]
WantedBy=sockets.target
' >> /etc/systemd/system/gunicorn.pyfindmespot.socket

rm -f /etc/tmpfiles.d/gunicorn.pyfindmespot.conf
touch /etc/tmpfiles.d/gunicorn.pyfindmespot.conf
echo 'd /run/gunicorn 0755 pyfindmespot nginx -
' >> /etc/tmpfiles.d/gunicorn.pyfindmespot.conf


# Теперь можно включить сервис Gunicorn
systemctl enable gunicorn.pyfindmespot.socket
systemctl stop gunicorn.pyfindmespot.socket
systemctl start gunicorn.pyfindmespot.socket

# Если не запускается, то для отладки используем
# journalctl -u gunicorn.pyfindmespot.service

# Проверяем (Должен вернуться ответ)
curl --unix-socket /web/pyfindmespot/pyfindmespot.socket http


# создаём виртуальный хост Nginx
# создаём конфигурационный файл:
# rm -f /etc/nginx/conf.d/nginx.pyfindmespot.conf
# touch /etc/nginx/conf.d/nginx.pyfindmespot.conf
# echo 'server {
#  listen  80;
#  listen [::]:443 ssl ipv6only=on; # managed by Certbot
#  listen 443 ssl; # managed by Certbot
#  ssl_certificate /etc/letsencrypt/live/proj179.ru/fullchain.pem; # managed by Certbot
#  ssl_certificate_key /etc/letsencrypt/live/proj179.ru/privkey.pem; # managed by Certbot
#  include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
#  ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

#  server_name proj179.ru;
#  access_log /web/pyfindmespot/logs/nginx_access.log;
#  error_log /web/pyfindmespot/logs/nginx_error.log;

#  root /web/pyfindmespot/pyfindmespot;

#  location /pyfindmespot/ {
#   proxy_pass http://unix:/web/pyfindmespot/pyfindmespot.socket;
#   proxy_read_timeout 300s;
#   proxy_set_header Host $host;
#   proxy_set_header X-Real-IP $remote_addr;
#   proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#   proxy_buffering off;
#  }

#  location ~* \.(css|js|png|gif|jpg|jpeg|ico)$ {
#   root /web/pyfindmespot/pyfindmespot;
#   expires 1d;
#  }

#  error_page 500 502 503 504 /50x.html;
#  location = /50x.html {
#   root /usr/share/nginx/html;
#  }
# }
# ' >> /etc/nginx/conf.d/nginx.pyfindmespot.conf


rm -f /etc/nginx/default.d/nginx.pyfindmespot.conf
touch /etc/nginx/default.d/nginx.pyfindmespot.conf
echo '
 location /pyfindmespot/ {
  # Socket is configured at gunicorn.pyfindmespot.socket and gunicorn.pyfindmespot.service
  proxy_pass http://unix:/website/pyfindmespot/pyfindmespot.socket;
  proxy_read_timeout 300s;
  # Setting headers for prefix_and_wsgi_proxy_fix
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Scheme $scheme;
  proxy_set_header X-Forwarded-Host $server_name;
  proxy_set_header X-Script-Name /pyfindmespot;
  proxy_buffering off;
 }

 location /pyfindmespot/static/ {
  root /web/pyfindmespot/pyfindmespot/static;
  expires 1d;
 }
' >> /etc/nginx/default.d/nginx.pyfindmespot.conf




# Проверяем корректность конфига
nginx -t

# Перезапускаем nginx
nginx -s reload


# Перезапускаем всё
systemctl stop gunicorn.pyfindmespot.socket
systemctl start gunicorn.pyfindmespot.socket
systemctl reload nginx.service




# cgi
yum groupinstall 'Development Tools'
yum install fcgi-devel spawn-fcgi
cd /usr/local/src/
git clone git://github.com/gnosek/fcgiwrap.git
cd fcgiwrap
autoreconf -i
./configure
make
make install
echo '
FCGI_SOCKET=/var/run/fcgiwrap.socket
FCGI_PROGRAM=/usr/local/sbin/fcgiwrap
FCGI_USER=nginx
FCGI_GROUP=nginx
FCGI_EXTRA_OPTIONS="-M 0700"
OPTIONS="-u $FCGI_USER -g $FCGI_GROUP -s $FCGI_SOCKET -S $FCGI_EXTRA_OPTIONS -F 1 -P /var/run/spawn-fcgi.pid -- $FCGI_PROGRAM"
' >> /etc/sysconfig/spawn-fcgi

# OPTIONS="-u $FCGI_USER -g $FCGI_GROUP -s $FCGI_SOCKET -S $FCGI_EXTRA_OPTIONS -F 1 -P /var/run/spawn-fcgi.pid -- $FCGI_PROGRAM -f"
# чтобы логи пробрасывались в nginx


systemctl start spawn-fcgi
file /var/run/fcgiwrap.socket
chkconfig --add spawn-fcgi


#  установим консольные утилиты для управления политиками SELinux:
yum install -y policycoreutils-python policycoreutils-newrole policycoreutils-restorecond setools-console

# Разрешаем запускать cgi в папке
semanage fcontext -a -t httpd_sys_script_exec_t "/web/pyfindmespot/pyfindmespot/cgi-bin(/.*)?"
semanage fcontext -a -t httpd_sys_rw_content_t "/web/pyfindmespot/pyfindmespot/cgi-bin(/.*)?"
semanage fcontext -a -t httpd_var_run_t '/var/run/fcgiwrap(/.*)?'
restorecon -r -v /web/pyfindmespot/pyfindmespot

# логи безопасности
tail -f /var/log/audit/audit.log

# сделать запускаемым
chmod 774 /web/pyfindmespot/pyfindmespot/cgi-bin/github_commit_webhook.py

# Проверка прав
namei -l /web/pyfindmespot/pyfindmespot/cgi-bin/github_commit_webhook.py
sudo -u nginx /web/pyfindmespot/cgi-bin/github_commit_webhook.py

# Разрешим nginx'у перезапускать сервис
rm -f /etc/sudoers.d/pyfindmespot
touch /etc/sudoers.d/pyfindmespot
echo '
%nginx ALL= NOPASSWD: /bin/systemctl stop gunicorn.pyfindmespot.socket
%nginx ALL= NOPASSWD: /bin/systemctl start gunicorn.pyfindmespot.socket
%nginx ALL= NOPASSWD: /bin/systemctl restart gunicorn.pyfindmespot.socket
' >> /etc/sudoers.d/pyfindmespot

# Проверка прав
sudo -u nginx /web/pyfindmespot/cgi-bin/pull_and_restart.sh



#!/bin/bash
repo_path=/web/pyfindmespot/pyfindmespot

echo 'Обновляем код с githubа'
cd $repo_path
git pull origin master
git fetch --all
git reset --hard origin/master

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
yes | cp -u -f /web/pyfindmespot/pyfindmespot/config/nginx.pyfindmespot.conf /etc/nginx/conf.d/nginx.pyfindmespot.conf

echo 'Перезапускаем всё'
systemctl start gunicorn.pyfindmespot.socket
systemctl reload nginx.service

echo 'Тестируем: дёргаем сокет локально'
echo
curl -sS --unix-socket /web/pyfindmespot/pyfindmespot.socket http://localhost/test_app_is_working_kQK74RxmgPPm69 | head -n 5
echo

echo 'Тестируем: дёргаем приложение через вебсервис'
echo
curl -sS http://proj179.ru/pyfindmespot/test_app_is_working_kQK74RxmgPPm69 | head -n 5
echo
