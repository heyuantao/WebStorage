FROM ubuntu:18.04

###This part is use to set time zone ########
ENV TZ=Asia/Shanghai
RUN sed -i s/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g /etc/apt/sources.list
RUN echo $TZ > /etc/timezone && apt-get update && apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean
ENV LANG C.UTF-8
ENV LC_CTYPE en_US.UTF-8
### set timezone end #######################

RUN apt-get update && apt-get install -y locales &&  locale-gen zh_CN.UTF-8
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list  && echo "Asia/Shanghai" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

ENV LANG zh_CN.UTF-8
ENV LANGUAGE zh_CN.UTF-8
ENV LC_ALL zh_CN.UTF-8

WORKDIR /app/WebStorage

COPY ./ /app/WebStorage/

RUN bash /app/WebStorage/docker/install/install_web.sh

#VOLUME ['/app/EEAS/media/avatar/','/var/log/supervisor/']
VOLUME ['/app/WebStorage/data/merged/','/app/WebStorage/data/tmp/','/var/log/supervisor/']

ENTRYPOINT  ["supervisord","-n"]