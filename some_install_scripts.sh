# Ставим всё и настраиваем вебсервер
# Работаем в предположении, что nginx уже установлен
# https://tutorials.technology/tutorials/71-How-to-setup-Flask-with-gunicorn-and-nginx-with-examples.html


# Создаём папку проектов (если ещё не) 
cd /
mkdir -m 755 website 

# Содержимое каждого сайта будет находиться в собственном каталоге, поэтому создаём нового пользователя 
# и отдельный каталог для разграничения прав доступа:
#  -b папка в которой будет создан каталог пользователя
#  -m создать каталог
#  -U создаём группу с таким же именем как у пользователя
#  -s /bin/false отключаем пользователю shell
useradd findmespot -b /website/ -m -U -s /bin/false

# Делаем каталоги для данных сайта (файлы сайта, логи и временные файлы):
mkdir -p -m 754 /website/findmespot/www
mkdir -p -m 754 /website/findmespot/logs
mkdir -p -m 777 /website/findmespot/tmp

# Делаем юзера и его группу владельцем  всех своих папок
chown -R findmespot:findmespot /website/findmespot/

# Изменяем права доступа на каталог
chmod 755 /website/findmespot



# Добавляем юзера в группу тех, то может пользоваться установкой анаконды
usermod -a -G findmespot anaconda
# Чтобы Nginx получил доступ к файлам сайта, добавим пользователя nginx в группу
usermod -a -G findmespot nginx


# Создаём виртуальное окружение и ставим в него пакеты
cd /website/findmespot
python -m venv --without-pip findmespot_env
source findmespot_env/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
deactivate
source findmespot_env/bin/activate
pip install gunicorn flask





# Создаём ключ для ssh+github
mkdir /website/findmespot/.ssh
chmod 0700 /website/findmespot/.ssh
touch /website/findmespot/.ssh/authorized_keys
chmod 0644 /website/findmespot/.ssh/authorized_keys
ssh-keygen -t rsa -b 4096 -C "findmespot@v.shashkov.ru"
  /website/findmespot/.ssh/findmespot_rsa_key_for_github
ssh-keygen -t rsa -b 4096 -C "findmespot@v.shashkov.ru"
  /website/findmespot/.ssh/findmespot_rsa_key_for_ssh

cat /website/findmespot/.ssh/findmespot_rsa_key_for_github.pub >> /website/findmespot/.ssh/authorized_keys
cat /website/findmespot/.ssh/findmespot_rsa_key_for_ssh.pub >> /website/findmespot/.ssh/authorized_keys
# выгружаем findmespot_rsa_key_for_ssh наружу
rm -rf /website/findmespot/.ssh/findmespot_rsa_key_for_ssh*

# Копируем ключ для гитхаба
cat /website/findmespot/.ssh/findmespot_rsa_key_for_github.pub
# Вставляем в deploy keys https://github.com/ShashkovS/py_findmespot/settings/keys

# Создаём настройки для github'а
touch /website/findmespot/.ssh/config
chmod 0644 /website/findmespot/.ssh/config
echo 'Host github.com
  IdentityFile /website/findmespot/.ssh/findmespot_rsa_key_for_github' > /website/findmespot/.ssh/config

# Клонируем репу
cd /website/findmespot/
ssh-agent bash -c 'ssh-add /website/findmespot/.ssh/findmespot_rsa_key_for_github; git clone https://github.com/ShashkovS/py_findmespot.git'
cd /website/findmespot/py_findmespot
git pull origin master








# Создаём тестовое dummy-приложение
# /website/findmespot/py_findmespot
rm /website/findmespot/py_findmespot/dummy.py
touch /website/findmespot/py_findmespot/dummy.py
echo 'from flask import Flask
from werkzeug.contrib.fixers import ProxyFix  # For Gunicorn
application = Flask(__name__)
@application.route("/")
def hello():
    return """<h1>Hello world!</h1>"""
application.wsgi_app = ProxyFix(application.wsgi_app)  # For Gunicorn
if __name__ == "__main__":
    application.run(host="0.0.0.0")
' >> /website/findmespot/py_findmespot/dummy.py

# Тестово запускаем из командной строки
gunicorn dummy:application






# Даём права всем заинтересованным пинать findmespot
usermod -a -G abishev findmespot
usermod -a -G diakonov findmespot
usermod -a -G serge findmespot
usermod -a -G shuliatev findmespot
usermod -a -G yudv findmespot



# Делаем юзера владельцем всех своих папок последний раз
chown -R findmespot:findmespot /website/findmespot/









# Настраиваем автозапуск
rm -f /etc/systemd/system/findmespot.service
touch /etc/systemd/system/findmespot.service
echo '[Unit]
Description=Gunicorn instance to serve findmespot
Requires=gunicorn.socket
After=network.target

[Service]
PIDFile=/website/findmespot/app.pid
Restart=on-failure
User=findmespot
Group=nginx
RuntimeDirectory=gunicorn
WorkingDirectory=/website/findmespot/py_findmespot
Environment="PATH=/website/findmespot/findmespot_env/bin"
ExecStart=/website/findmespot/findmespot_env/bin/gunicorn  --pid /website/findmespot/app.pid  --workers 1  --bind unix:/website/findmespot/app.socket  -m 007  dummy:application
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
' >> /etc/systemd/system/findmespot.service


# Создаём socket-файл
rm -f /etc/systemd/system/gunicorn.socket
touch /etc/systemd/system/gunicorn.socket
echo '[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn/socket

[Install]
WantedBy=sockets.target
' >> /etc/systemd/system/gunicorn.socket

rm -f /etc/tmpfiles.d/gunicorn.conf 
touch /etc/tmpfiles.d/gunicorn.conf 
echo 'd /run/gunicorn 0755 findmespot findmespot -
' >> /etc/tmpfiles.d/gunicorn.conf 


# Теперь можно включить сервис Gunicorn
systemctl enable gunicorn.socket
systemctl start gunicorn.socket

# Если не запускается, то для отладки используем
# journalctl -u findmespot.service



# создаём виртуальный хост Nginx
# создаём конфигурационный файл:
rm -f /etc/nginx/conf.d/findmespot.conf
touch /etc/nginx/conf.d/findmespot.conf
echo 'server {
 listen  80;

 server_name v.shashkovs.ru www.v.shashkovs.ru;
 access_log /website/findmespot/logs/nginx_access.log;
 error_log /website/findmespot/logs/nginx_error.log;

 root /website/findmespot/py_findmespot;

 location /findmespot/ {
  proxy_pass http://unix:/website/findmespot/app.socket;
  proxy_read_timeout 300s;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_buffering off;
 }
 
 error_page 500 502 503 504 /50x.html;
 location = /50x.html {
  root /usr/share/nginx/html;
 }
}
' >> /etc/nginx/conf.d/findmespot.conf

# Проверяем корректность конфига
nginx -t

# Перезапускаем nginx
service nginx reload




