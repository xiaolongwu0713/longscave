#/bin/bash

# usage: deploy.sh openssl|certbot

# ssl method
myssl=openssl
myssl=$1

## add user
id -u xiaowu
if [ $? == 1 ];then
useradd xiaowu
echo "xiaowu" | passwd -f xiaowu --stdin
fi


## python installatin
pyv="$(python --version 2>&1)"
pyversion=`echo $pyv | awk -F'.' '{print $1}' | awk -F ' ' '{print $2}'`

if [ $pyversion == 2 ];then
	yum -y install sqlite-devel zlib-devel xml *openssl*   openssl*  gcc  libffi-dev
	cd /root
	wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tgz
	tar -zxvf Python-3.6.4.tgz
	cd Python-3.6.4
	./configure --prefix=/usr/python --enable-loadable-sqlite-extensions --enable-optimizations --with-ssl
	make && make install
fi

if [ $pyversion == 2 ];then
	mv /usr/bin/python /usr/bin/python.bak
	mv /usr/bin/pip /usr/bin/pip.bak
	ln -s /usr/python/bin/python3 /usr/bin/python
	ln -s /usr/python/bin/pip3 /usr/bin/pip
	sed -l 1 -i "s/python/python.bak/g" /usr/bin/yum
	sed -l 1 -i "s/python/python.bak/g" /usr/libexec/urlgrabber-ext-down
fi


if [ ! -f /usr/python/venv/longscave/bin/activate ];then
## python vertirtual env
echo "creating python venv env at /usr/python/venv/longscave"
chmod a+w -R /usr/python
python -m venv /usr/python/venv/longscave
source /usr/python/venv/longscave/bin/activate
fi


if [ ! -d "/home/xiaowu/longscave/app" ];then
## get git repo
echo "git clone longscave from GitHub"
yum -y install git
cd /home/xiaowu
git clone https://github.com/xiaolongwu1987/longscave.git
#mv microblog longscave
cd longscave
source /usr/python/venv/longscave/bin/activate
echo "pip install requirements"
pip install -r requirements.txt  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
echo "pip install pymysql gunicorn"
pip install pymysql gunicorn
chown xiaowu:xiaowu -R /home/xiaowu/longscave
fi


# install guess_language package
source /usr/python/venv/longscave/bin/activate
pip freeze | grep guess-language
if [ $? == 1 ];then
echo "install guess_language"
yum install -y wget
wget https://files.pythonhosted.org/packages/8b/4f/9ed0280b24e9e6875c3870a97659d0106a14e36db0d7d65c5277066fc7d0/guess_language-spirit-0.5.3.tar.bz2
tar -jxvf guess_language-spirit-0.5.3.tar.bz2
source /usr/python/venv/longscave/bin/activate
cd /root/guess_language-spirit-0.5.3
python setup.py install
fi


# configure supervisor
if [ ! -d "/etc/supervisor" ];then
mkdir /etc/supervisor
mkdir /etc/supervisor/conf.d
cd /root
git clone https://github.com/Supervisor/supervisor.git
cd supervisor
python setup.py install
/usr/python/bin/echo_supervisord_conf > /etc/supervisor/supervisord.conf
cat>>/etc/supervisor/supervisord.conf<<EOF
[include]
files = /etc/supervisor/conf.d/*.ini
EOF

touch /etc/supervisor/conf.d/longscave.ini
cat>>/etc/supervisor/conf.d/longscave.ini<<EOF
[program:longscave]
command=/usr/python/venv/longscave/bin/gunicorn -b localhost:8000 -w 4 longscave:app
directory=/home/xiaowu/longscave
user=xiaowu
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
EOF
/usr/python/bin/supervisord -c /etc/supervisor/supervisord.conf
fi

netstat -tnpl | grep 8000
if [ $? == 1 ]; then
	echo "starting web app"
	/usr/python/bin/supervisorctl start longscave
	netstat -ntpl | grep 8000
	if [ $? == 0 ];then
	echo "web app started successfully"
	fi
elif [ $? == 0 ];then
	echo "Already running"

fi

#install nginx
rpm -qa | grep nginx
if [ $? == 1 ];then
	echo "installing nginx"
	yum install -y nginx
fi

#config nginx for longscave
if [ ! -f /etc/nginx/conf.d/longscave.conf ];then
        mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
        cp /home/xiaowu/longscave/nginxconf/nginx.conf /etc/nginx/
	nginx -s reload
fi


# ssl configuration
openssl dhparam -out /home/xiaowu/longscave/cert/dhparam.pem 2048
if [ $1 == "openssl" ];then
	printf 'CN\nshanghai\nSH\nLong\nLong\nlongscave\nxiaolongwu1987@sin.com\n' | openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -keyout /home/xiaowu/longscave/cert/key.pem -out /home/xiaowu/longscave/cert/cert.pem
	cp /home/xiaowu/longscave/nginxconf/openssl.conf /etc/nginx/conf.d/
	nginx -s reload
elif [ $1 == "certbot" ];then
	yum install -y certbot python2-certbot-nginx
	chmod a+xr /home/xiaowu
	printf 'xiaolongwu1987@sina.com\nA\nN\n' | certbot certonly --webroot -w /home/xiaowu/longscave/cert -d longscave.top,www.longscave.top
	cp /home/xiaowu/longscave/nginxconf/letencrypt.conf /etc/nginx/conf.d/
	nginx -s reload
fi	

# install mysql 5.7
rpm -qa | grep mysql-community-server-5
if [ $? == 1 ];then
echo "installing mysql 5.7"
yum localinstall -y /home/xiaowu/longscave/packages/mysql80-community-release-el7-3.noarch.rpm 
yum --disablerepo=mysql80-community --enablerepo=mysql57-community install -y mysql-community-server
fi

service mysqld start
temppass=`grep 'A temporary password is generated for root@localhost' /var/log/mysqld.log |tail -1 | awk -F'localhost' '{print $2}' | awk -F ' ' '{print $2}'`
echo "temporary password generated:" $temppass
mysql --connect-expired-password  -hlocalhost -P3306 -uroot -p$temppass -e "alter user 'root'@'localhost' identified by '0okm(IJN890-'"
mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"0okm(IJN890-" -e "uninstall plugin validate_password"
mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"0okm(IJN890-" -e "alter user 'root'@'localhost' identified by 'xiaowu'"
mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"xiaowu" -e "flush privileges"
mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"xiaowu" -e "create database longscave character set utf8 collate utf8_bin"
mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"xiaowu" -e "create user 'longscave'@'localhost' identified by 'xiaowu'"
mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"xiaowu" -e "grant all privileges on longscave.* to 'longscave'@'localhost'"
mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"xiaowu" -e "flush privileges"

#open https:ip to verify the result.






