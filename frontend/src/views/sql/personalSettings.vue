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
              <FormItem label="操作">
                <Button type="primary" @click='handleCreatePersonalSettings'>保存</Button>
              </FormItem>
            </Form>
          </div>
        </Col>       
        <Col span="8">
          <div style="margin-left:20px">
            <Alert type="warning" show-icon closable>
                订阅设置
            <template slot="desc">
              <p>
                您可以在设置里指定常用的数据库及leader，审核工单时只显示这些数据供您选择。
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
        queryParams:{
          cluster:'',
          env:'prd'
        },
        personalSettings:{
          dbs:[],  // id list
          leader:null  // id
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

      getLeader (instance) {
        let leader = null
        if (instance != null) {
          leader = instance.id
        }
        return leader
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

      handleGetPersonalSettings () {
        GetPersonalSettings({env:this.queryParams.env})
        .then(
          response => {
            const data = response.data.results[0]
            this.personalSettings.dbs = this.getDbList(data.db_list)
            if (this.queryParams.env == 'prd') {
              this.personalSettings.leader = this.getLeader(data.leader)
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

