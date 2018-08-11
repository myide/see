<template>
  <div>
      <Card>
      <Row>            
        <Col span="12">
            <Alert show-icon>输入要上线的SQL语句</Alert>
            </br>
            <div>
              <Form class="step-form" ref="checkContent" :model="checkData" :rules="ruleCheckData" :label-width="100">
                <FormItem label="SQL" prop="sql_content">
                  <Input v-model="checkData.sql_content" type="textarea" :autosize="{minRows: 10,maxRows: 20}" placeholder="请输入SQL" />
                </FormItem>
                <FormItem label="备注">
                  <Input v-model="checkData.remark" type="textarea" :autosize="{minRows: 2,maxRows: 5}" placeholder="请输入备注" />
                </FormItem>
                <FormItem label="操作">
                  <Row>
                    <Col span="12">
                      <center>
                        <Button type="primary" @click='handleCheckSql'>审核</Button>
                      </center>
                    </Col>
                    <Col span="12">
                      <center>
                        <Button @click='handleClear'>清空</Button>
                      </center>
                    </Col>
                  </Row>
                </FormItem>
              </Form>
            </div>
            </Col>

          <Col span="12">
            <Alert show-icon style='margin-left:12%'>
              <Icon type="ios-lightbulb-outline" slot="icon"></Icon>
                选择执行条件
            </Alert>
            <div style='margin-left:50px'>
              </br>
              <div>
                <Form class="step-form" ref="checkConf" :model="checkData" :rules="ruleCheckData" :label-width="100">
                  <FormItem label="环境">
                    <RadioGroup v-model="checkData.env" @on-change="handleSelect">
                      <Radio label="prd">生产</Radio>
                      <Radio label="test">测试</Radio>
                    </RadioGroup>
                  </FormItem>
                  <FormItem label="数据库" prop="db">
                    <Select v-model="checkData.db" style="width:200px; margin-left:10px">
                        <Option v-for="item in dbList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                    </Select>
                  </FormItem>
                  <FormItem label="执行人" prop="treater">
                    <Select v-model="checkData.treater" @on-change="selectTreater" label-in-value style="width:200px; margin-left:10px">
                        <Option v-for="item in transactorList" :value="item.value" :key="item.label">{{ item.label }}</Option>
                    </Select>
                  </FormItem>
                </Form>
              </div>

            </div>
        </Col>
      </Row>

    </Card>

  </div>
</template>
<script>
  import { GetSelectData, CheckSql } from '@/api/sql/check'

  export default {
    data () {
      return {
        checkData: {
          sql_content:'',
          remark:'',
          env:'prd',
          db:'',
          treater:'',
          commiter:'',
          users:[]
        },
        treaters:[],
        commiter:{},
        ruleCheckData: {
          sql_content: [{ required: true, message: '请填写SQL', trigger: 'blur' }],
          treater:  [{ required: true, message: '请选择执行人', trigger: 'change', type: 'number' }],
          db: [{ required: true, message: '请选择数据库', trigger: 'change', type: 'number' }],
        },
        dbList: [],
        transactorList: [],
        keyMap: {
          'sql_content':'SQL',
          'env':'环境',
          'db':'数据库',
          'treater':'执行人',
        },
      }
    },

    created () {
      this.handleSelect(this.checkData.env)
    },

    methods: {
      renderFunc (treater) {
        this.$Notice.success({
          title: 'SQL审核通过',
          desc: 'SQL审核通过...',
          render: h => {
            return h('span', [
              '请等待 ',
              h('a', treater),
              ' 执行'
            ])
          }
        });
      },

      warning (title, msg) {
        this.$Notice.warning({
          title: title,
          duration: 0,
          desc: msg
        });
      },

      handleClear () {
        this.checkData.sql_content = ''
      },

      selectTreater (data) {
        const treaterId = data.value
        this.checkData.users = [this.commiter.id, treaterId]
      },

      getTreaterName (id) { 
        for (let i in this.treaters) {
          let item = this.treaters[i]
          if (item.id == id) {
            return item.username
          } 
        }
      },

      handleSelect (e) {
        GetSelectData({env:e})
        .then(response => {
          console.log(response)
          const dbs = response.data.data.dbs
          const treaters = response.data.data.treaters
          this.treaters = treaters 
          this.commiter = response.data.data.commiter
          this.checkData.commiter = response.data.data.commiter.username
          this.dbList = []
          dbs.map( (item) => {
            this.dbList.push({
              value:item.id,
              label:item.name
            })
          })
          this.transactorList = []
          treaters.map( (item) => {
            this.transactorList.push({
              value:item.id,
              label:item.username,
            })
          })
        })
        .catch(error => {
          console.log(error)
        })
      },
      
      handleCheckSql () {
        this.$refs.checkContent.validate((valid) => {
          if (!valid) {
            return
          }
          this.$refs.checkConf.validate((valid) => {
            if (!valid) {
              return
            }
            this.checkData.treater_username = this.getTreaterName(this.checkData.treater)
            CheckSql(this.checkData)
            .then(response => {
              console.log(response)
              let status = response.data.status
              let msg = response.data.msg
              if (status == 0){
                this.renderFunc(this.getTreaterName(this.checkData.treater))
              } else if (status == -1 || status == -2){
                this.warning('SQL审核不通过', msg)
              } 
            })
            .catch(error => {
              console.log(error)
            })
          })
        })

      },


    },


  }
</script>

