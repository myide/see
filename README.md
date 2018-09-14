
# See SQL审核平台

![](https://img.shields.io/badge/build-release-brightgreen.svg)  
![](https://img.shields.io/badge/version-v1.0.0-brightgreen.svg)  
![](https://img.shields.io/badge/vue.js-2.9.1-brightgreen.svg) 
![](https://img.shields.io/badge/iview-2.8.0-brightgreen.svg?style=flat-square) 
![](https://img.shields.io/badge/python-3.6-brightgreen.svg)
![](https://img.shields.io/badge/Django-2.0-brightgreen.svg)

## 功能

- 目标库管理
    - 目标数据库配置，库/表查询
- SQL操作
    - 基于Inception
    - SQL语法检测
    - SQL语句执行
    - SQL回滚
    - 历史记录
- SQL查询
    - 查询目标数据库的详细表结构
    - SQL语句优化（基于美团SQLAdvisor）
- 用户管理
    - 对用户/组的注册/注销/加组/授权等管理
- 个性化设置
    - 管理员可以做SQL关键字拦截，平台的审批功能开关等设置
    - 用户可以订阅其常用的数据库，指定审批工单的经理，以简化审核时所需的操作
- 人工审批功能
    - 开启流程，工单至少需双人确认才可上线（流程：提交人 -- inception自动审核 -- 经理审批 -- DBA上线）
    - 关闭流程，工单可由经理上线（流程：提交人 -- inception自动审核 -- 经理上线）
- 用户权限
    - 基于RBAC的表级，对象级权限控制体系
    - 通过用户管理设置用户权限
    - 根据用户身份（组员/经理/总监）鉴权用户对SQL的审核/取消/执行/回滚等操作
- 操作流程
    - 用户需要输入SQL，指定环境，执行人，数据库
    - inception自动审核SQL语法，不通过会提示语法信息，通过则进入工单列表待下一步操作
    - 审批人做审批通过或驳回操作
    - 执行人做执行/撤销/回滚等操作
    - SQL列表界面提供SQL查询，操作等相关功能
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

## 安装文档
- [安装文档](https://github.com/myide/see/blob/master/frontend/src/files/install.md)

## 界面展示

- Dashboard审计

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/dashboard.png)

- SQL查询

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/query.png)

- 工单审核

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/check.png)

- 工单设置

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/platsettings.png)

- 工单列表

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/list.png)

- 用户管理

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/user.png)

- API

![image](https://github.com/myide/see/blob/master/frontend/src/images/github/api.png)

## 交流学习
QQ群 630791951

## License

- Eclipse Public License - v 2.0

Copyright © 2018 See


