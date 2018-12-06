<style scoped>
  .parm_check_element {
    width: 320px;
    margin-left: 20px;
  }
</style>

<template>
  <div>
    <Card>
      <Row>            
        <Col span="12">
          <div>
            <Alert show-icon>数据库表结构</Alert>
            <Row>
              <Col span="12">
                <Cascader :data="targetDbs" trigger="hover" @on-change="handleGetTables" placeholder="选择数据库"></Cascader>
              </Col>
              <Col span="2">
                <div>&nbsp;</div>
              </Col>
              <Col span="10">
                <Select v-model="table" @on-change="handleGetTableInfo" placeholder="选择表" filterable>
                  <Option v-for="item in tableList" :value="item" :key="item">{{ item }}</Option>
                </Select>
              </Col>
            </Row>
          </div>
          </br>
          <Alert show-icon>SQL语句优化</Alert>
          </br>
          <div>
            <Form class="step-form" ref="checkContent" :model="checkData" :rules="ruleCheckData" :label-width="100">
              <FormItem label="优化类型" prop="type">
                <RadioGroup v-model="optimizeType">
                  <Radio label="SOAR"></Radio>
                  <Radio label="SQLAdvisor"></Radio>
                </RadioGroup>
              </FormItem>
              <FormItem label="SQL语句" prop="sql">
                <editor v-model="checkData.sql" @init="editorInit" @setCompletions="setCompletions"></editor>
              </FormItem>
              <FormItem label="操作">
                <div v-if="optimizeType=='SQLAdvisor'">
                  <Row>
                    <Col span="12">
                      <center>
                        <Button type="primary" @click='handleCheckSql'>查询</Button>
                      </center>
                    </Col>
                    <Col span="12">
                      <center>
                        <Button @click='handleClear'>清空</Button>
                      </center>
                    </Col>
                  </Row>
                </div>
                <div v-if="optimizeType=='SOAR'">
                  <Row>
                    <Col span="6">
                      <center>
                        <Button type="primary" @click="SOARAllowOnline">SQL评分</Button>
                      </center>
                    </Col>
                    <Col span="6">
                      <center>
                        <Button type="primary" @click="SOARBnlySyntax">语法检查</Button>
                      </center>
                    </Col>
                    <Col span="6">
                      <center>
                        <Button type="primary" @click="SOARFingerPrint">SQL指纹</Button>
                      </center>
                    </Col>
                    <Col span="6">
                      <center>
                        <Button type="primary" @click="SOARPretty">SQL美化</Button>
                      </center>
                    </Col>
                  </Row>
                </div>
              </FormItem>
            </Form>
          </div>
        </Col>

        <Col span="12">
            <Alert show-icon style='margin-left:6%'>
              <Icon type="ios-lightbulb-outline" slot="icon"></Icon>
                查询结果 {{query_type}}
            </Alert>
            <div style='margin-left:50px'>
              <vue-markdown :source="query_result"> </vue-markdown>
            </div>
        </Col>
      </Row>
    </Card>
    <copyright> </copyright>
  </div>
</template>

<script>
  import {GetDbList} from '@/api/sql/dbs'
  import {GetPersonalSettings} from '@/api/sql/check'
  import {CascaderData} from '@/utils/sql/formatData'
  import {GetTableList, GetTableInfo, GetSqlAdvisor, GetSqlSOAR} from '@/api/sql/sqlquery'
  import editor from '../my-components/sql/editor'
  import copyright from '../my-components/public/copyright'
  import VueMarkdown from 'vue-markdown'

  export default {
    components: {editor, copyright, VueMarkdown},
    data () {
      return {
        spinShow: false,
        optimizeType:'SOAR',
        targetDbs:[],
        wordList:[],
        dbList:[],
        tableList:[],
        table:'',
        query_type:'',
        query_result:'',
        checkData:{
          sql:'',
        },
        env_map: {
          prd:'生产',
          test:'测试',
          '生产':'prd',
          '测试':'test'
        },
        getParams:{
          page:1,
          pagesize:1000,
          search:'',
        },
        ruleCheckData:{
          type:[{ required: true, message: '请选择优化类型', trigger: 'blur' }],
          sql:[{ required: true, message: '请输入SQL', trigger: 'blur' }],
          treater:[{ required: true, message: '请选择执行人', trigger: 'change', type: 'number' }],
          db: [{ required: true, message: '请选择数据库', trigger: 'change', type: 'number' }],
        },
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
        this.checkData.sql = ''
      },

      SOARAllowOnline () {
        this.query_type = ' / SOAR SQL评分'
        let soar_type = 'allow_online'
        this.handleSOAR(soar_type)
      },

      SOARBnlySyntax () {
        this.query_type = ' / SOAR 语法检查'
        let soar_type = 'only_syntax'
        this.handleSOAR(soar_type)
      },

      SOARFingerPrint () {
        this.query_type = ' / SOAR SQL指纹'
        let soar_type = 'fingerprint'
        this.handleSOAR(soar_type)
      },

      SOARPretty () {
        this.query_type = ' / SOAR SQL美化'
        let soar_type = 'pretty'
        this.handleSOAR(soar_type)
      },

      handleSelect () {
        GetPersonalSettings()
        .then(response => {
          const data = response.data.results[0]
          const dbs = data.db_list
          dbs.map( (item) => {
              item.env = this.env_map[item.env]
          })
          this.targetDbs = CascaderData(dbs)          
        })
      },

      handleGetTables (e) {
        this.database = e[2]
        this.spinShow = true
        GetTableList(this.database)
        .then(
          response => {
            this.spinShow = false
            this.tableList = response.data.results
          }
        )
      },

      handleGetTableInfo (e) {
        if (e.length != 0){
          this.spinShow = true
          this.query_type = ' / 表结构'
          GetTableInfo(this.database, e)
          .then(
          response => {
            this.spinShow = false
            this.query_result = response.data.results
          }
          )
        }
      },

      handleCheckSql () {
        this.query_type = ' / SQLAdvisor 优化建议'
        GetSqlAdvisor(this.database, this.checkData.sql)
        .then(
          response => {
            this.spinShow = false
            this.query_result = response.data.results
          }
        )
      },

      handleSOAR (soar_type) {
        let data = {
          sql:this.checkData.sql,
          soar_type:soar_type
        }
        GetSqlSOAR(this.database, data)
        .then(
          response => {
            this.query_result = response.data.results
            if (soar_type == 'only_syntax' && this.query_result.length == 0) {
              this.query_result = 'SQL语法检测通过'
            }
          }          
        )
      }

    },

  }
</script>
