<style scoped>
  .left20 {
    margin-left: 20px
  }
</style>

<template>
  <div>
    <Card>
      <Row>            
        <Col span="12">
          <Alert show-icon>订阅</Alert>
          <div>
            <Form class="step-form" :label-width="100">
              <FormItem label="集群">
                <Select v-model="queryParams.cluster" filterable @on-change="handleChange">
                  <Option v-for="item in clusterList" :value="item.id" :key="item.id">{{ item.name }}</Option>
                </Select>
              </FormItem>
              <FormItem label="环境">
                <RadioGroup v-model="queryParams.env" @on-change="handleChange">
                  <Radio label="prd">生产</Radio>
                  <Radio label="test">测试</Radio>
                </RadioGroup>
              </FormItem>
              <FormItem label="数据库">
                <Select v-model="personalSettings.dbs" multiple filterable>
                  <Option v-for="item in dbList" :value="item.id" :key="item.id">{{ item.name }}</Option>
                </Select>
              </FormItem>
              <FormItem label="工单核准人" v-if="showLeader">
                <Select v-model="personalSettings.leader" filterable>
                  <Option v-for="item in leaderList" :value="item.id" :key="item.id">{{ item.username }}</Option>
                </Select>
              </FormItem>
              <FormItem label="管理员组收件人" v-if="showLeader">
                <Select v-model="personalSettings.admin_mail" filterable>
                  <Option v-for="item in adminList" :value="item.id" :key="item.id">{{ item.username }}</Option>
                </Select>
              </FormItem>
              <FormItem label="操作">
                <Button type="primary" @click='handleCreatePersonalSettings'>保存</Button>
              </FormItem>
            </Form>
          </div>
        </Col>       
        <Col span="12">
          <div style="margin-left:20px">
            <Alert type="warning" show-icon closable>
              <b>订阅设置</b>
            <template slot="desc">
              <p class="left20">
                您可以在设置里指定常用的数据库及leader，提交工单时只显示这些数据供您选择。
              </p>
              <p>
                <b>1</b>.  关于工单核准人
              </p>
              <p class="left20">
                <b>1.1</b>. 研发角色：工单核准人是同组的经理（角色/组 在用户管理里设置）。
              </p>
              <p class="left20">
                <b>1.2</b>. 经理/总监/管理员角色：工单核准人是自己。
              </p>
              <p>
                <b>2</b>.  关于管理员组收件人
              </p>
              <p class="left20">
                <b>2.1</b>. 指定接收工单邮件的管理员。
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
  import {GetSelectData, GetPersonalSettings, CreatePersonalSettings} from '@/api/sql/check'
  import {GetMailActions, SetMailActions} from '@/api/sql/mailactions'
  import {GetClusterList} from '@/api/sql/cluster'
  import copyright from '../my-components/public/copyright'
  
  export default {
    components:{copyright},
    data () {
      return {
        showLeader:true,
        dbList:[],
        clusterList:[],
        leaderList:[],
        adminList:[],
        queryParams:{
          cluster:'',
          env:'prd'
        },
        personalSettings:{
          dbs:[],  // id list
          leader:null,  // id
          admin_mail:null
        },
      }
    },

    created () {
      this.handleInitData()
    },

    methods: {

      notice (title, msg) {
        this.$Notice.success({
          title: title,
          duration: 6,
          desc: msg
        });
      },

      getDbList (list) {
        let res = []
        for (let i in list) {
          res.push(list[i].id)
        }
        return res
      },

      getLeaderID (instance) {
        let leaderID = null
        if (instance != null) {
          leaderID = instance.id
        }
        return leaderID
      },

      handleInitData () {
        this.handleGetClusterList()
        this.handleGetPersonalSettings()
      },

      handleChange (e) {
        if (e == 'prd'){
          this.showLeader = true
        } else if (e == 'test') {
          this.showLeader = false
        }
        this.handleSelect()
        this.handleGetPersonalSettings()
      },

      handleGetMailActions () {
        

      },

      handleGetPersonalSettings () {
        GetPersonalSettings({env:this.queryParams.env})
        .then(
          response => {
            const data = response.data.results[0]
            this.personalSettings.dbs = this.getDbList(data.db_list)
            if (this.queryParams.env == 'prd') {
              this.personalSettings.leader = this.getLeaderID(data.leader)
              this.personalSettings.admin_mail = data.admin_mail
            }
          }
        )
      },

      handleSelect () {
        let data = this.queryParams
        GetSelectData(data)
        .then(response => {
          this.dbList = response.data.data.dbs
          this.leaderList = response.data.data.treaters
          this.adminList = response.data.data.admins
        })
      },

      handleGetClusterList () {
        this.spinShow = true
        GetClusterList(this.getClusterParams)
        .then(
          res => {
            this.spinShow = false
            this.clusterList = res.data.results
            this.setDefaultCluster()
          }
        )
      },

      setDefaultCluster () {
        if (this.clusterList.length != 0) {
          this.queryParams.cluster = this.clusterList[0].id
        }
      },

      handleCreatePersonalSettings () {
        this.personalSettings.cluster = this.queryParams.cluster
        this.personalSettings.env = this.queryParams.env
        const data = this.personalSettings
        CreatePersonalSettings (data)  
        .then(
          response => {
            let httpstatus = response.status
            if (httpstatus == 200) {
              let title = '服务器提示'
              let msg = '设置 保存成功'
              this.notice(title, msg)
            }
            this.handleInitData()
          },
        )
      }

    },

  }
</script>

