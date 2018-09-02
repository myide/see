<style scoped>
    .parm_check_element {
      width: 200px;
      margin-left: 10px;
    }
</style>

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
                  <editor v-model="checkData.sql_content" @init="editorInit" @setCompletions="setCompletions"></editor>
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
                    <Select v-model="checkData.db" class="parm_check_element" filterable>
                        <Option v-for="item in dbList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                    </Select>
                  </FormItem>
                  <FormItem label="工单处理人" prop="treater">
                      <Input v-model="checkData.treater_username" class="parm_check_element" :readonly="readonly" />
                  </FormItem>
                </Form>
              </div>
              <div>
                <Alert type="warning" show-icon closable>
                    <p><b>Tips</b></p>
                <template slot="desc">
                  <p>
                    <b>1</b>.  您可以在<router-link to='/sqlmng/settings'><b>设置</b></router-link>里指定常用的数据库&工单处理人，之后只显示这些数据供您选择。
                  </p>
                  <p>
                    <b>2</b>.  关于流程
                  </p>
                  <p style="margin-left:20px">
                    <b>2.1</b>. 若管理员没有设置流程，工单将按 提交人 --- 执行人 的流程进行处理。
                  </p>
                  <p style="margin-left:20px">
                    <b>2.2</b>. 若管理员有设置流程，工单将按 提交人 --- 审批人 --- 执行人 的流程进行处理。
                  </p>
                </template>
                </Alert>
              </div>
            </div>
        </Col>
      </Row>

    </Card>

  </div>
</template>
<script>
  import { GetPersonalSettings, CheckSql } from '@/api/sql/check'
  import editor from '../my-components/sql/editor'
  
  export default {
    components: {editor},
    data () {
      return {
        readonly:true,
        wordList:[],
        checkData:{
          treater_username:'',
          sql_content:'',
          remark:'',
          env:'prd',
          db:'',
          treater:'',
          commiter:'',
          users:[]
        },
        commiter:{},
        ruleCheckData:{
          sql_content:[{ required: true, message: '请输入SQL', trigger: 'blur' }],
          treater:[{ required: true, message: '请选择执行人', trigger: 'change', type: 'number' }],
          db: [{ required: true, message: '请选择数据库', trigger: 'change', type: 'number' }],
        },
        dbList:[],
        keyMap:{
          'sql_content':'SQL',
          'env':'环境',
          'db':'数据库',
          'treater':'执行人',
        },
      }
    },

    created () {
      this.getWordList()
      this.handleSelect(this.checkData.env)
    },

    methods: {

      getWordList () {
        for (let i of this.util.highlight.split('|')) {
          this.wordList.push({'vl': i, 'meta': '关键字'})
        }
      },

      setCompletions (editor, session, pos, prefix, callback) {
        callback(null, this.wordList.map(function (word) {
          return {
            caption: word.vl,
            value: word.vl,
            meta: word.meta
          }
        }))
      },

      editorInit: function () {               
        require('brace/mode/mysql')    //language
        require('brace/theme/xcode')
      },

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

      setTreater (treater) {
        if (JSON.stringify(treater) != "{}") {
          this.checkData.treater = treater.id
          this.checkData.treater_username = treater.username
        }
      },

      handleSelect (e) {
        GetPersonalSettings({env:e})
        .then(response => {
          console.log(response)
          const data = response.data.results[0]
          const dbs = data.db_list
          const commiter = data.commiter
          const treater = data.leader
          this.setTreater(treater)
          this.checkData.commiter = commiter.username
          this.checkData.users = [commiter.id, treater.id]
          this.dbList = []
          dbs.map( (item) => {
            this.dbList.push({
              value:item.id,
              label:item.name
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
            CheckSql(this.checkData)
            .then(response => {
              console.log(response)
              let status = response.data.status
              let msg = response.data.msg
              if (status == 0){
                this.renderFunc(this.checkData.treater_username)
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
