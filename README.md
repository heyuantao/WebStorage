一、该项目实现了一个大文件上传的微服务（前端依赖webuploader),软件分为两个部分，一个用于文件的上传和管理，另一个模块用于文件的下载


1.1 文件上传和管理模块

启用用于上传和管理接口的微服务
gunicorn -w 6 -b 0.0.0.0:5000 --log-level=info --timeout 30 App_Manager:application

启动工作列队
celery -A task.task worker

启动周期任务提醒
celery -A task.task beat

1.2 文件下载模块
启用文件下载模块
gunicorn -w 6 -b 0.0.0.0:5001 --log-level=info --timeout 30 -k gevent App_FileServer:application
注：文件下载模块面临长时间下载的场景，因此HTTP使用了长连接"keepalive"，因此如果前端使用反向代理的话确保反向代理也配置过长连接


二、使用nginx进行流量转发

对于匹配 /api/  的流量转发到文件管理模块
对于匹配 /file/ 的流量转发到文件下载模块，该模块配置长连接

类似如下
````
server {
        listen 80;
        server_name webstorage.x.y;

        location /static/
        {
                proxy_pass http://x.x.x.x:5000;
                charset utf-8;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-for $remote_addr;
                proxy_set_header X-Real-IP $remote_addr;
        }
        location /api/
        {
                proxy_pass http://x.x.x.x:5000;
                charset utf-8;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-for $remote_addr;
                proxy_set_header X-Real-IP $remote_addr;
        }
        location /file/
        {
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


其他：查阅资料的配置，但未发现生效
WSGIRequestHandler.protocol_version = "HTTP/1.1"
