## See项目搭建

### 安装清单
     1. Mysql
     2. Inception
     3. Sqladvisor
     4. Redis
     5. Nginx
     6. See项目


#### 1 Mysql
##### 1.1 安装过程略
##### 1.2 mysql配置文件内容需包含以下配置
```ini
[mysqld]
server-id       = 100  # 不限制具体数值
log_bin = mysql-bin
binlog_format = row
```

#### 2 Inception
##### 2.1 安装
```bash
yum -y install cmake libncurses5-dev libssl-dev g++ bison gcc gcc-c++ openssl-devel ncurses-devel mysql MySQL-python
wget http://ftp.gnu.org/gnu/bison/bison-2.5.1.tar.gz tar -zxvf bison-2.5.1.tar.gz
cd bison-2.5.1
./configure
make
make install

cd /usr/local/
wget https://github.com/mysql-inception/inception/archive/master.zip 
unzip master.zip
cd inception-master/
sh inception_build.sh builddir linux

```

##### 2.2 修改配置

```ini

vi /etc/inc.cnf ###################
[inception]
general_log=1
general_log_file=inc.log
port=6669
socket=/tmp/inc.socket 
character-set-client-handshake=0 
character-set-server=utf8 
inception_remote_system_password=123456 
inception_remote_system_user=root 
inception_remote_backup_port=3306 
inception_remote_backup_host=127.0.0.1 
inception_support_charset=utf8 
inception_enable_nullable=0 
inception_check_primary_key=1 
inception_check_column_comment=1 
inception_check_table_comment=1 
inception_osc_min_table_size=1 
inception_osc_bin_dir=/usr/bin 
inception_osc_chunk_time=0.1 
inception_ddl_support=1
inception_enable_blob_type=1 
inception_check_column_default_value=1 
```

##### 2.3 启动服务
```bash
nohup /usr/local/inception-master/builddir/mysql/bin/Inception --defaults-file=/etc/inc.cnf &
```

##### 2.4 官方文档学习
```bash
http://mysql-inception.github.io/inception-document/
```

#### 3 Sqladvisor

##### 3.1 克隆代码
```bash
cd /usr/local/src/
git clone https://github.com/Meituan-Dianping/SQLAdvisor.git
```

##### 3.2 安装依赖
```bash
yum install -y cmake libaio-devel libffi-devel glib2 glib2-devel bison
cd /usr/lib64/ 
ln -s libperconaserverclient_r.so.18 libperconaserverclient_r.so 
yum install http://www.percona.com/downloads/percona-release/redhat/0.1-3/percona-release-0.1-3.noarch.rpm
yum install Percona-Server-shared-56
cd /usr/local/src/SQLAdvisor/
cmake -DBUILD_CONFIG=mysql_release -DCMAKE_BUILD_TYPE=debug -DCMAKE_INSTALL_PREFIX=/usr/local/sqlparser ./
make && make install

```

##### 3.3 编译sqladvisor(源码目录)
```bash
cd ./sqladvisor/
cmake -DCMAKE_BUILD_TYPE=debug ./
make
```

##### 3.4 完成测试
```bash
cp /usr/local/src/SQLAdvisor/sqladvisor/sqladvisor /usr/bin/sqladvisor
sqladvisor -h 127.0.0.1  -P 3306  -u root -p '123456' -d test -q "sql语句" -v 1
```

##### 3.5 官方文档学习
```bash
https://github.com/Meituan-Dianping/SQLAdvisor/blob/master/doc/QUICK_START.md
```

#### 4 Redis

##### 4.1 安装
```bash
yum install -y redis
```
##### 4.2 配置 /etc/redis.conf
```ini
daemonize yes
```

#### 5 Nginx
##### 5.1 安装过程略

