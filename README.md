该项目实现了一个大文件上传的微服务

gunicorn -w 6 -b 0.0.0.0:34567 --log-level=debug --timeout 180 app:application
gunicorn -w 6 -b 0.0.0.0:34567 --log-level=debug --timeout 180 -k gevent app:application

测试下在运行前设置
WSGIRequestHandler.protocol_version = "HTTP/1.1"
