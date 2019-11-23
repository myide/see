## See项目搭建


### 操作系统支持
     CentOS 6+
     CentOS 7+

### 部署清单
     1. Mysql
     2. pt-online-schema-change
     3. Inception
     4. Sqladvisor
     5. Redis
     6. Nginx
     7. See项目

### 1 Mysql
##### 1.1 安装过程略
##### 1.2 mysql配置文件内容需包含以下配置
```ini
[mysqld]
server-id = 100  # 不限制具体数值
log_bin = mysql-bin
binlog_format = row  # 或 MIXED
```

### 2 pt-online-schema-change
##### 在线修改表结构的工具
```bash
yum install -y perl-DBI perl-DBD-mysql perl-Time-HiRes perl-ExtUtils-MakeMaker
wget https://www.percona.com/get/percona-toolkit.tar.gz
tar -zxvf percona-toolkit.tar.gz
cd percona-toolkit-3.0.13
perl Makefile.PL
make
make install
ln -s /usr/local/bin/pt-online-schema-change /usr/bin/

```

### 3 Inception
##### 3.1 安装
```bash
yum -y install cmake libncurses5-dev libssl-dev g++ bison gcc gcc-c++ openssl-devel ncurses-devel mysql MySQL-python
wget http://ftp.gnu.org/gnu/bison/bison-2.5.1.tar.gz
tar -zxvf bison-2.5.1.tar.gz
cd bison-2.5.1
./configure
make
make install

cd /usr/local/
wget https://github.com/myide/inception/archive/master.zip
unzip master.zip
cd inception-master/
sh inception_build.sh builddir linux

```

##### 3.2 修改配置
创建文件 /etc/inc.cnf ,内容如下 
```ini
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

##### 3.3 启动服务
```bash
nohup /usr/local/inception-master/builddir/mysql/bin/Inception --defaults-file=/etc/inc.cnf &
```

### 4 Sqladvisor

##### 4.1 克隆代码
```bash
cd /usr/local/src/
git clone https://github.com/Meituan-Dianping/SQLAdvisor.git
```

##### 4.2 安装依赖
```bash
yum install -y cmake libaio-devel libffi-devel glib2 glib2-devel bison
# 移除mysql-community库(无用途且和Percona-Server有冲突)
yum remove -y mysql-community-client mysql-community-server mysql-community-common mysql-community-libs
cd /usr/lib64/ 
ln -s libperconaserverclient_r.so.18 libperconaserverclient_r.so 
wget http://www.percona.com/downloads/percona-release/redhat/0.1-3/percona-release-0.1-3.noarch.rpm -O /tmp/percona-release-0.1-3.noarch.rpm
rpm -ivh /tmp/percona-release-0.1-3.noarch.rpm
yum install -y Percona-Server-shared-56
cd /usr/local/src/SQLAdvisor/
cmake -DBUILD_CONFIG=mysql_release -DCMAKE_BUILD_TYPE=debug -DCMAKE_INSTALL_PREFIX=/usr/local/sqlparser ./
make && make install

```

##### 4.3 编译sqladvisor(源码目录)
```bash
cd ./sqladvisor/
cmake -DCMAKE_BUILD_TYPE=debug ./
make
```

##### 4.4 完成测试
```bash
cp /usr/local/src/SQLAdvisor/sqladvisor/sqladvisor /usr/bin/sqladvisor
sqladvisor -h 127.0.0.1  -P 3306  -u root -p '123456' -d test -q "sql语句" -v 1
```

##### 4.5 官方文档学习
```bash
https://github.com/Meituan-Dianping/SQLAdvisor/blob/master/doc/QUICK_START.md
```

### 5 Redis

##### 5.1 安装
```bash
yum install -y redis
```
##### 5.2 配置 /etc/redis.conf
```ini
daemonize yes
```

### 6 Nginx
##### 6.1 安装过程略

##### 6.2 配置
修改Nginx配置文件 nginx.conf, 使server部分的内容如下
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

### 7 See

##### 7.1 安装依赖

```bash
yum install -y readline readline-devel gcc gcc-c++ zlib zlib-devel openssl openssl-devel sqlite-devel python-devel openldap-clients openldap-devel openssl-devel
```

##### 7.2 下载并安装python3.6

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

##### 7.3 安装Django及See后端
步骤
```bash
cd /usr/local/
/usr/local/python3.6/bin/pyvenv seevenv
cd seevenv
source bin/activate
wget https://github.com/myide/see/archive/master.zip
unzip master.zip
cd see-master/backend/
pip install -r requirements.txt --trusted-host mirrors.aliyun.com -i https://mirrors.aliyun.com/pypi/simple/

```

##### 7.4 创建数据库
确保mysql的root密码为 123456 (如需修改，可参考步骤10.1)

```bash
mysql -uroot -p123456 -e "create database sqlweb CHARACTER SET utf8;"
python manage.py makemigrations
python manage.py migrate
# 再执行一次migrate
python manage.py migrate

