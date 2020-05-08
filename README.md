该项目实现了一个大文件上传的微服务（前端依赖webuploader),软件分为两个部分，一个用于文件的上传和管理，另一个模块用于文件的下载
该软件可以利用给第三方网站提供微服务，并支持大文件的分片直传，类似于云存储的大文件直传方案。

一、以容器方式运行
1.1 构建容器
```
docker build -t webstorage:3.0 .
```
1.2 运行容器
先运行redis：
```
sudo mkdir -p /app/
sudo chown -R ${USER}:${USER} /app/
git clone https://github.com/heyuantao/WebStorage.git /app/WebStorage/
docker run -d --name redis --restart=always --network=host -v /app/WebStorage/docker/redis/redis.conf:/etc/redis/redis.conf redis:5.0 redis-server /etc/redis/redis.conf
```
然后运行应用
```
mkdir -p /app/data/files/merged /app/data/files/tmp /app/data/logs  #merged存放合并后的文件,tmp存放未合并的文件,logs放置supervisor的日志
mkdir -p /app/data/files/tmp       #存放未合并的文件
mkdir -p /app/data/logs            #存放日志，放置supervisor的日志
docker run -d --name webstorage --restart=always --net=host -e TOKEN=UseMyWebStorage -v /app/data/files/merged:/app/WebStorage/data/merged/ -v /app/data/files/tmp:/app/WebStorage/data/tmp/ -v /app/data/logs:/var/log/supervisor/ webstorage:3.0 
```
其中"TOKEN"为其他服务连接使用的密钥,切记不要泄露。

二、源代码方式安装和调试
2.1 文件上传和管理模块

启用用于上传和管理接口的微服务
gunicorn -w 6 -b 0.0.0.0:5000 --log-level=ERROR --timeout 30 -k gevent App_Manager:application

启动工作列队
celery -A task.task worker --loglevel=ERROR

启动周期任务提醒
celery -A task.task beat

2.2 文件下载模块
启用文件下载模块
gunicorn -w 6 -b 0.0.0.0:5001 --log-level=ERROR --timeout 30 -k gevent App_FileServer:application
注：文件下载模块面临长时间下载的场景，因此HTTP使用了长连接"keepalive"，因此如果前端使用反向代理的话确保反向代理也配置过长连接


2.3、使用nginx进行流量转发

对于匹配 /api/  的流量转发到文件管理模块
对于匹配 /file/ 的流量转发到文件下载模块，该模块配置长连接

类似如下
````
server {
        listen 80;
        server_name webstorage.x.y;
	    client_max_body_size 15m; 
    	location /static/ {
            alias /app/WebStorage/templates/mystorageapp/build/static/;
    	}
        location /static/
        {
                proxy_pass http://x.x.x.x:5000;
                charset utf-8;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-for $remote_addr;
                proxy_set_header X-Real-IP $remote_addr;
        }
        location /api/ {
                proxy_http_version 1.1;
                proxy_set_header Connection "";
                proxy_pass http://x.x.x.x:5000;
                charset utf-8;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-for $remote_addr;
                proxy_set_header X-Real-IP $remote_addr;
        }
        location /file/ {
                proxy_http_version 1.1;
                proxy_set_header Connection "";
                proxy_pass http://x.x.x.x:5001;
                charset utf-8;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-for $remote_addr;
                proxy_set_header X-Real-IP $remote_addr;
        }

}
````


其他：
1.查阅资料的配置，但未发现生效 
```
WSGIRequestHandler.protocol_version = "HTTP/1.1"
```
2.调试模式请设置
```
--log-level=DEBUG
```
