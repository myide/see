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
          <Alert show-icon>SQL审核</Alert>
          <div>
            <Form class="step-form" :label-width="100">
              <FormItem label="SQL条数限制">
                <Slider v-model="sqlsettings.sql_count_limit" :max="10000"></Slider>
              </FormItem>
              <FormItem label="SQL语句禁用词">
                <Input v-model="sqlsettings.forbidden_words" :readonly="readonly" type="textarea" :rows="3" placeholder="SQL语句里不允许出现的词，多个以/分隔" />
              </FormItem>
              <FormItem label="操作">
                <div>
                  <Button type="warning" v-show="readonly == true" @click="editHandle">编辑</Button>
                  <Button type="primary" v-show="readonly == false" @click="saveHandle">保存</Button>
                </div>
              </FormItem>
            </Form>
          </div>
        </Col>       
        <Col span="12">
          <div style="margin-left:20px">
            <Alert type="warning" show-icon closable>
              <b>SQL审核设置</b>
            <template slot="desc">
                <div class="left20">
                  <p><b>1</b>. 限制每个工单的SQL语句数量；默认1000，最大可设置10000。</p>
                </div>
                <div class="left20">
                  <p><b>2</b>. 可指定不允许语句中出现的词（多个以/分隔），对包含禁词的SQL语句，后端会做拦截处理。</p>
                  <p> 示例：*/drop test1/^test2 </p>
                </div>
            </template>
            </Alert>
          </div>
        </Col>
      </Row>

      <Row>            
        <Col span="12">
          <Alert show-icon>工单流</Alert>
          <div>
            <Form class="step-form" :label-width="100">
              <FormItem label="工单流">
                <i-switch size="large" v-model="strategy.is_manual_review" @on-change="handleWriteStrategy">
                  <span slot="open">开启</span>
                  <span slot="close">关闭</span>
                </i-switch>
              </FormItem>
            </Form>
            
          </div>
        </Col>

        <Col span="12">
          <div class="left20">
            <Alert type="warning" show-icon closable>
              <b>工单流设置</b>
              <template slot="desc">
                <p class="left20">
                  <b>1</b>. 关闭，工单流: 提交人 --- 核准人 。
                </p>
                <p class="left20">
                  <b>2</b>. 开启，工单流: 提交人 --- 核准人 --- 管理员 。
                </p>
              </template>
            </Alert>
          </div>
        </Col>
      </Row>

     <Row>            
        <Col span="12">
          <Alert show-icon>邮件提醒</Alert>
          <div>
            <Form class="step-form" :label-width="100">
              <FormItem label="选择事件">
                <div style="border-bottom: 1px solid #e9e9e9;padding-bottom:6px;margin-bottom:6px;">
                  <Checkbox
                    :indeterminate="indeterminate"
                    :value="checkAll"
                    @click.prevent.native="handleCheckAll">全选</Checkbox>
                </div>
                <CheckboxGroup v-model="actions_checked" @on-change="checkAllGroupChange">
                  <Checkbox label="审核"></Checkbox>
                  <Checkbox label="放弃"></Checkbox>
                  <Checkbox label="执行"></Checkbox>
                  <Checkbox label="回滚"></Checkbox>
                  <Checkbox label="审批通过"></Checkbox>
                  <Checkbox label="审批驳回"></Checkbox>
                </CheckboxGroup>
              </FormItem>
              <FormItem label="操作">
                <div>
                  <Button type="primary" @click="handleSetMailActions">提交</Button>
                </div>
              </FormItem>
            </Form>
          </div>
        </Col>

        <Col span="12">
          <div class="left20">
            <Alert type="warning" show-icon closable>
              <b>邮件提醒设置</b>
              <template slot="desc">
                <p class="left20">
                  &nbsp;&nbsp; 对于生产环境的数据库，发生选择的事件时，工单相关人员将收到邮件提醒。
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
  import {GetStrategyList, UpdateStrategy, CreateStrategy} from '@/api/sql/strategy'
  import {GetFWList, UpdateFW, CreateFW} from '@/api/sql/sqlsettings'
  import {GetMailActions, SetMailActions} from '@/api/sql/mailactions'
  import {GetUserList} from '@/api/account/account'
  import copyright from '../my-components/public/copyright'

  export default {
    components: {copyright},
    data () {
      return {
        readonly:true,
        res:[],
        actions:[],
        indeterminate: true,
        checkAll: false,
        actions_checked: [],
        sqlsettings:{
          id:'',
          sql_count_limit:0,
          forbidden_words:''
        },
        userList:[],
        strategy:{
          id:'',
          is_manual_review:false,
        }
      }
    },

    created () {
      this.handleGetUsers()
      this.handleGetFWList()
      this.handleGetStrategyList()
      this.handleGetMailActions()
    },

    methods: {
      handleCheckAll () {
        if (this.indeterminate) {
          this.checkAll = false;
        } else {
          this.checkAll = !this.checkAll;
        }
        this.indeterminate = false;
        if (this.checkAll) {
          this.actions_checked = this.actions;
        } else {
          this.actions_checked = [];
        }
      },
      checkAllGroupChange (data) {
        console.log(data)
        if (data.length === this.actions.length) {
          this.indeterminate = false;
          this.checkAll = true;
        } else if (data.length > 0) {
          this.indeterminate = true;
          this.checkAll = false;
        } else {
          this.indeterminate = false;
          this.checkAll = false;
        }
      },
      getActionName() {
        let actions_checked = []
        for (let i in this.actions_checked) {
          let item = this.actions_checked[i]
          for (let j in this.res) {
            let row = this.res[j]
            if (row.desc_cn == item) {
              actions_checked.push(row.name)
              if (row.desc_cn == '执行') {
                actions_checked.push('select')
              }
              break
            }
          }
        }
        return actions_checked
      },

      handleGetMailActions() {
        GetMailActions({pagesize:1000})
        .then(
          response => {
            this.res = response.data.results
            this.actions = []
            this.actions_checked = []
            for (let i in this.res) {
              let item = this.res[i]
              this.actions.push(item.desc_cn)
              if (item.value == true) {
                this.actions_checked.push(item.desc_cn)
              }
            }
          }
        )
      },

      handleSetMailActions () {
        let data = this.getActionName()
        console.log(data)
        SetMailActions(data)
        .then(
          response => {
            console.log(response)
            this.handleNotice(response)
        })
      },

      notice (title, msg) {
        this.$Notice.success({
          title: title,
          duration: 6,
          desc: msg
        });
      },
      handleNotice (response) {
        let httpstatus = response.status
        if (httpstatus == 200 || httpstatus == 201) {
          let title = '服务器提示'
          let msg = '设置 保存成功'
          this.notice(title, msg)
        }
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
              this.sqlsettings = results[0]
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
        const id = this.sqlsettings.id 
        const data = this.sqlsettings
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

