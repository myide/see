<template>
  <div>
    <Card>
      <Row>            
        <Col span="12">
          <Alert show-icon>设置禁用词</Alert>
          <div>
            <Form class="step-form" :label-width="100">
              <FormItem label="SQL语句禁用词">
                <Input v-model="forbiddenWords.forbidden_words" :readonly="readonly" type="textarea" :rows="4" placeholder="SQL语句里不允许出现的词，多个以空格分隔" />
              </FormItem>
              <FormItem label="操作">
                <div style="margin-left:20px">
                  <Button type="warning" v-show="readonly == true" @click="editHandle">编辑</Button>
                  <Button type="primary" v-show="readonly == false" @click="saveHandle">保存</Button>
                </div>
              </FormItem>
            </Form>
          </div>
        </Col>       
        <Col span="8">
          <div style="margin-left:20px">
            <Alert type="warning" show-icon closable>
                SQL语句禁用词
            <template slot="desc">
              可指定不允许语句中出现的词，对包含禁词的SQL语句，后端会做拦截处理。
            </template>
            </Alert>
          </div>
        </Col>

      </Row>

      <Row>            
        <Col span="12">
          <Alert show-icon>设置审批方式</Alert>
          <div>
            <Form class="step-form" :label-width="100">
              <FormItem label="开启审批流">
                <i-switch v-model="strategy.is_manual_review" @on-change="change" />
              </FormItem>
              <FormItem label="工单SQL操作人" v-show="strategy.is_manual_review">
                <Select v-model="strategy.users" multiple filterable>
                  <Option v-for="item in userList" :value="item.id" :key="item.id">{{ item.username }}</Option>
                </Select>
              </FormItem>
              <FormItem label="操作">
                <div style="margin-left:20px">
                  <Button type="primary" @click="handleWriteStrategy">提交</Button>
                </div>
              </FormItem>
            </Form>
            
          </div>
        </Col>

        <Col span="8">
          <div style="margin-left:20px">
            <Alert type="warning" show-icon closable>
                设置审批方式
            <template slot="desc">
              可选择开启或关闭审批流，开启后工单需要审批人通过后，由管理员执行；关闭后工单由审批人直接执行。
            </template>
            </Alert>
          </div>
        </Col>

      </Row>

    </Card>
  </div>
</template>
<script>
  import {GetStrategyList, UpdateStrategy, CreateStrategy} from '@/api/sql/strategy'
  import {GetFWList, UpdateFW, CreateFW} from '@/api/sql/forbiddenwords'
  import {GetUserList} from '@/api/account/account'

  export default {
    components: {},
    data () {
      return {
        readonly:true,
        forbiddenWords:{
          id:'',
          forbidden_words:''
        },
        userList:[],
        strategy:{
          id:'',
          is_manual_review:false,
          users:[]
        },

      }
    },

    created () {
      this.handleGetUsers()
      this.handleGetFWList()
      this.handleGetStrategyList()
    },

    methods: {

      notice (title, msg) {
        this.$Notice.success({
          title: title,
          duration: 6,
          desc: msg
        });
      },

      handleNotice (response) {
        let httpstatus = response.status
        if (httpstatus == 200) {
          let title = '服务器提示'
          let msg = '设置 保存成功'
          this.notice(title, msg)
        }
      },

      change (status) {
        this.$Message.info('开关状态：' + status);
      },

      editHandle () {
        this.readonly = false
      },
      
      saveHandle () {
        this.readonly = true
        this.handleWriteFW()
      },

      handleGetStrategyList () {
        GetStrategyList({})
        .then(
          response => {
            console.log(response)
            const results = response.data.results
            if (results.length > 0) {
              this.strategy = results[0]
            }
          }
        )
      },

      handleWriteStrategy () {
        const id = this.strategy.id 
        const data = this.strategy
        if (id == '') {
          CreateStrategy (data)  
          .then(
            response => {
              this.handleNotice(response)
              this.handleGetStrategyList()
            },
          )
        } else {
          UpdateStrategy (id, data)  
          .then(
            response => {
              this.handleNotice(response)
              this.handleGetStrategyList()
            },
          )
        }
      },

      handleGetFWList () {
        GetFWList({})
        .then(
          response => {
            console.log(response)
            const results = response.data.results
            if (results.length > 0) {
              this.forbiddenWords = results[0]
            }
          }
        )
      },

      handleGetUsers () {
        GetUserList({pagesize:1000})
        .then(
          response => {
            console.log(response)
            this.userList = []
            const results = response.data.results
            for (let i in results) {
              let user = results[i]
              if (user.is_superuser == true) {
                this.userList.push(user)
              }
            }

          }
        )
      },

      handleWriteFW () {
        const id = this.forbiddenWords.id 
        const data = this.forbiddenWords
        if (id == '') {
          CreateFW (data)  
          .then(
            response => {
              this.handleNotice(response)
              this.handleGetFWList()
            },
          )
        } else {
          UpdateFW (id, data)  
          .then(
            response => {
              this.handleNotice(response)
              this.handleGetFWList()
            },
          )
        }

      },

    },


  }
</script>

