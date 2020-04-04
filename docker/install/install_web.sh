echo "Remove the node_modules !"
rm -Rf /app/WebStorage/templates/mystorageapp/node_modules/

echo "Install Apt Package !"
apt-get install -y nginx supervisor
apt-get install -y python3 python3-pip #python3-dev libmysqlclient-dev
#apt-get install -y libssl-dev

echo "Install Python Package !"
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo "Copy Nginx and Supervisor Config Fle !"
cp /app/WebStorage/docker/nginx/default /etc/nginx/sites-enabled/default
cp /app/WebStorage/docker/supervisor/webstorage.conf /etc/supervisor/conf.d/webstorage.conf

echo "Install Finished !" 
