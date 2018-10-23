<template>
  <div>
    <Card>
      <Row>            
        <Col span="12">
          <Alert show-icon>订阅</Alert>
          <div>
            <Form class="step-form" :label-width="100">
              <FormItem label="常用数据库">
                <Select v-model="personalSettings.dbs" multiple filterable>
                  <Option v-for="item in dbList" :value="item.id" :key="item.id">{{ item.name }}</Option>
                </Select>
              </FormItem>
              <FormItem label="工单核准人">
                <Select v-model="personalSettings.leader" filterable>
                  <Option v-for="item in leaderList" :value="item.id" :key="item.id">{{ item.username }}</Option>
                </Select>
              </FormItem>
              <FormItem label="操作">
                <Row>
                  <Col span="12">
                    <center>
                      <Button type="primary" @click='handleCreatePersonalSettings'>保存</Button>
                    </center>
                  </Col>
                </Row>
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
  import copyright from '../my-components/public/copyright'
  
  export default {
    components:{copyright},
    data () {
      return {
        dbList:[],
        leaderList:[],
        personalSettings:{
          dbs:[],  // id list
          leader:null  // id
        },
      }
    },

    created () {
      this.handleGetData()
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

      handleGetData () {
        this.handleSelect()
        this.handleGetPersonalSettings()
      },

      handleGetPersonalSettings () {
        GetPersonalSettings({env:'prd'})
        .then(
          response => {
            console.log(response)
            const data = response.data.results[0]
            this.personalSettings.dbs = this.getDbList(data.db_list)
            this.personalSettings.leader = this.getLeader(data.leader)
          }
        )
      },

      handleSelect () {
        GetSelectData({env:'prd'})
        .then(response => {
          console.log(response)
          this.dbList = response.data.data.dbs
          this.leaderList = response.data.data.treaters
        })
        .catch(error => {
          console.log(error)
        })
      },

      handleCreatePersonalSettings () {
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
            this.handleGetData()
          },
        )
      }

    },

  }
</script>

