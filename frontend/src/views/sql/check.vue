
<style scoped>
  .parm_check_element {
    width: 400px;
    margin-left: 10px;
  }
  .left20 {
    margin-left: 20px
  }
  .checkException {
    background: black;
    color:white;
    max-height:360px; 
    overflow-y:auto
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
                <Form ref="checkConf" :model="checkData" :rules="ruleCheckData" :label-width="100">
                  <FormItem label="目标数据库">
                    <Cascader :data="targetDbs" v-model="targetDb" trigger="hover" class="parm_check_element" @on-change="handleSelect"></Cascader>
                  </FormItem>
                  <FormItem label="工单核准人" prop="treater">
                    <Input v-model="checkData.treater_username" class="parm_check_element" :readonly="readonly" />
                  </FormItem>
                </Form>
              </div>
              <div>
                <Alert type="warning" show-icon closable>
                <p><b>Tips</b></p>
                <template slot="desc">
                  <p>
                    <b>1</b>.  您可以在<router-link to='/sqlmng/settings'><b>设置</b></router-link>里指定常用的数据库&工单核准人，之后只显示这些数据供您选择。
                  </p>
                  <p>
                    <b>2</b>.  关于流程 (由管理员在 <router-link to='/settings/platform'><b>流程设置</b></router-link>里指定 )
                  </p>
                  <p class="left20">
                    <b>2.1</b>. 关闭流程，工单流: 提交人 --- 核准人 。
                  </p>
                  <p class="left20">
                    <b>2.2</b>. 开启流程，工单流: 提交人 --- 核准人 --- 管理员 。
                  </p>
                </template>
                </Alert>
              </div>
            </div>
        </Col>
      </Row>

    </Card>
    <copyright> </copyright>

    <Modal
        v-model="showException"
        width="800"
        :styles="{right: '10px'}"
        title="SQL语法错误">
        <div class="checkException">
          <div v-for="item in exceptionList" :value="item" :key="item">{{ item }}</div>
        </div>
    </Modal>    

  </div>
</template>
<script>
  import {CascaderData} from '@/utils/sql/formatData'
  import { GetPersonalSettings, CheckSql } from '@/api/sql/check'
  import editor from '../my-components/sql/editor'
  import copyright from '../my-components/public/copyright'

  export default {
    components: {editor, copyright},
    data () {
      return {
        showException:false,
        readonly:true,
        exceptionList:[],
        wordList:[],
        env_map: {
          prd:'生产',
          test:'测试',
          '生产':'prd',
          '测试':'test'
        },
        checkData:{
          sql_content:'',
          remark:'',
          env:'',
          db:'',
          treater_username:'',
          treater:'',
          commiter:'',
          users:[],
        },
        commiter:{},
        ruleCheckData:{
          sql_content:[{ required: true, message: '请输入SQL', trigger: 'blur' }],
          treater:[{ required: true, message: '请设置工单核准人', trigger: 'change', type: 'number' }],
          db: [{ required: true, message: '请选择数据库', trigger: 'change', type: 'array', len: 3, fields: {0: {type: "number", required: true},1: {type: "string", required: true},2: {type: "number", required: true}} }],
        },
        targetDb:[],
        targetDbs:[],
      }
    },

    created () {
      this.getWordList()
      this.handleSelect()
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

      renderFunc (treater, title) {
        this.$Notice.success({
          title: title,
          render: h => {
            return h('span', [
              '请等待 ',
              h('a', treater),
              ' 处理'
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

      treaterClear(){
        this.checkData.treater_username = ''
        this.checkData.treater = ''
      },

      handleSelect (e) {
        this.treaterClear()
        if (e == undefined) {
          var env = 'test'
        } else {
          env = this.env_map[e[1]]
        }
        const data = {
          env:env
        }
        GetPersonalSettings(data)
        .then(response => {
          const data = response.data.results[0]
          const dbs = data.db_list
          const commiter = data.commiter
          const treater = data.leader
          this.setTreater(treater)
          this.checkData.commiter = commiter.username
          this.checkData.users = [commiter.id, treater.id]
          dbs.map( (item) => {
            item.env = this.env_map[item.env]
          })
          this.targetDbs = CascaderData(dbs)       
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
            this.checkData.env = this.env_map[this.targetDb[1]]
            this.checkData.db = this.targetDb[2]
            CheckSql(this.checkData)
            .then(response => {
              let status = response.data.status
              let data = response.data.data
              let msg = response.data.msg
              if (status == 0){
                this.renderFunc(this.checkData.treater_username, 'SQL工单 已提交')          
              } else if (status == -1 || status == -2){
                this.warning('SQL审核不通过', msg)
              } 
            })
            .catch(err => {
              let exceptionSQL = err.response.request.response.replace('[', '').replace(']', '')
              this.exceptionList = exceptionSQL.split(',')
              this.showException = true
            })

          })
        })

      },

    },

  }
</script>
