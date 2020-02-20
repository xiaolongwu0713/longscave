#！/bin/bash
exec 1>>/tmp/longscave.log
exec 2>>/tmp/longscave.log
setenforce 0
# usage: longscave.sh start/stop/erase
# usage: longscave.sh deploy openssl/certbot (default is openssl)

if [[ $# == 0 ]] || [[ $# -gt 2 ]];then # $#: parameter number
echo "usage:
    To deploy: $0 deploy openssl/certbot
    To start/stop/erase: $0 start/stop/erase"
exit 1
fi

# start/stop/erase web app
# start/stop/erase web app
if [[ $# == 1 ]] && ([[ $1 != "start" ]]  || [[ $1 != "stop" ]] || [[ $1 != "erase" ]]);then
echo "usage:
    To deploy: $0 deploy openssl/certbot
    To start/stop/erase: $0 start/stop/erase"
exit 1
fi

if [[ $# == 1 ]] && [[ $1 == "start" ]];then
  echo "start supervisord"
  /usr/python/venv/longscave/bin/supervisord -c /etc/supervisor/supervisord.conf
  /usr/python/venv/longscave/bin/supervisorctl reload
  echo "start longscave web app"
  /usr/python/venv/longscave/bin/supervisorctl start longscave
    echo "verifying......"
    netstat -tnpl | grep 8000
    if [ $? == 1 ]; then
      echo "starting longscave web app"
      /usr/python/venv/longscave/bin/supervisorctl reload
      /usr/python/venv/longscave/bin/supervisorctl start longscave
      netstat -ntpl | grep 8000
        if [ $? == 0 ];then
          echo "web app started successfully"
        fi
    fi
    echo "Already running"
    echo "start nginx"
    systemctl start nginx
    echo "start mysql"
    service mysqld start
fi

if [[ $# == 1 ]] && [[ $1 == "stop" ]];then
  # stop web app
  echo "stop longscave web app"
  /usr/python/venv/longscave/bin/supervisorctl stop longscave
  # stop supervisord
  echo "stop supervisord deamon"
  ps -elf | grep supervisord | grep -v 'grep' | awk '{print $4}'
  netstat -ntpl | grep 8000
  if [ $? == 1 ];then
    echo "web app stopped successfully"
  fi
  echo "stop mysqld"
  systemctl stop mysqld
fi

if [[ $# == 1 ]] && [[ $1 == "erase" ]];then
  # delete user 'xiaowu'
  echo "keep user xiaowu"

  # keep python3
  echo "keep python3"

  # keep python virtualenv at /usr/pyhon/venv/longscave
  echo "keep python virtualenv"

  # keep folder created under /tmp
  echo "keep temp contents under /tmp"

  # use nginx default configuration
  echo "use default nginx configuration"
  rm -f /etc/nginx/nginx.conf
  mv /etc/nginx/nginx.conf.bak /etc/nginx/nginx.conf
  rm -f /etc/nginx/conf.d/*
  nginx -s reload

  # stop web app
  echo "stop longscave web app"
  /usr/python/venv/longscave/bin/supervisorctl stop longscave
  # stop supervisord
  echo "stop supervisord deamon"
  ps -elf | grep supervisord | grep -v 'grep' | awk '{print $4}'
  netstat -ntpl | grep 8000
  if [ $? == 1 ];then
    echo "web app stopped successfully"
  fi

  # erase mysql repo, but keep mysql package
  echo "uninstall mysql repo"
  rpm -aq | grep mysql | grep noarch | xargs yum erase -y
  echo "keep mysql package"

  # clean up mysql data
  echo "keep mysql data"
  #systemctl start mysqld
  #mysql --connect-expired-password  -hlocalhost -P3306 -uroot -pxiaowu -e "select count(*) from longscave.user"

  echo "stop mysqld"
  systemctl stop mysqld

fi


# deploy web app using openssl/certbot
if [[ $# == 2 ]] && [[ $1 != "deploy" ]];then
  echo "usage: longscave.sh deploy openssl/certbot"
  exit 1
elif [[ $# == 2 ]] && [[ $1 == "deploy" ]];then
myssl=$2
if [[ $myssl == "openssl" ]] || [[ $myssl == "certbot" ]];then
  echo "encryption method: $myssl"
else
  echo "encryption should be eigth openssl or certbot"
  exit 1
fi

## add user
id -u xiaowu
if [ $? == 1 ];then
useradd xiaowu
echo "xiaowu" | passwd -f xiaowu --stdin
else
echo "user exists"
fi
chmod a+xr /home/xiaowu


## python installatin
pyv="$(python --version 2>&1)"
pyversion=`echo $pyv | awk -F'.' '{print $1}' | awk -F ' ' '{print $2}'`

if [ $pyversion == 2 ];then
	echo "python version 2.7"
	echo "installing python 3.6"
	yum -y install wget  sqlite-devel zlib-devel xml *openssl*   openssl*  gcc  libffi-dev
	if [ $? == 1 ];then
	  echo "failed, exit now"
	  exit 1
	fi
	cd /tmp || exit
	if [ ! -d "/tmp/python3.6" ];then
		mkdir python3.6
	fi
	cd /tmp/python3.6 || exit
	rm -rf Python-3.6.4.tgz*
	wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tgz
		if [ $? == 1 ];then
	  echo "failed, exit now"
	  exit 1
	  fi
	tar -zxvf Python-3.6.4.tgz
	cd Python-3.6.4 || exit
	./configure --prefix=/usr/python --enable-loadable-sqlite-extensions --enable-optimizations --with-ssl
	make && make install
		if [ $? == 1 ];then
	  echo "failed, exit now"
	  exit 1
	 fi
	echo "installation done"
fi

if [ $pyversion == 2 ];then
	echo "creating soft link"
	mv /usr/bin/python /usr/bin/python.bak
	mv /usr/bin/pip /usr/bin/pip.bak
	ln -s /usr/python/bin/python3 /usr/bin/python
	ln -s /usr/python/bin/pip3 /usr/bin/pip
	sed -l 1 -i "s/python/python.bak/g" /usr/bin/yum
	sed -l 1 -i "s/python/python.bak/g" /usr/libexec/urlgrabber-ext-down
fi

if [ $pyversion == 2 ];then
	echo "Python version 3"
fi



if [ ! -f /usr/python/venv/longscave/bin/activate ];then
## python vertirtual env
	echo "creating python venv env at /usr/python/venv/longscave"
	chmod a+w -R /usr/python
	python -m venv /usr/python/venv/longscave
	source /usr/python/venv/longscave/bin/activate
else
	echo "python virtualenv exists"
fi


if [ ! -d "/home/xiaowu/longscave/app" ];then
	## get git repo
	echo "git clone longscave from GitHub"
	yum -y install git
	cd /home/xiaowu || exit
	git clone https://github.com/xiaolongwu1987/longscave.git
		if [ $? == 1 ];then
	  echo "failed, exit now"
	  exit 1
	  fi
	#mv microblog longscave
	cd longscave || exit
	source /usr/python/venv/longscave/bin/activate
	echo "pip install requirements"
	pip install -r requirements.txt  -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
		if [ $? == 1 ];then
	  echo "failed, exit now"
	  exit 1
	  fi
	echo "pip install pymysql gunicorn"
	pip install pymysql gunicorn
		if [ $? == 1 ];then
	  echo "failed, exit now"
	  exit 1
	  fi
	chown xiaowu:xiaowu -R /home/xiaowu/longscave
else
	echo "git repository longscave exists"
fi


# install guess_language package
source /usr/python/venv/longscave/bin/activate
pip freeze | grep guess-language
if [ $? == 1 ];then
echo "install guess_language"
yum install -y bzip2
		if [ $? == 1 ];then
	  echo "failed, exit now"
	  exit 1
	  fi
mkdir /tmp/guess_languagetmp/
cd /tmp/guess_languagetmp || exit
wget https://files.pythonhosted.org/packages/8b/4f/9ed0280b24e9e6875c3870a97659d0106a14e36db0d7d65c5277066fc7d0/guess_language-spirit-0.5.3.tar.bz2
		if [ $? == 1 ];then
	  echo "failed, exit now"
	  exit 1
	  fi
tar -jxvf guess_language-spirit-0.5.3.tar.bz2
source /usr/python/venv/longscave/bin/activate
cd /tmp/guess_languagetmp/guess_language-spirit-0.5.3 || exit
python setup.py install
else
echo "guess_language package exists"
fi


# configure supervisor
if [ ! -d "/etc/supervisor/conf.d" ];then
mkdir /etc/supervisor
mkdir /etc/supervisor/conf.d
fi
if [ ! -d "/tmp/supervisortmp" ];then
echo "install supervisor from source"
cd /tmp || exit
mkdir supervisortmp
cd /tmp/supervisortmp || exit
git clone https://github.com/Supervisor/supervisor.git
		if [ $? == 1 ];then
	  echo "failed, exit now"
	  exit 1
	  fi
fi
if [ ! -f "/usr/python/venv/longscave/bin/supervisord" ];then
cd /tmp/supervisortmp/supervisor || exit
python setup.py install
fi
if [ ! -f "/etc/supervisor/conf.d/longscave.ini" ];then
/usr/python/venv/longscave/bin/echo_supervisord_conf > /etc/supervisor/supervisord.conf
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
fi
echo "start supervisord"
/usr/python/venv/longscave/bin/supervisord -c /etc/supervisor/supervisord.conf


yum -y install net-tools
netstat -tnpl | grep 8000
if [ $? == 1 ]; then
	echo "starting longscave web app"
	/usr/python/venv/longscave/bin/supervisorctl reload
	/usr/python/venv/longscave/bin/supervisorctl start longscave
	netstat -ntpl | grep 8000
	if [ $? == 0 ];then
	echo "web app started successfully"
	fi
elif [ $? == 0 ];then
	echo "Already running"

fi

#install nginx
rpm -qa | grep nginx | grep -v noarch
if [ $? == 1 ];then
	echo "installing nginx"
	yum localinstall -y  /home/xiaowu/longscave/packages/nginx-release-centos-7-0.el7.ngx.noarch.rpm
	yum install -y nginx
		if [ $? == 1 ];then
	  echo "failed, exit now"
	  exit 1
	  fi
	mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.bak
  mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
  cp /home/xiaowu/longscave/nginxconf/nginx.conf /etc/nginx/
	systemctl start nginx
fi


# ssl configuration
#openssl dhparam -out /home/xiaowu/longscave/cert/dhparam.pem 2048
mkdir /tmp/cert
rm -f /tmp/cert/*
if [ $myssl == "openssl" ];then
	printf 'CN\nshanghai\nSH\nLong\nLong\nlongscave\nxiaolongwu1987@sin.com\n' | openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -keyout /tmp/cert/key.pem -out /tmp/cert/cert.pem
	cp /home/xiaowu/longscave/nginxconf/openssl.conf /etc/nginx/conf.d/
	nginx -s reload
elif [ $myssl == "certbot" ];then
	yum install -y certbot python2-certbot-nginx
		if [ $? == 1 ];then
	  echo "failed, exit now"
	  exit 1
	  fi
	chmod a+xr /home/xiaowu
	printf 'xiaolongwu1987@sina.com\nA\nN\n' | certbot certonly --webroot -w /tmp/cert -d longscave.top,www.longscave.top
	cp /home/xiaowu/longscave/nginxconf/letencrypt.conf /etc/nginx/conf.d/
	nginx -s reload
fi	

# install mysql 5.7
rpm -qa | grep mysql-community-server-5
if [ $? == 1 ];then
echo "installing mysql 5.7"
yum localinstall -y /home/xiaowu/longscave/packages/mysql80-community-release-el7-3.noarch.rpm 
yum clean all
yum makecache
yum --disablerepo=mysql80-community --enablerepo=mysql57-community install -y mysql-community-server
		if [ $? == 1 ];then
	  echo "failed, exit now"
	  exit 1
	  fi
fi

service mysqld start
mysql --connect-expired-password  -hlocalhost -P3306 -uroot -pxiaowu -e "select count(*) from longscave.user"
if [ $? == 1 ];then
  echo "initiate mysql database"
  temppass=`grep 'A temporary password is generated for root@localhost' /var/log/mysqld.log |tail -1 | awk -F'localhost' '{print $2}' | awk -F ' ' '{print $2}'`
  echo "temporary password generated:" $temppass
  mysql --connect-expired-password  -hlocalhost -P3306 -uroot -p$temppass -e "alter user 'root'@'localhost' identified by '0okm(IJN890-'"
  	if [ $? == 1 ];then
	  echo "failed, exit now"
	  exit 1
	  fi
  mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"0okm(IJN890-" -e "uninstall plugin validate_password"
  mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"0okm(IJN890-" -e "alter user 'root'@'localhost' identified by 'xiaowu'"
  mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"xiaowu" -e "flush privileges"
  mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"xiaowu" -e "create database longscave character set utf8 collate utf8_bin"
  mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"xiaowu" -e "create user 'longscave'@'localhost' identified by 'xiaowu'"
  mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"xiaowu" -e "grant all privileges on longscave.* to 'longscave'@'localhost'"
  mysql --connect-expired-password -hlocalhost -P3306 -uroot -p"xiaowu" -e "flush privileges"
  # database migration
  echo "flask db upgrade"
  cd /home/xiaowu/longscave || exit
  source /usr/python/venv/longscave/bin/activate
  flask db upgrade
fi
#open https:ip to verify the result.

fi