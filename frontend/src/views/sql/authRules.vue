<style scoped>
  .left20 {
    margin-left: 20px;
  }
  .left40 {
    margin-left: 40px;
  }
  .left60 {
    margin-left: 60px;
  }
</style>

<template>
  <div>
    <Card>
      <Row>            
        <Col span="12">
          <Alert show-icon>权限表</Alert>
          <div>
            <Tabs type="card" @on-click="handleChangeTab">
                <TabPane name="prd" label="生产环境"> <Table size="small" :columns="columnsAuth" :data="authRules"></Table> </TabPane>
                <TabPane name="test" label="测试环境"> <Table size="small" :columns="columnsAuth" :data="authRules"></Table> </TabPane>
            </Tabs>
          </div>
        </Col>       
        <Col span="12">
          <div class='left20'>
            <Alert type="warning" show-icon closable>
              <b>平台使用步骤</b>
                <template slot="desc">
                  <div class='left20'>
                    <b>1</b>. 创建目标数据库/集群（申请 功能一般是研发人员使用，用来向管理员提交建库申请）
                  </div>
                  <div class='left20'>
                    <b>2</b>. 创建组/用户
                  </div>
                  <div class='left20'>
                    <b>3</b>. 平台流程设置
                  </div>
                  <div class='left20'>
                    <b>4</b>. SQL工单设置
                  </div>
                  <div class='left20'>
                    <b>5</b>. 提交SQL工单及后续处理
                  </div>
                </template>
            </Alert>
          </div>

          <div class='left20'>
            <Alert type="warning" show-icon closable>
                <b>流程说明</b>
                <template slot="desc">
                  <div class='left20'>
                    <b>1</b>. 测试环境
                  </div>
                  <div class="left40">
                    <b>1.1</b>. 提交人发起 --- 提交人执行
                  </div>
                  <div class='left20'>
                    <b>2</b>. 生产环境
                  </div>
                  <div class='left40'>
                    <b>2.1</b>. 无流程
                  </div>
                  <div class='left60'>
                    研发： 研发发起 --- 经理执行 
                  </div>
                  <div class='left60'>
                    其它角色： 本用户发起 --- 本用户执行 
                  </div>
                  <div class='left40'>
                    <b>2.2</b>. 有流程
                  </div>
                  <div class='left60'>
                    研发： 研发发起 --- 经理核准 --- 管理员执行
                  </div>
                  <div class='left60'>
                    经理： 经理发起 --- 经理核准 --- 管理员执行
                  </div>
                  <div class='left60'>
                    总监： 总监发起 --- 总监核准 --- 管理员执行
                  </div>
                  <div class='left60'>
                    管理员：管理员发起 --- 管理员本人核准 --- 其它管理员执行
                  </div>
                </template>
            </Alert>
          </div>

          <div class='left20'>
            <Alert type="warning" show-icon closable>
                <b>数据库权限</b>
                <template slot="desc">
                  <div class='left20'>
                    <b>1</b>. 用户拥有的权限 = 用户权限 + 用户组的权限
                  </div>
                  <div class='left20'>
                    <b>2</b>. 管理员可以对所有用户授权
                  </div>
                  <div class='left20'>
                    <b>3</b>. 经理/总监 可以把自己拥有的权限对研发人员授权
                  </div>
                  <div class='left20'>
                    <b>4</b>. 用户对自己拥有权限的数据库可以设置订阅，进而可以做后续操作
                  </div>
                </template>
            </Alert>
          </div>

        </Col>

      </Row>

    </Card>
    <copyright> </copyright>

  </div>
</template>
<script>
  import {Icon} from 'iview'
  import {GetAuthRules} from '@/api/sql/authRules'
  import copyright from '../my-components/public/copyright'

  export default {
    components: {Icon, copyright},
    data () {
      return {
        getParams:{
          page:1,
          pagesize:1000,
          search:'prd',
        },
        iconMap : {
          true: "checkmark",
          false: "close"
        },
        columnsAuth: [
            {
                title: '工单流程',
                render: (h, params) => {
                  const value = params.row.is_manual_review
                  return h(Icon, {props:{type:this.iconMap[value]}}, [])
                }
            },
            {
                title: '角色',
                render: (h, params) => {
                  const roleMap = {
                    developer:'研发',
                    developer_manager:'研发经理',
                    developer_supremo:'研发总监',
                    admin:'管理员'
                  }
                  const value = params.row.role
                  return h('span', {props:{}}, [roleMap[value]])
                }   
            },
            {
                title: '执行',
                render: (h, params) => {
                  const value = params.row.execute
                  return h(Icon, {props:{type:this.iconMap[value]}}, [])
                }
            },
            {
                title: '放弃',
                render: (h, params) => {
                  const value = params.row.reject
                  return h(Icon, {props:{type:this.iconMap[value]}}, [])
                }
            },
            {
                title: '回滚',
                render: (h, params) => {
                  const value = params.row.rollback
                  return h(Icon, {props:{type:this.iconMap[value]}}, [])
                }
            },
            {
                title: '审批',
                render: (h, params) => {
                  const value = params.row.approve
                  return h(Icon, {props:{type:this.iconMap[value]}}, [])
                }
            },
        ],
        authRules:[]

      }
    },

    created () {
      this.handleGetAuthRules()
    },

    methods: {

      handleChangeTab (name) {
        this.getParams.search = name
        this.handleGetAuthRules()
      },

      handleGetAuthRules () {
        GetAuthRules(this.getParams)
        .then(
          response => {
            this.authRules = response.data.results
          }
        )
      },

    },


  }
</script>