```

##### 7.5 执行命令创建inception库
###### 7.5.1 创建测试库，测试表
```
mysql -uroot -p123456  # 登录数据库
mysql> CREATE DATABASE pro1;
mysql> CREATE TABLE IF NOT EXISTS pro1.mytable1 (
   `id` INT UNSIGNED AUTO_INCREMENT,
   `myname` VARCHAR(10) NOT NULL,
   PRIMARY KEY ( `id` )
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
```
###### 7.5.2 执行测试脚本
```
python /usr/local/seevenv/see-master/backend/utils/inception_test.py
# 有类似如下返回即可
((1, 'RERUN', 0, 'Execute Successfully', 'None', 'use pro1', 0, "'1537264031_2_0'", 'None', '0.000', ''), (2, 'EXECUTED', 0, 'Execute Successfully\nBackup successfully', 'None', 'insert into mytable1 (myname) values ("xianyu1"),("xianyu2")', 2, "'1537264031_2_1'", '127_0_0_1_3306_pro1', '0.000', ''), (3, 'EXECUTED', 0, 'Execute Successfully\nBackup successfully', 'None', 'insert into mytable1 (myname) values ("xianyu1"),("xianyu2")', 2, "'1537264031_2_2'", '127_0_0_1_3306_pro1', '0.000', ''))
```

##### 7.6 前端打包 (非必需操作)
Nginx配置里包含了已打包的前端文件，如需自己生成前端文件，可执行以下步骤
```bash
cnpm install
cnpm install --save vue-markdown
cnpm install --save-dev vue2-ace-editor
cnpm install emmet@git+https://github.com/cloud9ide/emmet-core.git#41973fcc70392864c7a469cf5dcd875b88b93d4a
npm run build  # 打包, 目录 /usr/local/seevenv/see-master/frontend/dist 即是打包后产生的前端文件，用于nginx部署
```

##### 7.7 创建管理员用户 (可用于页面的用户登录)
```bash
python manage.py createsuperuser --username admin --email admin@domain.com
```

### 8 解决python3下pymysql对inception支持的问题
##### 8.1 解决报错 ValueError: invalid literal for int() with base 10: 'Inception2'
```
# 查找pymysql源码修改connections.py文件，/usr/local/seevenv/lib/python3.6/site-packages/pymysql/connections.py

    # 找到此处
    def _request_authentication(self):
        # https://dev.mysql.com/doc/internals/en/connection-phase-packets.html#packet-Protocol::HandshakeResponse
        if int(self.server_version.split('.', 1)[0]) >= 5:
            self.client_flag |= CLIENT.MULTI_RESULTS

    # 修改为
    def _request_authentication(self):
        # https://dev.mysql.com/doc/internals/en/connection-phase-packets.html#packet-Protocol::HandshakeResponse
        if self.server_version.split('.', 1)[0] == 'Inception2':
            self.client_flag |= CLIENT.MULTI_RESULTS
        elif int(self.server_version.split('.', 1)[0]) >= 5:
            self.client_flag |= CLIENT.MULTI_RESULTS

```
##### 8.2 解决 Inception始终反馈”Must start as begin statement”的语法错误
```
# 查找pymysql源码修改cursors.py文件，/usr/local/seevenv/lib/python3.6/site-packages/pymysql/cursors.py

    # 找到此处
    if not self._defer_warnings:
        self._show_warnings()    

    # 修改为
    if not self._defer_warnings:
        pass  
```

### 9 安装SOAR
```bash
mkdir -p /usr/local/SOAR/bin/
cp /usr/local/seevenv/see-master/frontend/src/files/soar /usr/local/SOAR/bin
chmod +x /usr/local/SOAR/bin/soar

```

### 10 设置（非必需操作）
打开文件 /usr/local/seevenv/see-master/backend/sqlweb/settings.py,找到以下设置并修改

#### 10.1 MySQL
```bash
DATABASES = {
	'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sqlweb',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST':'127.0.0.1',
        'PORT':'3306',
        'OPTIONS': {'charset':'utf8mb4'},
	},
}
```

#### 10.2 Redis
```bash
REDIS_HOST = '127.0.0.1'  # redis地址
REDIS_PORT = 6379  # redis端口
REDIS_PASSWORD = ''  # redis密码
```

#### 10.3 Inception配置文件
```bash
INCEPTION_SETTINGS = {
    'file_path': '/etc/inc.cnf'
}
```

#### 10.4 SQLAdvisor和SOAR的路径
```bash
OPTIMIZE_SETTINGS = {
    'sqladvisor_cli': '/usr/bin/sqladvisor',
    'soar_cli': '/usr/local/SOAR/bin/soar'
}
```

#### 10.5 邮件
```bash
MAIL = {
    'smtp_host': 'smtp.163.com',  # 邮件服务器
    'smtp_port': 25,  # SMTP协议默认端口是25
    'mail_user': 'sql_see@163.com',  # 邮件用户名
    'mail_pass': 'see123',  # 授权码
    'see_addr': 'http://xxx.xxx.xxx.xxx:81',  # see项目访问地址
}

```

### 11 对接统一认证系统（非必需操作）
```bash
需要自定义访问统一认证接口的方法, 详见文件 /usr/local/seevenv/see-master/backend/utils/unitaryauth.py,
修改authenticate的内容为自定义的方法即可。
注意：
1. 该方法的参数一般为 username, password
2. 根据请求接口的结果(成功/失败)，定义authenticate的返回值(True/False)即可
```

### 12 启动所有服务
```bash
# mysql  3306端口
/etc/init.d/mysqld start

# inception  6669端口
nohup /usr/local/inception-master/builddir/mysql/bin/Inception --defaults-file=/etc/inc.cnf &

# redis  6379端口
redis-server /etc/redis.conf

# nginx  81端口
/usr/local/nginx/sbin/nginx

# see  8090端口
source /usr/local/seevenv/bin/activate
cd /usr/local/seevenv/see-master/backend
nohup python manage.py celery worker -c 10 -B --loglevel=info &
gunicorn -c sqlweb/gunicorn_config.py sqlweb.wsgi
```

启动都OK！可以使用啦： 

http://xxx.xxx.xxx.xxx:81/    # see 项目

http://xxx.xxx.xxx.xxx:81/api/docs/  # see api 文档

##### 推荐用Chrome浏览器访问

