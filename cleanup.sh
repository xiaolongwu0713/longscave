#/bin/bash
exec 1>>/tmp/cleanup.log
exec 2>>/tmp/cleanup.log
setenforce 0

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
