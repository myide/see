
# See SQL审核平台

![](https://img.shields.io/badge/build-release-brightgreen.svg)  
![](https://img.shields.io/badge/version-v1.0.0-brightgreen.svg)  
![](https://img.shields.io/badge/vue.js-2.9.1-brightgreen.svg) 
![](https://img.shields.io/badge/iview-2.8.0-brightgreen.svg?style=flat-square) 
![](https://img.shields.io/badge/python-3.6-brightgreen.svg)
![](https://img.shields.io/badge/Django-2.0-brightgreen.svg)

## API集成
- **Inception**: 去哪儿网开源，提供SQL语句审核、执行、回滚功能
- **SQLAdvisor**: 美团开源，提供分析SQL中的where条件、聚合条件、多表Join关系，输出索引优化建议
- **SOAR**: 小米开源，提供SQL启发式算法的语句优化、多列索引优化等功能

## 功能简介

- 目标库管理
    - 支持多场地/数据中心的数据库管理，集群方式归纳目标数据库
    - 支持目标数据库配置，库/表结构查询
- SQL操作
    - 基于Inception
    - SQL语法检测
    - SQL语句执行
    - SQL回滚
    - 定时工单
    - 历史记录
- SQL查询
    - 查询目标数据库的详细表结构
    - 查询表数据，对结果可导出文件
    - SQL语句优化（基于美团SQLAdvisor）
    - 多层次优化建议（基于小米SOAR）
- 用户管理
    - 对用户/组的注册/注销/加组/授权等管理
- 个性化设置
    - 管理员可以做SQL关键字拦截，平台的审批功能开关等设置
    - 用户可以订阅其常用的数据库，指定审批工单的经理，以简化审核时所需的操作
- inception设置
    - inception服务连接信息
    - inception备份库连接信息
    - inception支持的参数释义及值
- 人工审批功能
    - 流程开关
    - 开启流程，工单至少需双人确认（流程：提交人 -- inception自动审核 -- 经理审批 -- DBA上线）
    - 关闭流程，工单可由经理上线（流程：提交人 -- inception自动审核 -- 经理上线）
- 用户权限
    - 基于RBAC的表级，对象级权限控制体系
    - 通过用户管理设置用户权限
    - 根据用户身份（组员/经理/总监）鉴权用户对SQL的审核/取消/执行/回滚等操作
- 操作流程
    - 用户需要输入SQL，指定环境，执行人，数据库
    - inception自动审核SQL语法
    - 审批人做审批通过或驳回操作
    - 执行人做执行/撤销/回滚等操作
    - SQL列表界面提供SQL查询，操作等相关功能

- API文档
    - 各接口生成自动化的API文档，对接外部需求
    
- 登录
    - 支持see系统登录
    - 支持自定义公司统一认证中心(sso)登录

- 通知
    - E-mail邮件推送

- 其他
    - DashBoard数据报表展示

## 环境

- Python 3.6
    - Django 2.0
    - Django Rest Framework 3.8
    
- Vue.js 2.9
    - iview 2.8
    - iview-admin 1.3

## 平台使用
- [在线访问](http://oldcat.online:52080/) (下表为登录的用户/密码)
  
| 用户名 | 密码 |
| --- | --- |
| 武松 | see |
| 宋江 | see |

## 安装文档
- [安装文档](https://github.com/myide/see/blob/master/frontend/src/files/install.md)

## 界面展示

- 邮件提醒

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/mail.png)

- SQL查询

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/query.png)

- 工单审核

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/check.png)

- 工单详情 1

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/detail1.png)

- 工单详情 2

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/detail2.png)

- 工单详情 3

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/detail3.png)

- 工单列表

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/list.png)

- 平台设置

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/plantformsettings.png)

- 用户管理

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/user.png)

- Dashboard审计

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/dashboard.png)

## 交流学习
- QQ群 630791951

## License

- Eclipse Public License - v 2.0

Copyright © 2018 See


