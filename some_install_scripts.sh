
# Ставим вебсервер на flask
adduser findmespot_user
passwd findmespot_user
  Здесь-был-пароль
gpasswd -a findmespot_user anaconda
echo 'export PATH="/opt/miniconda3/bin:$PATH"' >> /home/findmespot_user/.bashrc
# создаём ключ
ssh-keygen 
  /home/findmespot_user/.ssh/findmespot_user_rsa_key
cat /home/findmespot_user/.ssh/findmespot_user_rsa_key.pub >> /home/findmespot_user/.ssh/authorized_keys
cat /home/findmespot_user/.ssh/authorized_keys
rm -rf /home/findmespot_user/.ssh/findmespot_user_rsa_key.pub
# Выгружаем /home/findmespot_user/.ssh/findmespot_user_rsa_key, конвертируем при помощи puttygen
rm -rf /home/findmespot_user/.ssh/findmespot_user_rsa_key

echo 'export PATH="/opt/miniconda3/bin:$PATH"' >> /home/findmespot_user/.bashrc


chown -R findmespot_user /home/findmespot_user/









# Добавляем дырку для портов
mkdir /home/findmespot_user/.ssl
chmod 0700 /home/findmespot_user/.ssl
# Если есть нормальные сертификаты, то копируем их себе
cp /etc/letsencrypt/live/v.shashkovs.ru/fullchain.pem /home/findmespot_user/.ssl/fullchain.pem
cp /etc/letsencrypt/live/v.shashkovs.ru/privkey.pem /home/findmespot_user/.ssl/privkey.pem
# Иначе генерим
openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout /home/findmespot_user/.ssl/privkey.pem -out /home/findmespot_user/.ssl/fullchain.pem


chmod 0644 /home/findmespot_user/.ssl/*


# Создаём папку проекта и основной файл
mkdir /home/findmespot_user/find_web_server
chmod 0700 /home/findmespot_user/find_web_server
touch /home/findmespot_user/find_web_server/main.py
chmod 0644 /home/findmespot_user/find_web_server/main.py





















# Создаём ключ для ssh+github
mkdir /home/findmespot_user/.ssh
chmod 0700 /home/findmespot_user/.ssh
touch /home/findmespot_user/.ssh/authorized_keys
chmod 0644 /home/findmespot_user/.ssh/authorized_keys
ssh-keygen -t rsa -b 4096 -C "findmespot_user@v.shashkov.ru"
  /home/findmespot_user/.ssh/findmespot_user_rsa_key_for_github
ssh-keygen -t rsa -b 4096 -C "findmespot_user@v.shashkov.ru"
  /home/findmespot_user/.ssh/findmespot_user_rsa_key_for_ssh

cat /home/findmespot_user/.ssh/findmespot_user_rsa_key_for_github.pub >> /home/findmespot_user/.ssh/authorized_keys
cat /home/findmespot_user/.ssh/findmespot_user_rsa_key_for_ssh.pub >> /home/findmespot_user/.ssh/authorized_keys
# выгружаем findmespot_user_rsa_key_for_ssh наружу
rm -rf /home/findmespot_user/.ssh/findmespot_user_rsa_key_for_ssh*

# Копируем ключ для гитхаба
cat /home/findmespot_user/.ssh/findmespot_user_rsa_key_for_github.pub
# Вставляем в deploy keys https://github.com/ShashkovS/py_findmespot/settings/keys


# Создаём настройки для github'а
touch /home/findmespot_user/.ssh/config
chmod 0644 /home/findmespot_user/.ssh/config
echo 'Host github.com
  IdentityFile /home/findmespot_user/.ssh/findmespot_user_rsa_key_for_github' > /home/findmespot_user/.ssh/config

# Клонируем репу
cd /home/findmespot_user/find_web_server
ssh-agent bash -c 'ssh-add /home/findmespot_user/.ssh/findmespot_user_rsa_key_for_github; git clone https://github.com/ShashkovS/py_findmespot.git'
cd /home/findmespot_user/find_web_server
git pull origin master

# Создаём виртуальное окружение и ставим туда пакеты
cd /home/findmespot_user/find_web_server
python -m venv --without-pip findmespot_env
source findmespot_env/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
deactivate
source findmespot_env/bin/activate
pip install -r ~/find_web_server/requirements.txt


nohup /home/findmespot_user/find_web_server/findmespot_env/bin/python /home/findmespot_user/find_web_server/py_findmespot/main.py > find_web_server.log &
