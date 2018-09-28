<style scoped>
    .spaceLeft {
        margin-left: 20px;
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
        <Col span="10">
          <div class='spaceLeft'>
            <Alert type="warning" show-icon closable>
                <b>附加规则</b>
                <template slot="desc">
                      <p> 对于有审批流程的工单，有如下的规则：</p>
                      <p>
                        <b>1. 关于审批类的操作</b>
                      </p>
                      <p class='spaceLeft'>
                        <b>1.1</b>. 需要当前用户是工单的审批人
                      </p>

                      <p>
                        <b>2. 关于执行类的操作</b>
                      </p>
                      <p class='spaceLeft'>
                        <b>2.1</b>. 需要工单已经被审批通过
                      </p>
                      <p class='spaceLeft'>
                        <b>2.2</b>. 需要审批人与执行人（当前用户）不能相同
                      </p>

                      <p>
                        <b>3. 关于放弃工单的操作</b>
                      </p>
                      <p class='spaceLeft'>
                        <b>3.1</b>. 工单有无流程均可做放弃操作
                      </p>
                      <p class='spaceLeft'>
                        <b>3.2</b>. 有流程时，不可做越步放弃，只能放弃流转到本人的工单
                      </p>
                      <p class='spaceLeft'>
                        <b>   </b>  例：研发不能放弃已流转到经理的工单，管理员不能放弃还没流转到自己的工单
                      </p>

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
            console.log(response)
            this.authRules = response.data.results
          }
        )
      },

    },


  }
</script>