##### 5.2 配置, 使server部分的配置如下
```
 server
  {
    listen 81;  # 用户访问端口
    access_log    /var/log/access.log;
    error_log    /var/log/error.log;

    location / { 
        root /usr/local/seevenv/see-master/frontend/dist/;  # 前端项目文件
        try_files $uri $uri/ /index.html =404; 
        index  index.html; 
    } 

    location /static/rest_framework_swagger {  #  前端API静态文件
        root /usr/local/seevenv/lib/python3.6/site-packages/rest_framework_swagger/; 
    } 

    location /static/rest_framework {  #  前端rest_framework静态文件
        root /usr/local/seevenv/lib/python3.6/site-packages/rest_framework/;
    } 

    location /api {
        proxy_pass http://127.0.0.1:8090;  # 后端端口
        add_header Access-Control-Allow-Origin *; 
        add_header Access-Control-Allow-Headers Content-Type;
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept";
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS, PUT, DELETE, PATCH";
    }

  }

```
##### 5.3 前端打包
上一步的Nginx配置里包含了已打包的前端文件，如需自己生成前端文件，可执行以下步骤
```bash
cnpm install
cnpm install --save-dev vue2-ace-editor
cnpm install emmet@git+https://github.com/cloud9ide/emmet-core.git#41973fcc70392864c7a469cf5dcd875b88b93d4a
npm run dev  # 启动
npm run build  # 打包
```

#### 6 See

##### 6.1 安装依赖

```bash
yum install -y readline readline-devel gcc gcc-c++ zlib zlib-devel openssl openssl-devel sqlite-devel python-devel
```

##### 6.2 下载并安装python3.6

```bash
wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tgz
tar -xzf Python-3.6.6.tgz 
cd Python-3.6.6
./configure --prefix=/usr/local/python3.6 --enable-shared
make && make install
ln -s /usr/local/python3.6/bin/python3.6 /usr/bin/python3
ln -s /usr/local/python3.6/bin/pip3 /usr/bin/pip3
ln -s /usr/local/python3.6/bin/pyvenv /usr/bin/pyvenv

# 链接库文件
cp /usr/local/python3.6/lib/libpython3.6m.so.1.0 /usr/local/lib
cd /usr/local/lib
ln -s libpython3.6m.so.1.0 libpython3.6m.so
echo '/usr/local/lib' >> /etc/ld.so.conf
/sbin/ldconfig

```

##### 6.3 安装Django及See后端
步骤
```bash
cd /usr/local/
/usr/local/python3.6/bin/pyvenv seevenv
cd seevenv
source bin/activate
wget https://github.com/chenkun1998/see/archive/master.zip
unzip master.zip
cd see-master/backend/
pip install -r requirements.txt --trusted-host mirrors.aliyun.com -i https://mirrors.aliyun.com/pypi/simple/

```

##### 6.4 配置gunicorn
在see项目的setting.py文件的同级目录里，增加一个配置文件 /usr/local/seevenv/see-master/backend/sqlweb/gunicorn_config.py, 内容如下：
```ini
bind = "127.0.0.1:8090"
daemon = True
workers = 2
errorlog = '/tmp/gunicorn.error.log'
accesslog = '/tmp/gunicorn.access.log'
```

##### 6.5 创建autoAdmin数据库
确保mysql的root密码为 123456

```bash
mysql -uroot -p123456 -e "create database sqlweb CHARACTER SET utf8;"
python manage.py makemigrations
python manage.py migrate

```

##### 6.6 创建管理员用户
```bash
python manage.py createsuperuser --username admin --email admin@domain.com
```

### 7 启动所有服务
```bash

/etc/init.d/mysqld start
nohup /usr/local/inception-master/builddir/mysql/bin/Inception --defaults-file=/etc/inc.cnf &
redis-server /etc/redis.conf
/usr/local/nginx/sbin/nginx
cd /usr/local/seevenv/see-master/backend
nohup python manage.py celery worker -c 4 --loglevel=info &
gunicorn -c sqlweb/gunicorn_config.py sqlweb.wsgi
```

启动都OK！可以使用啦： 

http://xxx.xxx.xxx.xxx:81/    # see 项目

http://xxx.xxx.xxx.xxx:81/api/docs/  # see api 文档


