## See项目搭建

### 安装清单
##### 1. Mysql
##### 2. Inception
##### 3. Sqladvisor
##### 4. Redis
##### 5. Nginx
##### 6. See项目


#### 1 Mysql
##### 1.1 安装过程略
##### 1.2 mysql配置文件内容需包含以下配置
```ini
[mysqld]
server-id       = 100  # 不限制
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
wget https://github.com/mysql-inception/inception/archive/master.zip unzip master.zip
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
    listen 81;#监听端口
    access_log    /var/log/access.log;
    error_log    /var/log/error.log;

    location / { 
        root /usr/local/seevenv/see/frontend/dist/; 
        try_files $uri $uri/ /index.html =404; 
        index  index.html; 
    } 

    location /api {
        # rewrite  ^/api/(.*)$ /$1 break;
        proxy_pass http://127.0.0.1:8090;
        add_header Access-Control-Allow-Origin *; 
        add_header Access-Control-Allow-Headers Content-Type;
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept";
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS, PUT, DELETE, PATCH";
    }

  }


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

创建虚拟环境，在该环境下安装Django

```bash
cd /usr/local/
/usr/local/python3.6/bin/pyvenv seevenv
cd seevenv
source bin/activate
git clone git@github.com:chenkun1998/see.git
cd see/backend
pip install -r requirements.txt --trusted-host mirrors.aliyun.com -i https://mirrors.aliyun.com/pypi/simple/

```

##### 6.4 创建autoAdmin数据库
确保mysql的root密码为 123456

```bash
mysql -uroot -p123456 -e "create database sqlweb CHARACTER SET utf8;"
python manage.py makemigrations
python manage.py migrate

```

##### 6.5 创建管理员用户
```bash
python manage.py createsuperuser --username admin --email admin@domain.com
```

### 7 启动所有服务
```bash

/etc/init.d/mysqld start
nohup /usr/local/inception-master/builddir/mysql/bin/Inception --defaults-file=/etc/inc.cnf &
redis-server /etc/redis.conf
/usr/local/nginx/sbin/nginx
cd /usr/local/seevenv/see/backend
python manage.py celery worker -c 4 --loglevel=info
nohup python manage.py runserver 0:8090 &

```

启动都OK！可以使用啦： 

http://xxx.xxx.xxx.xxx:81/    # see 项目

http://xxx.xxx.xxx.xxx:81/api/docs/  # see api 文档


