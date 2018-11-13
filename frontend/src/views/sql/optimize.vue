<style scoped>
    .parm_check_element {
      width: 200px;
      margin-left: 20px;
    }
</style>

<template>
  <div>
    <Card>
      <Row>            
        <Col span="12">
            <div>
              <Alert show-icon>查询表结构</Alert>
                <Row>  
                  <Col span="10">
                    <Cascader :data="targetDbs" trigger="hover" @on-change="handleGetTables"></Cascader>
                  </Col>
                  <Col span="10">
                    <Select v-model="table" @on-change="handleGetTableInfo" placeholder="选择表" filterable class="parm_check_element">
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
                <FormItem label="SQL" prop="sql">
                  <editor v-model="checkData.sql" @init="editorInit" @setCompletions="setCompletions"></editor>
                </FormItem>
                <FormItem label="操作">
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
                </FormItem>
              </Form>
            </div>
        </Col>

        <Col span="12">
            <Alert show-icon style='margin-left:12%'>
              <Icon type="ios-lightbulb-outline" slot="icon"></Icon>
                查询结果
            </Alert>
            <div style='margin-left:50px'>
              <pre>
                <editor v-model="query_result" @init="editorInit" @setCompletions="setCompletions"></editor>
              </pre>
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
  import {GetTableList, GetTableInfo, GetSqlAdvisor} from '@/api/sql/sqlquery'
  import editor from '../my-components/sql/editor'
  import copyright from '../my-components/public/copyright'

  export default {
    components: {editor, copyright},
    data () {
      return {
        spinShow: false,
        targetDbs:[],
        wordList:[],
        dbList:[],
        tableList:[],
        table:'',
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
        .catch(error => {
          console.log(error)
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
        if (e!=''){
          this.spinShow = true
          GetTableInfo(this.database, e)
          .then(
            response => {
              console.log(response)
              this.spinShow = false
              this.query_result = response.data.results
            }
          )
        }
      },

      handleCheckSql () {
        GetSqlAdvisor(this.database, this.checkData.sql)
          .then(
            response => {
              console.log(response)
              this.spinShow = false
              this.query_result = response.data.results
            }
          )
      },

    },

  }
</script>
