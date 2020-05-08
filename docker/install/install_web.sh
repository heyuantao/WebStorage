echo "Create directorys for tmp and merged !"
mkdir -p /app/WebStorage/data/tmp
mkdir -p /app/WebStorage/data/merged

echo "Install virtualenv and requirements !"
cd /app/WebStorage && make installenv

echo "Install node yarn and node modules !"
cd /app/WebStorage && make installnodeenv

echo "Build node modules !"
cd /app/WebStorage && make buildnodemodules

echo "Clear useless node modules !"
cd /app/WebStorage && make cleannodemodules


echo "Copy Nginx and Supervisor Config Fle !"
cp /app/WebStorage/docker/nginx/default /etc/nginx/sites-enabled/default
cp /app/WebStorage/docker/supervisor/webstorage.conf /etc/supervisor/conf.d/webstorage.conf


echo "Install Finished !" 
