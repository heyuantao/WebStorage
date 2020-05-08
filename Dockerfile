FROM harbor.syslab.org/library/python3web:1.0
#RUN apt-get update && apt-get install -y nginx supervisor python3 python3-pip && && apt-get clean
WORKDIR /app/WebStorage
COPY ./ /app/WebStorage/
RUN bash /app/WebStorage/docker/install/install_web.sh
VOLUME ['/app/WebStorage/data/merged/','/app/WebStorage/data/tmp/','/var/log/supervisor/']
ENTRYPOINT  ["supervisord","-n"]
