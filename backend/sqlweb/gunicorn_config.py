# 配置服务器的监听ip和端口
bind = '127.0.0.1:8090'
# 以守护进程方式运行
daemon = True
# worker数量
workers = 2
# 错误日志路径
errorlog = 'logs/gunicorn.error.log'
# 访问日志路径
accesslog = 'logs/gunicorn.access.log'
